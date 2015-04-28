import unittest
import mock
from stubo.testing import make_stub, make_cache_stub, DummyModel, DummyQueue

class Test_body_contains_matching(unittest.TestCase):
    
    '''A stub can consists of a list of matchers and a response that goes with them.
       A request will be evaluated against each matcher in each stub. the first
       matching stub wins and has its response returned to the calling program.'''  
    
    def setUp(self):
        self.first_2_session = {       
        "session": "first_2", 
        "scenario": "localhost:first",         
        'status' : 'playback',   
        "system_date": "2013-09-05",          
        'stubs' : [ 
            make_cache_stub(["get my stub"], [1]),
            make_cache_stub(["first matcher - will match",
                   "second matcher - will not match"], [2]),
            make_cache_stub(["this is a lot of xml or text..."], [3]),
            make_cache_stub(["get my stub", "today"], [4]),
            make_cache_stub(["one two three"], [5]),
            make_cache_stub(["one two three"], [6]),
            make_cache_stub(['text    with \r\n line feeds'], [7])
         ]
        }    
    
    def _get_best_match(self, request_text, session, trace=None,
                        system_date=None,
                        url_args=None, 
                        module_system_date=None): 
        from stubo.match import match
        from stubo.utils.track import TrackTrace
        trace = trace or TrackTrace(DummyModel(tracking_level='normal'), 
                                    'matcher')
        from stubo.model.request import StuboRequest
        request = StuboRequest(DummyModel(body=request_text, headers={'Stubo-Request-Method' : 'POST'}))
        url_args = url_args or {}
        from stubo.ext.transformer import StuboDefaultHooks
        return match(request, session, trace, system_date, 
                     url_args,
                     StuboDefaultHooks(),
                     module_system_date=module_system_date)   

    def test_match_simple_request(self):
        request = "get my stub"
        results = self._get_best_match(request, self.first_2_session)
        self.assertTrue(results[0])
        stub = results[2]                                        
        self.assertEquals(stub.response_ids(), [1])
        
    def test_match_simple_request_with_spaces(self):
        request = "get my         stub"
        results = self._get_best_match(request, self.first_2_session)
        self.assertTrue(results[0])
        stub = results[2]                           
        self.assertEquals(stub.response_ids(), [1])     

    def test_not_all_matchers_match(self):
        request = "first matcher - will match"
        results = self._get_best_match(request, self.first_2_session)                                       
        self.assertFalse(results[0])

    def test_find_text_anywhere_in_matcher(self):
        request = "this is a lot of xml or text... or even json"
        results = self._get_best_match(request, self.first_2_session)
        self.assertTrue(results[0])
        stub = results[2]                                            
        self.assertEquals(stub.response_ids(), [3])

    def test_match_fail(self):
        request = "it's not me"
        results = self._get_best_match(request, self.first_2_session)                                       
        self.assertFalse(results[0])

    def test_first_of_a_tie_wins(self):
        request = "one two three"
        results = self._get_best_match(request, self.first_2_session)
        self.assertTrue(results[0])
        stub = results[2]                                       
        self.assertEquals(stub.response_ids(), [5])

    def test_ignore_rubble_in_request(self):
        request = "Rubble in front, one two three. Rubble at the end."
        results = self._get_best_match(request, self.first_2_session)
        self.assertTrue(results[0])
        stub = results[2]                                          
        self.assertEquals(stub.response_ids(), [5])

    def test_matcher_with_line_feeds(self):
        request =  'text with \r\n line feeds'
        results = self._get_best_match(request, self.first_2_session)
        self.assertTrue(results[0])
        stub = results[2]                                             
        self.assertEquals(stub.response_ids(), [7])
        
    def test_matcher_with_no_stubs_and_not_playback_session_fails(self):
        from stubo.exceptions import HTTPClientError
        session = {              
            "session": "first_2", 
            "scenario": "localhost:first",         
            'status' : 'dormant', 
            "system_date": "2013-09-05",   
        } 
        with self.assertRaises(HTTPClientError):
            self._get_best_match("", session)  
        
    def test_matcher_with_no_stubs_and_playback_session_errors(self):
        from stubo.exceptions import HTTPServerError  
        session = {              
            "session": "first_2_playback", 
            "scenario": "localhost:first",         
            'status' : 'playback',   
            "system_date": "2013-09-05", 
        } 
        with self.assertRaises(HTTPServerError): 
            self._get_best_match("", session)           

