#-*- coding: utf-8 -*-
import unittest
from hamcrest import *
from stubo.match.request_matcher import (
    has_method, body_contains, has_path, has_query_args, has_url_pattern,
    body_xpath, body_jsonpath, has_headers
)

class Base(unittest.TestCase):
    
    def get_stubo_request(self, body=None, **kwargs):
        from stubo.model.request import StuboRequest
        from stubo.testing import DummyModel
        request = DummyModel(body=body or '', headers=dict(**kwargs))
        return StuboRequest(request)
        
class TestHasMethod(Base):
    
    def test_has_method_match(self):
        headers = {'Stubo-Request-Method' : 'POST'}
        assert_that(self.get_stubo_request(**headers), 
                    has_method('POST'))
        
    def test_has_method_match2(self):
        headers = {'Stubo-Request-Method' : 'GET'}
        assert_that(self.get_stubo_request(**headers), 
                    has_method('GET'))    
        
    def test_has_method_failure(self):
        headers = {'Stubo-Request-Method' : 'POST'}
        assert_that(self.get_stubo_request(**headers), 
                    is_not(has_method('GET')))
        
    def test_undefined_default(self):
        headers = {}
        assert_that(self.get_stubo_request(**headers), 
                    has_method('POST'))    
        
class TestBodyContains(Base):
    
    def test_has_body_match(self):
        assert_that(self.get_stubo_request(body='hello my friend'), 
                    body_contains('my friend'))
        
    def test_has_body_match2(self):
        assert_that(self.get_stubo_request(body='hello my friend'), 
                    body_contains('myfriend')) 
        
    def test_has_body_failure(self):
        assert_that(self.get_stubo_request(body='hello my friend'), 
                    is_not(body_contains('enemy')))        
        
class TestPath(Base):
    
    def test_match(self):
        headers = {'Stubo-Request-Method' : 'GET',
                   'Stubo-Request-Path' : '/get/me'}
        assert_that(self.get_stubo_request(**headers), 
                    has_path('/get/me')) 
        
    def test_failure(self):
        headers = {'Stubo-Request-Method' : 'GET',
                   'Stubo-Request-Path' : '/get/me'}
        assert_that(self.get_stubo_request(**headers), 
                    is_not(has_path('/get/me2'))) 
        
    def test_undefined_path(self):
        headers = {'Stubo-Request-Method' : 'GET'}
        assert_that(self.get_stubo_request(**headers), 
                    is_not(has_path('/get/me2')))    
        
class TestXPath(Base):
    
    def test_match(self):
        assert_that(self.get_stubo_request(body='<find><me>hello</me></find>'),
                    body_xpath('/find/me'))
        assert_that(self.get_stubo_request(body='<find><me>hello</me></find>'),
                    body_xpath('//find/me'))
        
    def test_namespace_match(self):
        assert_that(self.get_stubo_request(body='<user:find xmlns:user="http://www.my.com/userschema"><me>hello</me></user:find>'),
                    body_xpath('/user:find/me', {'user' : "http://www.my.com/userschema"}))
        assert_that(self.get_stubo_request(body='<user:find xmlns:user="http://www.my.com/userschema"><me>hello</me></user:find>'),
                    body_xpath('//user:find/me', {'user' : "http://www.my.com/userschema"}))    
              
    def test_failure(self):
        assert_that(self.get_stubo_request(body='<findx><me>hello</me></findx>'),
                    is_not(body_xpath('/find/me')))
        assert_that(self.get_stubo_request(body='<findx><me>hello</me></findx>'),
                    is_not(body_xpath('//find/me')))       

