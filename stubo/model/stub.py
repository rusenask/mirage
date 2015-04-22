"""  
    :copyright: (c) 2015 by OpenCredo.
    :license: GPLv3, see LICENSE for more details.
"""
import logging
import json
from stubo.model.stub_parser import (
    JSONStubParser, LegacyStubParser
)
from stubo.utils import get_unicode_from_request

log = logging.getLogger(__name__)

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
    
    def scenario_name(self):
        return self.scenario_name
    
    def response(self):
        return self.payload['response']
    
    def response_status(self):
        return self.payload['response']['status']
    
    def set_response_body(self, body):
        self.response()['body'] = body 
         
    def response_body(self):
        response = self.response().get('body')
        if response and isinstance(response, basestring):
            response = [response]
        return response    
    
    def delay_policy(self):
        """Return ``policy name`` if ``Stub`` instance or ``policy playload`` 
        cached from delay_policy if  ``StubCache`` instance."""
        return self.response().get('delayPolicy')
             
    def set_delay_policy(self, policy):
         self.response()['delayPolicy'] =  policy   
    
    def priority(self):
        return self.payload.get('priority')
         
    def set_priority(self, priority):
        self.payload['priority'] = priority        
        
    def request(self):
        return self.payload['request']
    
    def request_method(self):
        return self.payload['request']['method']
        
    def contains_matchers(self):
        return self.payload['request']['bodyPatterns'][0]['contains']
    
    def set_contains_matchers(self, matchers):
        self.request()['bodyPatterns'][0]['contains'] = matchers
        
    def number_of_matchers(self):
        return len(self.contains_matchers())
    
    def args(self):
        return self.payload.get('args', {})    
    
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
                             bodyPatterns=[dict(contains=requests)]),
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
                "bodyPatterns": [
                    { "contains": ["<status>OK</status>"] }
                ]
                },
            "response": {
                "status": 200,
                "body": "<response>YES</response>"
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
    
    def load_from_cache(self, response_ids, delay_policy_name, recorded, 
                        system_date, module_info, request_index_key):                        
        self.payload = dict(response=dict(status=200, ids=response_ids))
        self.set_response_body(self.get_response_body_from_cache(
                                                        request_index_key))
        self.set_recorded(recorded)
        if module_info:
            self.set_module(module_info)                    
        if delay_policy_name:
            self.load_delay_from_cache(delay_policy_name)     
         
    def get_response_body_from_cache(self, request_index_key):
        # look up response
        return self.cache.get_response_text(self.scenario_name, 
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
              