class TestMatcherWithModule(unittest.TestCase):
    
    def setUp(self):
        self.q = DummyQueue
        self.q_patch = mock.patch('stubo.ext.module.Queue', self.q)
        self.q_patch.start()
        from stubo.ext.module import Module
        Module('localhost').add('dummy', exit_code)      
       
    def tearDown(self): 
        import sys
        test_modules = [x for x in sys.modules.keys() \
                        if x.startswith('localhost_stubotest')]
        for mod in test_modules:
            del sys.modules[mod]
            
        from stubo.ext.module import Module
        Module('localhost').remove('dummy')   
        self.q_patch.stop()         
        
    def test_match_eval_error(self): 
        from stubo.match import match
        from stubo.utils.track import TrackTrace
        trace = TrackTrace(DummyModel(tracking_level='normal'), 'matcher') 
        session = {       
            "session": "first_2", 
            "scenario": "localhost:first",         
            'status' : 'playback',   
            "system_date": "2013-09-05",         
            'stubs' : [   
                {"matchers" : [
                       "{{"],
                       "recorded": "2013-09-05", 
                       "response_id" : 5,
                       "module": {"system_date": "2013-08-07", "version": 1, 
                                  "name": "dummy"},
                }] 
            } 
        from stubo.exceptions import HTTPClientError
        from stubo.model.request import StuboRequest
        request = StuboRequest(DummyModel(body='xxx', headers={}))
        from stubo.ext.transformer import StuboDefaultHooks
        url_args = {}
        try:
            match(request, session, trace, session.get('system_date'), url_args, StuboDefaultHooks(), None)      
        except HTTPClientError, e:
            self.assertTrue(hasattr(e, 'traceback'))
        else:
            assert False    

                      
exit_code = """
from stubo.ext.user_exit import GetResponse, ExitResponse

class Dummy(GetResponse):
    
    def __init__(self, request, context):
        GetResponse.__init__(self, request, context)        
                
    def doResponse(self):  
        return ExitResponse(self.request, self.stub)        
        
def exits(request, context):
    if context['function'] == 'get/response':
        return Dummy(request, context)
"""

