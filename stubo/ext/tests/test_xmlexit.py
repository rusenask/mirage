import unittest
from stubo.ext.xmlutils import XPathValue
from stubo.testing import DummyModel
from stubo.model.request import StuboRequest


class TestXMLManglerPutStub(unittest.TestCase):
    def _make(self, **kwargs):
        from stubo.ext.xmlexit import XMLManglerPutStub

        return XMLManglerPutStub(**kwargs)

    def test_ctor(self):
        from stubo.ext.xmlutils import XMLMangler

        mangler = XMLMangler(elements=dict(a=XPathValue('/path/to/a')))
        request = DummyModel(body='<path><to><a>xyz</a></to></path>',
                             headers={})
        from stubo.model.stub import Stub, create

        stub = Stub(create('<path><to><a>xyz</a></to></path>',
                           '<response>abc</response>'), "foo")
        from stubo.ext.transformer import StuboTemplateProcessor

        context = dict(stub=stub, template_processor=StuboTemplateProcessor())
        putter = self._make(mangler=mangler, request=StuboRequest(request),
                            context=context)
        self.assertEqual(putter.mangler, mangler)

    def test_matcher(self):
        from stubo.ext.xmlutils import XMLMangler

        mangler = XMLMangler(elements=dict(a=XPathValue('/path/to/a')))
        request = DummyModel(body='<path><to><a>xyz</a></to></path>',
                             headers={})
        from stubo.model.stub import Stub, create

        stub = Stub(create('<path><to><a>xyz</a></to></path>',
                           '<response>abc</response>'), "foo")
        from stubo.ext.transformer import StuboTemplateProcessor

        context = dict(stub=stub, template_processor=StuboTemplateProcessor())
        putter = self._make(mangler=mangler, request=StuboRequest(request),
                            context=context)
        response = putter.doMatcher()
        self.assertEqual(response.stub.contains_matchers(),
                         [u'<path><to><a>***</a></to></path>'])

    def test_matcher_strip_ns(self):
        from stubo.ext.xmlutils import XMLMangler

        mangler = XMLMangler(elements=dict(a=XPathValue('/path/to/a')))
        request = DummyModel(body='<path><to><a>xyz</a></to></path>',
                             headers={})
        from stubo.model.stub import Stub, create

        stub = Stub(create('<path xmlns="http://great.com"><to><a>xyz</a></to></path>',
                           '<response>abc</response>'), "foo")
        from stubo.ext.transformer import StuboTemplateProcessor

        context = dict(stub=stub, template_processor=StuboTemplateProcessor())
        putter = self._make(mangler=mangler, request=StuboRequest(request),
                            context=context)
        result = putter.doMatcher()
        self.assertEqual(result.stub.contains_matchers(),
                         [u'<path><to><a>***</a></to></path>'])

    def test_matcher2(self):
        from stubo.ext.xmlutils import XMLMangler

        mangler = XMLMangler(elements=dict(a=XPathValue('/path/to/a',
                                                        extractor=lambda x: x[1:-1])))
        request = DummyModel(body='<path><to><a>xyz</a></to></path>',
                             headers={})
        from stubo.model.stub import Stub, create

        stub = Stub(create('<path><to><a>xyz</a></to></path>',
                           '<response>abc</response>'), "foo")
        from stubo.ext.transformer import StuboTemplateProcessor

        context = dict(stub=stub, template_processor=StuboTemplateProcessor())
        putter = self._make(mangler=mangler, request=StuboRequest(request),
                            context=context)
        response = putter.doMatcher()
        self.assertEqual(response.stub.contains_matchers(),
                         [u'<path><to><a>y</a></to></path>'])


