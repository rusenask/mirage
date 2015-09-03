"""  
    :copyright: (c) 2015 by OpenCredo.
    :license: GPLv3, see LICENSE for more details.
"""
import logging
import json

from stubo.model.stub_parser import (
    JSONStubParser, LegacyStubParser
)
from stubo.utils import compute_hash

log = logging.getLogger(__name__)


def response_hash(response_body, stub):
    return compute_hash(u"".join([response_body, str(stub.response_status())]))


def parse_stub(body, scenario, url_args):
    log.debug(u'parse_stub body={0}'.format(body))
    try:
        body = json.loads(body)
        log.debug('using JSONStubParser')
        parser = JSONStubParser()
    except ValueError:
        # old format
        log.debug('using LegacyStubParser')
        parser = LegacyStubParser()
    return Stub(parser.parse(body, url_args), scenario)


class StubData(object):
    def __init__(self, payload, scenario):
        self.payload = payload
        self.hostname, _, self.scenario_name = scenario.partition(':')

    def __eq__(self, other):
        if type(other) is type(self):
            return self.payload == other.payload
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def scenario_key(self):
        return '{0}:{1}'.format(self.hostname, self.scenario_name)

    def host(self):
        return self.hostname

    def response(self):
        return self.payload['response']

    def response_status(self):
        return self.payload['response']['status']

    def response_headers(self):
        return self.payload['response'].get('headers')

    def set_response_body(self, body):
        self.response()['body'] = body

    def response_body(self):
        # Note can be more than one response for stateful requests
        response = self.response().get('body')
        if isinstance(response, basestring):
            response = [response]
        return response

    def delay_policy(self):
        """Return ``policy name`` if ``Stub`` instance or ``policy playload`` 
        cached from delay_policy if  ``StubCache`` instance."""
        return self.response().get('delayPolicy')

    def set_delay_policy(self, policy):
        self.response()['delayPolicy'] = policy

    def priority(self):
        return self.payload.get('priority')

    def set_priority(self, priority):
        self.payload['priority'] = priority

    def set_args(self, args):
        self.payload['args'] = args

    def request(self):
        return self.payload['request']

    def request_method(self):
        return self.payload['request']['method']

    def request_path(self):
        return self.payload['request'].get('urlPath')

    def request_query_args(self):
        return self.payload['request'].get('queryArgs')

    def contains_matchers(self):
        return self.payload['request'].get('bodyPatterns', {}).get('contains')

    def set_contains_matchers(self, matchers):
        self.request()['bodyPatterns']['contains'] = matchers

    def number_of_matchers(self):
        return len(self.contains_matchers() or [])

    def args(self):
        return self.payload.get('args', {})

    def set_args(self, args):
        self.payload['args'] = args

    def recorded(self):
        return self.payload.get('recorded')

    def set_recorded(self, recorded):
        self.payload['recorded'] = recorded

    def module(self):
        return self.payload.get('module', {})

    def set_module(self, module):
        self.payload['module'] = module

    def space_used(self):
        return len(unicode(self.payload))

    def __unicode__(self):
        return unicode(self.payload)

    def __str__(self):
        return self.__unicode__().encode('utf8')


def create(request_body, response_body, method="POST", status=200):
    requests = request_body if isinstance(request_body, list) else [request_body]
    return dict(request=dict(method=method,
                             bodyPatterns=dict(contains=requests)),
                response=dict(status=status,
                              body=response_body))


class Stub(StubData):
    """ The stub.
    
    A stub consists of request and response definitions which are used to 
    reproduce an HTTP call during testing.
    
     .. code-block:: python
     
         '''An example payload
          
         {
            "request": {
                "method": "POST",
                "bodyPatterns": {
                    "contains": ["<status>OK</status>"] 
                }
                "urlPath": "/get/me",
                "queryArgs": {
                   "find" : "me",
                   "when" : "now"
                },
                "headers": {
                  "User-Agent": "python-requests/2.5.1 CPython/2.7.7 Darwin/13.4.0"
                }
            },
            "response": {
                "status": 200,
                "body": "<response>YES</response>",
                "headers": {}
            }    
        }
    """

    def __init__(self, payload, scenario):
        StubData.__init__(self, payload, scenario)

    def delay_policy_name(self):
        return self.delay_policy()


class StubCache(StubData):
    def __init__(self, payload, scenario, session_name):
        StubData.__init__(self, payload, scenario)
        self.session_name = session_name
        from stubo.cache import Cache

        self.cache = Cache(self.hostname)

    def id(self):
        return '{0} => {1}'.format(self.scenario_key(), self.session_name)

    def request_index_id(self):
        matchers = u"".join([u''.join(
            x.split()).strip() for x in self.contains_matchers() or []])
        return compute_hash(u"".join([self.scenario_name,
                                      matchers,
                                      self.request_path() or "",
                                      self.request_method(),
                                      self.request_query_args() or ""]))

    def load_from_cache(self, response_ids, delay_policy_name, recorded,
                        system_date, module_info, request_index_key):
        self.payload = dict(response=dict(ids=response_ids))
        response = self.get_response_from_cache(request_index_key)
        self.payload['response'] = response
        self.set_recorded(recorded)
        if module_info:
            self.set_module(module_info)
        if delay_policy_name:
            self.load_delay_from_cache(delay_policy_name)

    def get_response_from_cache(self, request_index_key):
        # look up response
        return self.cache.get_response(self.scenario_name,
                                       self.session_name,
                                       self.response_ids(),
                                       request_index_key)

    def load_delay_from_cache(self, name):
        self.set_delay_policy(self.cache.get_delay_policy(name))

    def response_ids(self):
        return self.response()['ids']

    def delay_policy_name(self):
        name = ''
        policy = self.delay_policy()
        if policy:
            name = policy.get('name')
        return name
