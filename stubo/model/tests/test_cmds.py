import mock
import unittest

from stubo.testing import DummyModel, DummyRequestHandler  

class TestExecCmds(unittest.TestCase):
    
    def setUp(self):
        self.requests = DummyRequests()
        self.db_patch = mock.patch('stubo.model.cmds.requests', self.requests)
        self.db_patch.start()

    def tearDown(self):
        self.db_patch.stop()   
        
    def make_one(self, handler, cmd_file_url=None):
        from stubo.model.cmds import StuboCommandFile
        return StuboCommandFile(handler.request, cmd_file_url)     
    
    def test_ctor(self):
        cmds = self.make_one(DummyRequestHandler(), "/a/b/c")
        self.assertEqual(cmds.location.get_base_url(), 'http://localhost:8001')
        self.assertEqual(cmds.cmd_file_url, '/a/b/c')
        
    def test_ctor_no_arg(self):
        cmds = self.make_one(DummyRequestHandler())
        self.assertEqual(cmds.location.get_base_url(), 'http://localhost:8001')
        self.assertEqual(cmds.cmd_file_url, '')    
            
    def test_rtz_exit_full(self):
        cmds = self.make_one(DummyRequestHandler(), 'rtz_exit_full')
        cmds.run()   
        self.assertTrue(len(self.requests.posts)==6)
        
    def test_cmdfile_with_spaces(self):
        cmds = self.make_one(DummyRequestHandler(), 'cmd_file_with_spaces')
        cmds.run()
        self.assertTrue(len(self.requests.posts)==4)
               
    def test_file_not_provided(self):  
        from stubo.exceptions import HTTPServerError   
        cmds = self.make_one(DummyRequestHandler())  
        with self.assertRaises(HTTPServerError):
            cmds.run()   
            
    def test_file_not_found(self):  
        from stubo.exceptions import HTTPClientError   
        cmds = self.make_one(DummyRequestHandler(), 'bogus')  
        with self.assertRaises(HTTPClientError):
            cmds.run() 
            
    def test_missing_session_param(self):
        from stubo.exceptions import HTTPClientError
        from urlparse import urlparse   
        cmds = self.make_one(DummyRequestHandler())  
        with self.assertRaises(HTTPClientError):
            cmds.run_command(urlparse('put/stub')) 
            
    def test_put_stub_with_url_param(self):
        cmds = self.make_one(DummyRequestHandler(), 'cmd_file1')
        cmds.run()  
        self.assertTrue(len(self.requests.posts)==4)
            
    def test_put_stub_with_text_param(self):
        cmds = self.make_one(DummyRequestHandler(), 'cmd_file2')
        response = cmds.run()  
        self.assertTrue(len(self.requests.posts)==4)
            
    def test_put_stub_with_response_urlparam(self):
        cmds = self.make_one(DummyRequestHandler(), 'cmd_file3')
        cmds.run()  
        self.assertTrue(len(self.requests.posts)==4)
            
    def test_put_stub_with_response_urltext(self):
        cmds = self.make_one(DummyRequestHandler(), 'cmd_file4')
        cmds.run()  
        self.assertTrue(len(self.requests.posts)==4)
        
    def test_put_stub_empty_response(self):
        from stubo.exceptions import HTTPClientError
        cmds = self.make_one(DummyRequestHandler(), 'cmd_file_empty_response')
        with self.assertRaises(HTTPClientError):
            cmds.run()    
        
    def test_get_response(self):
        cmds = self.make_one(DummyRequestHandler(), 'cmd_file5')
        cmds.run()  
        self.assertTrue(len(self.requests.posts)==5)
        
    def test_get_response_no_session(self):
        from stubo.exceptions import HTTPClientError
        cmds = self.make_one(DummyRequestHandler(), 'cmd_file6')  
        with self.assertRaises(HTTPClientError):
            cmds.run()   
            
    def test_get_response7(self):
        cmds = self.make_one(DummyRequestHandler(), 'cmd_file7')
        cmds.run()  
        self.assertTrue(len(self.requests.posts)==5) 
        
    def test_get_response8(self):
        cmds = self.make_one(DummyRequestHandler(), 'cmd_file8')
        cmds.run()  
        self.assertTrue(len(self.requests.posts)==5)   
    
    def test_get_response9(self):
        cmds = self.make_one(DummyRequestHandler(), 'cmd_file9')
        cmds.run()  
        self.assertTrue(len(self.requests.posts)==5)                    