class TestPutStubMangleResponse(unittest.TestCase):
    def _make(self, **kwargs):
        from stubo.ext.xmlexit import PutStubMangleResponse

        return PutStubMangleResponse(**kwargs)

    def test_ctor(self):
        from stubo.ext.xmlutils import XMLMangler

        mangler = XMLMangler(elements=dict(a=XPathValue('/path/to/a')))
        response_mangler = XMLMangler(elements=dict(a=XPathValue('/response', extractor=lambda x: x)),
                                      copy_attrs_on_match=True)

        request = DummyModel(body='<path><to><a>xyz</a></to></path>',
                             headers={})
        from stubo.model.stub import Stub, create

        stub = Stub(create('<path><to><a>xyz</a></to></path>',
                           '<response>abc</response>'), "foo")
        from stubo.ext.transformer import StuboTemplateProcessor

        context = dict(stub=stub, template_processor=StuboTemplateProcessor())
        putter = self._make(response_mangler=response_mangler,
                            mangler=mangler, request=StuboRequest(request),
                            context=context)
        self.assertEqual(putter.mangler, mangler)
        self.assertEqual(putter.response_mangler, response_mangler)

    def test_ctor_fails_if_xpath_has_no_extractor(self):
        from stubo.ext.xmlutils import XMLMangler

        mangler = XMLMangler(elements=dict(a=XPathValue('/path/to/a')))
        response_mangler = XMLMangler(elements=dict(a=XPathValue('/response')),
                                      copy_attrs_on_match=True)

        request = DummyModel(body='<path><to><a>xyz</a></to></path>',
                             headers={})
        from stubo.model.stub import Stub, create

        stub = Stub(create('<path><to><a>xyz</a></to></path>',
                           '<response>abc</response>'), "foo")
        from stubo.ext.transformer import StuboTemplateProcessor

        context = dict(stub=stub, template_processor=StuboTemplateProcessor())
        with self.assertRaises(ValueError):
            self._make(response_mangler=response_mangler,
                       mangler=mangler, request=StuboRequest(request),
                       context=context)

    def test_response(self):
        from stubo.ext.xmlutils import XMLMangler

        mangler = XMLMangler(elements=dict(a=XPathValue('/path/to/a')))
        response_mangler = XMLMangler(elements=dict(a=XPathValue('/response', extractor=lambda x: x.upper())),
                                      copy_attrs_on_match=True)

        request = DummyModel(body='<path><to><a>xyz</a></to></path>',
                             headers={})
        from stubo.model.stub import Stub, create

        stub = Stub(create('<path><to><a>xyz</a></to></path>',
                           '<response>abc</response>'), "foo")
        from stubo.ext.transformer import StuboTemplateProcessor

        context = dict(stub=stub, template_processor=StuboTemplateProcessor())
        putter = self._make(response_mangler=response_mangler,
                            mangler=mangler, request=StuboRequest(request),
                            context=context)
        putter.doMatcher()
        response = putter.doResponse()
        self.assertEqual(response.stub.payload,
                         {'request': {'bodyPatterns': {'contains': [u'<path><to><a>***</a></to></path>']},
                                      'method': 'POST'},
                          'response': {'body': u'<response>ABC</response>', 'status': 200}})

    def test_response_namespace(self):
        from stubo.ext.xmlutils import XMLMangler

        mangler = XMLMangler(elements=dict(a=XPathValue('/path/to/a')))
        response_mangler = XMLMangler(elements=dict(a=XPathValue('//user:response', extractor=lambda x: x.upper())),
                                      copy_attrs_on_match=True,
                                      namespaces=dict(user="http://www.my.com/userschema"))

        request = DummyModel(body='<path><to><a>xyz</a></to></path>',
                             headers={})
        from stubo.model.stub import Stub, create

        stub = Stub(create('<path><to><a>xyz</a></to></path>',
                           '<x xmlns:user="http://www.my.com/userschema"><user:response>abc</user:response></x>'),
                    "foo")
        from stubo.ext.transformer import StuboTemplateProcessor

        context = dict(stub=stub, template_processor=StuboTemplateProcessor())
        putter = self._make(response_mangler=response_mangler,
                            mangler=mangler, request=StuboRequest(request),
                            context=context)
        putter.doMatcher()
        response = putter.doResponse()
        self.assertEqual(response.stub.payload,
                         {'request': {'bodyPatterns': {'contains': [u'<path><to><a>***</a></to></path>']},
                                      'method': 'POST'},
                          'response': {
                          'body': u'<x xmlns:user="http://www.my.com/userschema">'
                                  u'<user:response>ABC</user:response></x>',
                          'status': 200}})


