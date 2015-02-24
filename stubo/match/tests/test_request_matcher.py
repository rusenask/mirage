#-*- coding: utf-8 -*-
import unittest
from hamcrest import *
from stubo.match.request_matcher import has_method, body_contains

class Base(unittest.TestCase):
    
    def get_stubo_request(self, body, **kwargs):
        from stubo.model.request import StuboRequest
        from stubo.testing import DummyModel
        request = DummyModel(body=body, headers=dict(**kwargs))
        return StuboRequest(request)
        
class TestHasMethod(Base):
    
    def test_has_method_match(self):
        headers = {'Stubo-Request-Method' : 'POST'}
        assert_that(self.get_stubo_request(body='', **headers), 
                    has_method('POST'))
        
    def test_has_method_failure(self):
        headers = {'Stubo-Request-Method' : 'POST'}
        assert_that(self.get_stubo_request(body='', **headers), 
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
        
     
      