class TestJSONPath(Base):
    
    def test_match(self):
        payload = {
            "version": "1.2.3",
            "data": {
                "status": "playback",
                "message": "Playback mode initiated....",
                "session": "first_1",
                "scenario": "localhost:first"
            }
        }
        import json
        assert_that(self.get_stubo_request(body=json.dumps(payload)),
                    body_jsonpath('data.message'))
        
    def test_failure(self):
        payload = {
            "version": "1.2.3",
            "data": {
                "status": "playback",
                "message": "Playback mode initiated....",
                "session": "first_1",
                "scenario": "localhost:first"
            }
        }
        import json
        assert_that(self.get_stubo_request(body=json.dumps(payload)),
                    is_not(body_jsonpath('data.x')))
        
    def test_non_json(self):
        assert_that(self.get_stubo_request(body="some string"),
                    is_not(body_jsonpath('data.x')))
                      
class TestUrlPattern(Base):
    
    def test_match(self):
        headers = {'Stubo-Request-Method' : 'GET',
                   'Stubo-Request-Path' : '/get/me/3'}
        assert_that(self.get_stubo_request(**headers), 
                    has_url_pattern('/get/me/[0-9]+')) 
        
    def test_failure(self):
        headers = {'Stubo-Request-Method' : 'GET',
                   'Stubo-Request-Path' : '/get/me/a'}
        assert_that(self.get_stubo_request(**headers), 
                    is_not(has_path('/get/me/[0-9]+')))   
        
    def test_undefined(self):
        headers = {}
        assert_that(self.get_stubo_request(**headers), 
                    is_not(has_path('/get/me/[0-9]+')))                      

class TestQueryArgs(Base):
    
    def test_has_query_args(self):
        headers = {
            'Stubo-Request-Method' : 'GET',
            'Stubo-Request-Query' : 'foo=bar'
        }
        assert_that(self.get_stubo_request(**headers), 
                    has_query_args(dict(foo=['bar']))) 
        
    def test_has_query_args(self):
        headers = {
            'Stubo-Request-Method' : 'GET',
            'Stubo-Request-Query' : 'foo=bar&foo=bar2'
        }
        assert_that(self.get_stubo_request(**headers), 
                    has_query_args(dict(foo=['bar', 'bar2'])))  
        
    def test_has_query_args_failure(self):
        headers = {
            'Stubo-Request-Method' : 'GET',
            'Stubo-Request-Query' : 'foo=bar'
        }
        assert_that(self.get_stubo_request(**headers), 
                    is_not(has_query_args(dict(foo=['tar'])))) 
        
    def test_undefined(self):
        headers = {}
        assert_that(self.get_stubo_request(**headers), 
                    is_not(has_query_args(dict(foo=['tar']))))         
        
class TestHeaders(Base):
    
    def test_has_header(self):
        headers = {
            'Stubo-Request-Headers' : '''{
               "Content-Type" : "text/xml",
               "X-Custom-Header" : "1234"
            }'''
        }
        assert_that(self.get_stubo_request(**headers), 
                    has_headers('{"Content-Type" : "text/xml"}'))
        
    def test_not_has_header(self):
        headers = {
            'Stubo-Request-Headers' : '''{
               "Content-Type" : "application/json",
               "X-Custom-Header" : "1234"
            }'''
        }
        assert_that(self.get_stubo_request(**headers), 
                    is_not(has_headers('{"Content-Type" : "text/xml"}')))     
    
    def test_has_all_headers(self):
        headers = {
            'Stubo-Request-Headers' : '''{
               "Content-Type" : "text/xml",
               "X-Custom-Header" : "1234"
            }'''
        }
        assert_that(self.get_stubo_request(**headers), 
                    has_headers('{"Content-Type" : "text/xml", "X-Custom-Header" : "1234"}'))  
        
    def test_has_empty_headers(self):
        headers = {
            'Stubo-Request-Headers' : '{}'
        }
        assert_that(self.get_stubo_request(**headers), 
                    is_not(has_headers('{"Content-Type" : "text/xml"}'))) 
        
    def test_undefined(self):
        headers = {}
        assert_that(self.get_stubo_request(**headers), 
                    is_not(has_headers('{"Content-Type" : "text/xml"}')))           
                            