"""
    stubo.match
    ~~~~~~~~~~~
    
    Matchers
     
    :copyright: (c) 2015 by OpenCredo.
    :license: GPLv3, see LICENSE for more details.
"""
import logging
import copy

from hamcrest.core.string_description import StringDescription
from hamcrest import all_of, is_not

from .request_matcher import (
    body_contains, has_method, has_path, has_query_args, has_url_pattern,
    body_xpath, body_jsonpath, has_headers
)
from stubo.model.stub import StubCache
from stubo.exceptions import exception_response
from stubo.ext.transformer import transform

log = logging.getLogger(__name__)


def build_matchers(stub):
    matchers = []
    for k, v in stub.request().iteritems():
        if k == 'bodyPatterns':
            body_patterns = stub.request()['bodyPatterns']
            for body_pattern, body_pattern_value in body_patterns.iteritems():
                # bodyPatterns is a list
                for s in body_pattern_value:
                    if body_pattern == 'contains':
                        matchers.append(body_contains(s))
                    elif body_pattern == '!contains':
                        matchers.append(is_not(body_contains(s)))
                    elif body_pattern == 'xpath':
                        namespaces = None
                        if isinstance(s, tuple):
                            s, namespaces = s
                        matchers.append(body_xpath(s, namespaces))
                    elif body_pattern == '!xpath':
                        namespaces = None
                        if isinstance(s, tuple):
                            s, namespaces = s
                        matchers.append(is_not(body_xpath(s, namespaces)))
                    elif body_pattern == 'jsonpath':
                        matchers.append(body_jsonpath(s))
                    elif body_pattern == '!jsonpath':
                        matchers.append(is_not(body_jsonpath(s)))

        elif k == 'method':
            matchers.append(has_method(v))
        elif k == 'urlPath':
            matchers.append(has_path(v))
        elif k == 'urlPattern':
            matchers.append(has_url_pattern(v))
        elif k == 'queryArgs':
            matchers.append(has_query_args(v))
        elif k == '!method':
            matchers.append(is_not(has_method(v)))
        elif k == '!urlPath':
            matchers.append(is_not(has_path(v)))
        elif k == '!queryArgs':
            matchers.append(is_not(has_query_args(v)))
        elif k == '!urlPattern':
            matchers.append(is_not(has_url_pattern(v)))
        elif k == 'headers':
            matchers.append(has_headers(v))
        elif k == '!headers':
            matchers.append(is_not(has_headers(v)))
    return matchers


def match(request, session, trace, system_date, url_args, hooks,
          module_system_date=None):
    """Returns the stats of a request match process
    :param request: source stubo request
    :param session: cached session payload associated with this request
    :param module_system_date: optional system date of an external module
    """
    request_text = request.request_body()
    scenario_key = session['scenario']
    session_name = session['session']
    log.debug(u'match: request_text={0}'.format(request_text))
    trace.info('system_date={0}, module_system_date={1}'.format(
        system_date, module_system_date))

    if 'stubs' not in session or not len(session['stubs']):
        if session.get('status') != 'playback':
            raise exception_response(400,
                                     title="session {0} not in playback mode for scenario "
                                           "{1}".format(session_name, scenario_key))
        raise exception_response(500,
                                 title="no stubs found in session {0} for {1}, status={2}".format(
                                     session_name, scenario_key, session.get('status')))

    stub_count = len(session['stubs'])
    trace.info(u'matching against {0} stubs'.format(stub_count))
    for stub_number in range(stub_count):
        trace.info('stub ({0})'.format(stub_number))
        stub = StubCache(session['stubs'][stub_number], scenario_key,
                         session_name)
        source_stub = copy.deepcopy(stub)
        request_copy = copy.deepcopy(request)
        stub, request_copy = transform(stub,
                                       request_copy,
                                       module_system_date=module_system_date,
                                       system_date=system_date,
                                       function='get/response',
                                       cache=session.get('ext_cache'),
                                       hooks=hooks,
                                       stage='matcher',
                                       trace=trace,
                                       url_args=url_args)
        trace.info('finished transformation')
        if source_stub != stub:
            trace.diff('stub ({0}) was transformed'.format(stub_number),
                       source_stub.payload, stub.payload)
            trace.info('stub ({0}) was transformed into'.format(stub_number),
                       stub.payload)
        if request_copy != request:
            trace.diff('request was transformed', request_copy.request_body(),
                       request.request_body())
            trace.info('request was transformed into', request_copy.request_body())

        matcher = StubMatcher(trace)
        if matcher.match(request_copy, stub):
            return True, stub_number, stub

    return (False,)


class StubMatcher(object):
    def __init__(self, trace):
        self.trace = trace

    def match(self, request, stub):
        """Match request with single stub"""
        msg = StringDescription()
        all = all_of(*build_matchers(stub))
        result = all.matches(request, msg)
        if not result:
            log.debug(u'No match found: {0}'.format(msg.out))
            self.trace.warn(msg.out)
        return result