class TestUriLocation(unittest.TestCase):
    
    def _make(self, protocol='http', host='localhost:8001'):
        from stubo.model.cmds import UriLocation
        return UriLocation(DummyModel(protocol=protocol, host=host))
    
    def test_make_one(self):
        loc = self._make()
        self.assertEqual('http', loc.request.protocol)
        self.assertEqual('localhost:8001', loc.request.host)
        
    def test_make_another(self):
        loc = self._make(protocol='https', host='www.stubo.com:8001')
        self.assertEqual('https', loc.request.protocol)
        self.assertEqual('www.stubo.com:8001', loc.request.host)
        
    def test_call_internal(self):
        loc = self._make()
        url, base = loc(path='/foo')
        self.assertEqual(url, 'http://localhost:8001/foo')
        self.assertEqual(base, 'foo')
        
    def test_call_external(self):
        loc = self._make(host='www.stubo.com:8000')
        url, base = loc(path='/foo')
        self.assertEqual(url, 'http://www.stubo.com:8000/foo')
        self.assertEqual(base, 'foo')

class TestUrlFetch(unittest.TestCase):
    
    def setUp(self):
        self.requests = DummyRequests()
        self.db_patch = mock.patch('stubo.model.cmds.requests', self.requests)
        self.db_patch.start()

    def tearDown(self):
        self.db_patch.stop()   
    
    def _make(self):
        from stubo.model.cmds import UrlFetch
        return UrlFetch()
    
    def test_raise_on_error_ok(self):
        fetcher = self._make()
        response = DummyModel(status_code=200)
        fetcher.raise_on_error(response, "/some/url")
        
    def test_raise_on_error_file_not_found(self):
        from stubo.exceptions import HTTPClientError
        fetcher = self._make()
        response = DummyModel(status_code=404, reason="file not found")
        with self.assertRaises(HTTPClientError):
            fetcher.raise_on_error(response, "/some/url") 
                   
    def test_raise_on_error_stubo_error(self):
        from stubo.exceptions import HTTPClientError
        fetcher = self._make()
        response = DummyModel(status_code=405, reason="Unknown")
        response.json = lambda : {'error' : 
            {u'message': 'something went wrong', 'code' : 405}}
        with self.assertRaises(HTTPClientError):
            fetcher.raise_on_error(response, "/some/url")     
            
    def test_raise_on_error_unexpected_error(self):
        from stubo.exceptions import HTTPServerError
        fetcher = self._make()
        response = DummyModel(status_code=501, reason="Unknown")
        with self.assertRaises(HTTPServerError):
            fetcher.raise_on_error(response, "/some/url") 
            
    def test_get_content_not_json(self):
        fetcher = self._make()
        body, headers = fetcher.get('/content_not_json_1') 
        self.assertEqual(body, 'hello')  
        
    def test_get_content_not_json2(self):
        fetcher = self._make()
        body, headers = fetcher.get('/content_not_json_2')  
        self.assertEqual(body, 'goodbye')
     
    def test_get_content_not_json3(self):
        fetcher = self._make()
        body, headers = fetcher.get('/content_not_json_3') 
        self.assertEqual(body, b'\x80abc')
        
    def test_no_response_found(self):
        fetcher = self._make()
        response = fetcher.post('get/response/cantfindthis', {}) 
        self.assertEqual(response.status_code, 400)                         

class DummyRequests(object):
    
    def __init__(self):
        self.posts = []
    
    def get(self, url):
        if 'stubo/api/put/delay_policy' in url:
            # special case as this is not implemented as a HTTP GET
            return self.post(url,"")
        import os.path
        url = os.path.basename(url)
        response = DummyModel(headers={})
        if url in globals().keys():  
            response.content = globals()[url]
            response.status_code = 200
            response.headers = {"Content-Type" : 'text/html; charset=UTF-8'}
            if url == 'content_not_json_1':
                response.encoding = 'utf8'
                response.text = response.content
            elif url in ('content_not_json_2', 'content_not_json_3'):
                response.encoding = ""       
            else:
                response.headers["Content-Type"] = 'application/json; charset=UTF-8'
                response.json = lambda: response.content                  
        else:        
            response.status_code = 404
        return response
    
    def post(self, url, data=None, json=None, **kwargs):
        if url == 'get/response/cantfindthis':
            return DummyModel(status_code = 400, content = 'E017')
            
        self.posts.append((url, data or json))
        return DummyModel(status_code = 200, raise_for_status=lambda : 1,
          headers = {"Content-Type" : 'application/json; charset=UTF-8'},
          json = lambda: "") 
    