class TestXMLManglerGetResponse(unittest.TestCase):
    def _make(self, **kwargs):
        from stubo.ext.xmlexit import XMLManglerGetResponse

        return XMLManglerGetResponse(**kwargs)

    def test_ctor(self):
        from stubo.ext.xmlutils import XMLMangler

        mangler = XMLMangler(elements=dict(a=XPathValue('/path/to/a')))
        request = DummyModel(body='<path><to><a>xyz</a></to></path>',
                             headers={})
        from stubo.model.stub import Stub, create

        stub = Stub(create('<path><to><a>xyz</a></to></path>',
                           '<response>abc</response>'), "foo")
        from stubo.ext.transformer import StuboTemplateProcessor

        context = dict(stub=stub, template_processor=StuboTemplateProcessor())
        getter = self._make(mangler=mangler, request=StuboRequest(request),
                            context=context)
        self.assertEqual(getter.mangler, mangler)

    def test_matcher(self):
        from stubo.ext.xmlutils import XMLMangler

        mangler = XMLMangler(elements=dict(a=XPathValue('/path/to/a')))
        request = DummyModel(body='<path><to><a>xyz</a></to></path>',
                             headers={})
        from stubo.model.stub import Stub, create

        stub = Stub(create('<path><to><a>***</a></to></path>',
                           '<response>abc</response>'), "foo")
        from stubo.ext.transformer import StuboTemplateProcessor

        context = dict(stub=stub, template_processor=StuboTemplateProcessor())
        getter = self._make(mangler=mangler, request=StuboRequest(request),
                            context=context)
        response = getter.doMatcher()
        self.assertEqual(response.stub.contains_matchers(),
                         [u'<path><to><a>xyz</a></to></path>'])

    def test_matcher_with_request_ns(self):
        from stubo.ext.xmlutils import XMLMangler

        mangler = XMLMangler(elements=dict(a=XPathValue('/path/to/a')))
        request = DummyModel(body='<path xmlns="http://great.com"><to><a>xyz</a></to></path>',
                             headers={})
        from stubo.model.stub import Stub, create

        stub = Stub(create('<path><to><a>***</a></to></path>',
                           '<response>abc</response>'), "foo")
        from stubo.ext.transformer import StuboTemplateProcessor

        context = dict(stub=stub, template_processor=StuboTemplateProcessor())
        getter = self._make(mangler=mangler, request=StuboRequest(request),
                            context=context)
        result = getter.doMatcher()
        self.assertEqual(result.stub.contains_matchers(),
                         [u'<path><to><a>xyz</a></to></path>'])

    def test_matcher2(self):
        from stubo.ext.xmlutils import XMLMangler

        mangler = XMLMangler(elements=dict(a=XPathValue('/path/to/a',
                                                        extractor=lambda x: x[1:-1])))
        request = DummyModel(body='<path><to><a>xyz</a></to></path>',
                             headers={})
        from stubo.model.stub import Stub, create

        stub = Stub(create('<path><to><a>y</a></to></path>',
                           '<response>abc</response>'), "foo")
        from stubo.ext.transformer import StuboTemplateProcessor

        context = dict(stub=stub, template_processor=StuboTemplateProcessor())
        getter = self._make(mangler=mangler, request=StuboRequest(request),
                            context=context)
        response = getter.doMatcher()
        self.assertEqual(response.stub.contains_matchers(),
                         [u'<path><to><a>y</a></to></path>'])

    def test_matcher_request(self):
        from stubo.ext.xmlutils import XMLMangler

        mangler = XMLMangler(elements=dict(a=XPathValue('/path/to/a')))
        request = DummyModel(body='<path><to><a>xyz</a></to></path>',
                             headers={})
        from stubo.model.stub import Stub, create

        stub = Stub(create('<path><to><a>***</a></to></path>',
                           '<response>abc</response>'), "foo")
        from stubo.ext.transformer import StuboTemplateProcessor

        context = dict(stub=stub, template_processor=StuboTemplateProcessor())
        getter = self._make(mangler=mangler, request=StuboRequest(request),
                            context=context)
        response = getter.doMatcherRequest()
        self.assertEqual(response.stub.contains_matchers(),
                         [u'<path><to><a>***</a></to></path>'])

        self.assertEqual(response.request.request_body(),
                         '<path><to><a>xyz</a></to></path>')

    def test_matcher_request_with_ns(self):
        from stubo.ext.xmlutils import XMLMangler

        mangler = XMLMangler(elements=dict(a=XPathValue('/path/to/a')))
        request = DummyModel(body='<path xmlns="http://great.com"><to><a>xyz</a></to></path>',
                             headers={})
        from stubo.model.stub import Stub, create

        stub = Stub(create('<path><to><a>***</a></to></path>',
                           '<response>abc</response>'), "foo")
        from stubo.ext.transformer import StuboTemplateProcessor

        context = dict(stub=stub, template_processor=StuboTemplateProcessor())
        getter = self._make(mangler=mangler, request=StuboRequest(request),
                            context=context)
        result = getter.doMatcherRequest()
        self.assertEqual(result.stub.contains_matchers(),
                         [u'<path><to><a>***</a></to></path>'])

        self.assertEqual(result.request.request_body(),
                         '<path><to><a>xyz</a></to></path>')

    def test_matcher_request2(self):
        from stubo.ext.xmlutils import XMLMangler

        mangler = XMLMangler(elements=dict(a=XPathValue('/path/to/a',
                                                        extractor=lambda x: x[1:-1])))
        request = DummyModel(body='<path><to><a>xyz</a></to></path>',
                             headers={})
        from stubo.model.stub import Stub, create

        stub = Stub(create('<path><to><a>***</a></to></path>',
                           '<response>abc</response>'), "foo")
        from stubo.ext.transformer import StuboTemplateProcessor

        context = dict(stub=stub, template_processor=StuboTemplateProcessor())
        getter = self._make(mangler=mangler, request=StuboRequest(request),
                            context=context)
        response = getter.doMatcherRequest()
        self.assertEqual(response.stub.contains_matchers(),
                         [u'<path><to><a>***</a></to></path>'])

        self.assertEqual(response.request.request_body(),
                         '<path><to><a>y</a></to></path>')
