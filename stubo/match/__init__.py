"""
    stubo.match
    ~~~~~~~~~~~
    
    Matchers
     
    :copyright: (c) 2015 by OpenCredo.
    :license: GPLv3, see LICENSE for more details.
"""
import logging
import datetime
import copy
import json

from hamcrest.core.string_description import StringDescription
from hamcrest import all_of
from .request_matcher import body_contains, has_method
from stubo.model.stub import Stub, StubCache
from stubo.exceptions import exception_response
from stubo.utils import as_date
from stubo.ext.transformer import transform

log = logging.getLogger(__name__)

def build_matchers(stub):
    matchers = []
    for k, v in stub.request().iteritems():
        if k == 'bodyPatterns':
            body_patterns = stub.request()['bodyPatterns']
            for body_pattern in body_patterns:
                if 'contains' in body_pattern:
                    for s in body_pattern['contains']:
                        matchers.append(body_contains(s))
        elif k == 'method':
            matchers.append(has_method(v))                
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
    stats = []
    
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
        if matcher.match(request, stub):
            return (True, stub_number, stub)
     
    return (False,)     
  
class StubMatcher(object):
    
    def __init__(self, trace):
        self.trace = trace
        
    def match(self, request, stub):
        """Match request with single stub"""
        msg =  StringDescription()
        all = all_of(*build_matchers(stub))
        result = all.matches(request, msg)
        if not result:
            self.trace.warn(msg.out)
        return result                        
                                  
                                 
                    
                    
        
        