content_not_json_1 = 'hello' 
content_not_json_2 = 'goodbye'
content_not_json_3 = b'\x80abc'
 
    
rtz_exit_full = """
# blah blah blah

# blah

put/delay_policy?name=rtz_1&delay_type=fixed&milliseconds=700
put/delay_policy?name=rtz_2&delay_type=normalvariate&mean=100&stddev=50

delete/stubs?scenario=BS_ST_LAS_RES_I2
begin/session?scenario=BS_ST_LAS_RES_I2&session=LASV01_RES&mode=record

# blah
put/stub?session=LASV01_RES&delay_policy=rtz_1,matcher_text,response_text
end/session?session=LASV01_RES
"""

cmd_file_with_spaces = """
delete/stubs?scenario=BS_ST_LAS_RES_I2
begin/session?scenario=BS_ST_LAS_RES_I2&session=LASV01_RES&mode=record
put/stub?session=LASV01_RES&delay_policy=rtz_1, matcher_text , response_text
end/session?session=LASV01_RES
"""

cmd_file1 = """
delete/stubs?scenario=BS_ST_LAS_RES_I2
begin/session?scenario=BS_ST_LAS_RES_I2&session=LASV01_RES&mode=record
put/stub?session=LASV01_RES&delay_policy=rtz_1, url=/static/matcher_text,response_text
end/session?session=LASV01_RES
"""
cmd_file2 = """
delete/stubs?scenario=BS_ST_LAS_RES_I2
begin/session?scenario=BS_ST_LAS_RES_I2&session=LASV01_RES&mode=record
put/stub?session=LASV01_RES&delay_policy=rtz_1, text=/static/matcher_text,response_text
end/session?session=LASV01_RES
"""

cmd_file3 = """
delete/stubs?scenario=BS_ST_LAS_RES_I2
begin/session?scenario=BS_ST_LAS_RES_I2&session=LASV01_RES&mode=record
put/stub?session=LASV01_RES&delay_policy=rtz_1, matcher_text,url=response_text
end/session?session=LASV01_RES
"""

cmd_file4 = """
delete/stubs?scenario=BS_ST_LAS_RES_I2
begin/session?scenario=BS_ST_LAS_RES_I2&session=LASV01_RES&mode=record
put/stub?session=LASV01_RES&delay_policy=rtz_1, matcher_text,text=response_text
end/session?session=LASV01_RES
"""

cmd_file5 = """
begin/session?scenario=BS_ST_LAS_RES_I2&session=LASV01_RES&mode=record
put/stub?session=LASV01_RES&delay_policy=rtz_1, matcher_text,response_text
end/session?session=LASV01_RES
begin/session?scenario=BS_ST_LAS_RES_I2&session=LASV01_RES&mode=playback
get/response?session=LASV01_RES, matcher_text
"""

cmd_file6 = """
begin/session?scenario=BS_ST_LAS_RES_I2&session=LASV01_RES&mode=record
put/stub?session=LASV01_RES&delay_policy=rtz_1, matcher_text,response_text
end/session?session=LASV01_RES
begin/session?scenario=BS_ST_LAS_RES_I2&session=LASV01_RES&mode=playback
get/response
"""

cmd_file7 = """
begin/session?scenario=BS_ST_LAS_RES_I2&session=LASV01_RES&mode=record
put/stub?session=LASV01_RES&delay_policy=rtz_1, matcher_text,response_text
end/session?session=LASV01_RES
begin/session?scenario=BS_ST_LAS_RES_I2&session=LASV01_RES&mode=playback
get/response?session=LASV01_RES&tracking_level=full, matcher_text
"""

cmd_file8 = """
begin/session?scenario=BS_ST_LAS_RES_I2&session=LASV01_RES&mode=record
put/stub?session=LASV01_RES&delay_policy=rtz_1, matcher_text,response_text
end/session?session=LASV01_RES
begin/session?scenario=BS_ST_LAS_RES_I2&session=LASV01_RES&mode=playback
get/response?session=LASV01_RES, url=matcher_text
"""

cmd_file9 = """
begin/session?scenario=BS_ST_LAS_RES_I2&session=LASV01_RES&mode=record
put/stub?session=LASV01_RES&delay_policy=rtz_1, matcher_text,response_text
end/session?session=LASV01_RES
begin/session?scenario=BS_ST_LAS_RES_I2&session=LASV01_RES&mode=playback
get/response?session=LASV01_RES, text=matcher_text
"""

cmd_file_empty_response = """
begin/session?scenario=x&session=xy&mode=record
put/stub?session=xy, matcher_text, EMPTY_RESPONSE
end/session?session=xy
""" 

class Empty(object):
    def __len__(self): return 0
    
EMPTY_RESPONSE = Empty()

matcher_text = """
<?xml version="1.0" encoding="UTF-8"?>
<request>
<X>hello</X>
</request>
"""

response_text = """
<?xml version="1.0" encoding="UTF-8"?>
<response>
goodbye
</response>"""


