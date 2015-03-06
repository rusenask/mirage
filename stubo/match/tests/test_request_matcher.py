#-*- coding: utf-8 -*-
import unittest
from hamcrest import *
from stubo.match.request_matcher import (
    has_method, body_contains, has_path, has_query_args
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
    
    def test_has_method_match(self):
        headers = {'Stubo-Request-Method' : 'GET',
                   'Stubo-Request-Path' : '/get/me'}
        assert_that(self.get_stubo_request(**headers), 
                    has_path('/get/me')) 
        
    def test_has_method_match_failure(self):
        headers = {'Stubo-Request-Method' : 'GET',
                   'Stubo-Request-Path' : '/get/me'}
        assert_that(self.get_stubo_request(**headers), 
                    is_not(has_path('/get/me2')))         

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