class TestStubMatcher(unittest.TestCase):
    
    def _make(self):
        from stubo.match import StubMatcher
        from stubo.utils.track import TrackTrace
        return StubMatcher(TrackTrace(DummyModel(tracking_level='full'), 
                                      'matcher'))
    
    def _make_stubo_request(self, body=None, **kwargs):
        from stubo.model.request import StuboRequest
        from stubo.testing import DummyModel
        request = DummyModel(body=body or u'', headers=dict(**kwargs))
        return StuboRequest(request)
    
    def _make_stub(self, payload, scenario=None):
        from stubo.model.stub import Stub
        return Stub(payload, scenario or 'test')
    
    def test_combo(self):
        matcher = self._make()
        headers = {'Stubo-Request-Method' : 'GET',
                   'Stubo-Request-Path' : '/get/me',
                   'Stubo-Request-Query' : 'foo=bar'}
        request = self._make_stubo_request(**headers)
        payload = dict(request=dict(method='GET', 
                                    urlPath='/get/me', 
                                    queryArgs=dict(foo=['bar'])))
        stub = self._make_stub(payload)
        self.assertTrue(matcher.match(request, stub))
        
    def test_post_combo(self):
        matcher = self._make()
        headers = {'Stubo-Request-Method' : 'POST',
                   'Stubo-Request-Path' : '/get/me',
                   'Stubo-Request-Query' : 'foo=bar'}
        request = self._make_stubo_request(body = u'hello', **headers)
        payload = dict(request=dict(method='POST',
                                    bodyPatterns=dict(contains=[u'hello']), 
                                    urlPath='/get/me', 
                                    queryArgs=dict(foo=['bar'])))
        stub = self._make_stub(payload)
        self.assertTrue(matcher.match(request, stub))
        
    def test_headers(self):
        matcher = self._make()
        headers = {'Stubo-Request-Headers' : '''{
                      "Content-Type" : "text/xml",
                      "X-Custom-Header" : "1234"
                    }'''}
        request = self._make_stubo_request(body = u'hello', **headers)
        payload = dict(request=dict(method='POST',
                                    headers=str({"Content-Type" : "text/xml"})))
        stub = self._make_stub(payload)
        self.assertTrue(matcher.match(request, stub)) 
        
    def test_not_headers(self):
        matcher = self._make()
        headers = {'Stubo-Request-Headers' : '''{
                      "Content-Type" : "text/xml",
                      "X-Custom-Header" : "1234"
                    }'''}

        request = self._make_stubo_request(**headers)
        payload = dict(request={ '!headers' : str({"Content-Type" : "text/xml"})}) 
        stub = self._make_stub(payload)
        self.assertFalse(matcher.match(request, stub))
        self.assertEqual(matcher.trace.trace[0][1],
         ('warn', "not a request with headers: {'Content-Type': 'text/xml'} was StuboRequest: uri=None, host=None, method=POST, path=None, query=, id="+"{0}".format(request.id()), None))
                     
    def test_combo_method_fails(self):
        matcher = self._make()
        headers = {'Stubo-Request-Method' : 'POST',
                   'Stubo-Request-Path' : '/get/me',
                   'Stubo-Request-Query' : 'foo=bar'}
        request = self._make_stubo_request(**headers)
        payload = dict(request=dict(method='GET', 
                                    urlPath='/get/me', 
                                    queryArgs=dict(foo=['bar'])))
        stub = self._make_stub(payload)
        self.assertFalse(matcher.match(request, stub))  
        self.assertEqual(len(matcher.trace.trace), 1)
        self.assertEqual(matcher.trace.trace[0][1], 
          ('warn', 'a request with method: GET was StuboRequest: uri=None, host=None, method=POST, path=/get/me, query=foo=bar, id={0}'.format(request.id()), None)) 
        
    def test_combo_path_fails(self):
        matcher = self._make()
        headers = {'Stubo-Request-Method' : 'GET',
                   'Stubo-Request-Path' : '/get/me/out',
                   'Stubo-Request-Query' : 'foo=bar'}
        request = self._make_stubo_request(**headers)
        payload = dict(request=dict(method='GET', 
                                    urlPath='/get/me', 
                                    queryArgs=dict(foo=['bar'])))
        stub = self._make_stub(payload)
        self.assertFalse(matcher.match(request, stub))  
        self.assertEqual(matcher.trace.trace[0][1], 
          ('warn', 'a request with path: /get/me was StuboRequest: uri=None, host=None, method=GET, path=/get/me/out, query=foo=bar, id={0}'.format(request.id()), None))   
    
    def test_urlpattern(self):
        matcher = self._make()
        headers = {'Stubo-Request-Method' : 'GET',
                   'Stubo-Request-Path' : '/get/me/1'}

        request = self._make_stubo_request(**headers)
        payload = dict(request=dict(method='GET', 
                                    urlPattern="/get/me/[0-9]+")) 
        stub = self._make_stub(payload)
        self.assertTrue(matcher.match(request, stub))
        
    def test_not_urlpattern(self):
        matcher = self._make()
        headers = {'Stubo-Request-Method' : 'GET',
                   'Stubo-Request-Path' : '/get/me/1'}

        request = self._make_stubo_request(**headers)
        payload = dict(request={'method' : 'GET', 
                                '!urlPattern' : "/get/me/[0-9]+"}) 
        stub = self._make_stub(payload)
        self.assertFalse(matcher.match(request, stub))
        self.assertEqual(matcher.trace.trace[0][1],
          ('warn', "not  urlPattern that matches regex: '/get/me/[0-9]+' was StuboRequest: uri=None, host=None, method=GET, path=/get/me/1, query=, id={0}".format(request.id()), None))     
         
    def test_combo_query_fails(self):
        matcher = self._make()
        headers = {'Stubo-Request-Method' : 'GET',
                   'Stubo-Request-Path' : '/get/me/out',
                   'Stubo-Request-Query' : 'foo=x'}
        request = self._make_stubo_request(**headers)
        payload = dict(request=dict(method='GET', 
                                    urlPath='/get/me', 
                                    queryArgs=dict(foo=['bar'])))
        stub = self._make_stub(payload)
        self.assertFalse(matcher.match(request, stub)) 
        self.assertEqual(matcher.trace.trace[0][1],
          ('warn', 'a request with path: /get/me was StuboRequest: uri=None, host=None, method=GET, path=/get/me/out, query=foo=x, id={0}'.format(request.id()), None))     
        
    def test_post_combo_path_fails(self):
        matcher = self._make()
        headers = {'Stubo-Request-Method' : 'POST',
                   'Stubo-Request-Path' : '/get/me/out',
                   'Stubo-Request-Query' : 'foo=bar'}
        request = self._make_stubo_request(body = u'hello', **headers)
        payload = dict(request=dict(method='POST',
                                    bodyPatterns=dict(contains=[u'hello']), 
                                    urlPath='/get/me', 
                                    queryArgs=dict(foo=['bar'])))
        stub = self._make_stub(payload)
        self.assertFalse(matcher.match(request, stub))    
        
    def test_combo_negate_path(self):
        matcher = self._make()
        headers = {'Stubo-Request-Method' : 'GET',
                   'Stubo-Request-Path' : '/get/me',
                   'Stubo-Request-Query' : 'foo=bar'}
        request = self._make_stubo_request(**headers)
        payload = {
            'request' : {
               'method' : 'GET', 
               '!urlPath' : '/get/me', 
               'queryArgs' : dict(foo=['bar'])
               }
        }     
        stub = self._make_stub(payload)
        self.assertFalse(matcher.match(request, stub)) 
        self.assertEqual(matcher.trace.trace[0][1],
         ('warn', 'not a request with path: /get/me was StuboRequest: uri=None, host=None, method=GET, path=/get/me, query=foo=bar, id={0}'.format(request.id()), None))  
        
    def test_combo_negate_method(self):
        matcher = self._make()
        headers = {'Stubo-Request-Method' : 'GET',
                   'Stubo-Request-Path' : '/get/me',
                   'Stubo-Request-Query' : 'foo=bar'}
        request = self._make_stubo_request(**headers)
        payload = {
            'request' : {
               '!method' : 'GET', 
               'urlPath' : '/get/me', 
               'queryArgs' : dict(foo=['bar'])
               }
        }     
        stub = self._make_stub(payload)
        self.assertFalse(matcher.match(request, stub)) 
        self.assertEqual(matcher.trace.trace[0][1],
          ('warn', 'not a request with method: GET was StuboRequest: uri=None, host=None, method=GET, path=/get/me, query=foo=bar, id={0}'.format(request.id()), None))
        
    def test_combo_negate_query(self):
        matcher = self._make()
        headers = {'Stubo-Request-Method' : 'GET',
                   'Stubo-Request-Path' : '/get/me',
                   'Stubo-Request-Query' : 'foo=bar'}
        request = self._make_stubo_request(**headers)
        payload = {
            'request' : {
               'method' : 'GET', 
               'urlPath' : '/get/me', 
               '!queryArgs' : dict(foo=['bar'])
               }
        }     
        stub = self._make_stub(payload)
        self.assertFalse(matcher.match(request, stub)) 
        self.assertEqual(matcher.trace.trace[0][1],
          ('warn', "not a request with query: {'foo': ['bar']} was StuboRequest: uri=None, host=None, method=GET, path=/get/me, query=foo=bar, id="+request.id(), None))                
        
    def test_combo_negate_body_contains(self):
        matcher = self._make()
        headers = {'Stubo-Request-Method' : 'POST',
                   'Stubo-Request-Path' : '/get/me',
                   'Stubo-Request-Query' : 'foo=bar'}
        request = self._make_stubo_request(body=u'hello', **headers)
        payload = {
            'request' : {
               'method' : 'POST', 
               'urlPath' : '/get/me', 
               'queryArgs' : dict(foo=['bar']),
               'bodyPatterns' : {
                    '!contains' : [u'hello']
               }     
               }
        }     
        stub = self._make_stub(payload)
        self.assertFalse(matcher.match(request, stub)) 
        self.assertEqual(matcher.trace.trace[0][1],
                    ('warn', 'not a request with body_unicode: hello was StuboRequest: uri=None, host=None, method=POST, path=/get/me, query=foo=bar, id={0}'.format(request.id()), None)) 
        
    def test_combo_body_contains(self):
        matcher = self._make()
        headers = {'Stubo-Request-Method' : 'POST',
                   'Stubo-Request-Path' : '/get/me',
                   'Stubo-Request-Query' : 'foo=bar'}
        request = self._make_stubo_request(body=u'hello', **headers)
        payload = {
            'request' : {
               'method' : 'POST', 
               'urlPath' : '/get/me', 
               'queryArgs' : dict(foo=['bar']),
               'bodyPatterns' : {
                    '!contains' : [u'foo'],
                    'contains' : [u'hello']
               }     
               }
        }     
        stub = self._make_stub(payload)
        self.assertTrue(matcher.match(request, stub)) 
        
    def test_body_contains_xpath(self):
        matcher = self._make()
        headers = {'Stubo-Request-Method' : 'POST'}
        request = self._make_stubo_request(body=u'<x><y>hello</y></x>', **headers)
        payload = {
            'request' : {
               'method' : 'POST', 
               'bodyPatterns' : {
                    'xpath' : ['/x/y']
               }     
               }
        }     
        stub = self._make_stub(payload)
        self.assertTrue(matcher.match(request, stub)) 
        
    def test_body_contains_not_xpath(self):
        matcher = self._make()
        headers = {'Stubo-Request-Method' : 'POST'}
        request = self._make_stubo_request(body=u'<x><y>hello</y></x>', **headers)
        payload = {
            'request' : {
               'method' : 'POST', 
               'bodyPatterns' : {
                    '!xpath' : ['/y']
               }     
               }
        }     
        stub = self._make_stub(payload)
        self.assertTrue(matcher.match(request, stub))
        
    def test_body_contains_not_xpath2(self):
        matcher = self._make()
        headers = {'Stubo-Request-Method' : 'POST'}
        request = self._make_stubo_request(body=u'<x><y>hello</y></x>', **headers)
        payload = {
            'request' : {
               'method' : 'POST', 
               'bodyPatterns' : {
                    'xpath' : ['/y']
               }     
               }
        }     
        stub = self._make_stub(payload)
        self.assertFalse(matcher.match(request, stub)) 
        self.assertEqual(matcher.trace.trace[0][1],
                         ('warn', u" body that matches xpath: '/y'  body does not match xpath: '/y'", None))   
        
    def test_body_contains_jsonpath(self):
        matcher = self._make()
        headers = {'Stubo-Request-Method' : 'POST'}
        payload = '{"version": "1", "data": {"status": "a", "message": "ok"}}'
        request = self._make_stubo_request(body=payload, **headers)
        payload = {
            'request' : {
               'method' : 'POST', 
               'bodyPatterns' : {
                    'jsonpath' : ['data.message']
               }     
               }
        }     
        stub = self._make_stub(payload)
        self.assertTrue(matcher.match(request, stub))    
        
    def test_body_contains_not_jsonpath(self):
        matcher = self._make()
        headers = {'Stubo-Request-Method' : 'POST'}
        payload = '{"version": "1", "data": {"status": "a", "message": "ok"}}'
        request = self._make_stubo_request(body=payload, **headers)
        payload = {
            'request' : {
               'method' : 'POST', 
               'bodyPatterns' : {
                    '!jsonpath' : ['data.x']
               }     
               }
        }     
        stub = self._make_stub(payload)
        self.assertTrue(matcher.match(request, stub))
        
    def test_body_combo_contains_jsonpath(self):
        matcher = self._make()
        headers = {'Stubo-Request-Method' : 'POST'}
        payload = '{"version": "1", "data": {"status": "a", "message": "ok"}}'
        request = self._make_stubo_request(body=payload, **headers)
        payload = {
            'request' : {
               'method' : 'POST', 
               'bodyPatterns' : {
                    'jsonpath' : ['data.message'],             
                    '!jsonpath' : ['data.x']
               }     
               }
        }     
        stub = self._make_stub(payload)
        self.assertTrue(matcher.match(request, stub)) 
        
    def test_body_combo_contains_jsonpath2(self):
        matcher = self._make()
        headers = {'Stubo-Request-Method' : 'POST'}
        payload = '{"version": "1", "data": {"status": "a", "message": "ok"}}'
        request = self._make_stubo_request(body=payload, **headers)
        payload = {
            'request' : {
               'method' : 'POST', 
               'bodyPatterns' : {
                    'jsonpath' : ['data.x'],             
                    '!jsonpath' : ['data.x']
               }     
               }
        }     
        stub = self._make_stub(payload)
        self.assertFalse(matcher.match(request, stub)) 
        self.assertEqual(matcher.trace.trace[0][1],
          ('warn', u" body that matches json path: 'data.x'  body does not match json path: 'data.x'", None))                                                                  