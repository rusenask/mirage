import unittest


class TestJSONStubParser(unittest.TestCase):
    def _get_stub_parser(self):
        from stubo.model.stub import JSONStubParser

        return JSONStubParser()

    def _parse(self, body, **url_args):
        return self._get_stub_parser().parse(body, url_args)

    def test_ctor(self):
        parser = self._get_stub_parser()
        self.assertTrue(parser)

    def test_normal_stub(self):
        stub = {
            'request':
                {'bodyPatterns': {'contains': ['get my stub', 'and another']},
                 'method': 'POST'},
            'response': {'body': 'a response', 'status': 200},
        }
        self.assertEqual(self._parse(stub, foo='bar'), {
            'request':
                {'bodyPatterns': {
                    'contains': ['get my stub', 'and another']},
                    'method': 'POST'},
            'response': {'body': 'a response', 'status': 200},
            'args': {'foo': 'bar'}
        })

    def test_no_args(self):
        stub = {
            'request':
                {'bodyPatterns': {'contains': ['get my stub', 'and another']},
                 'method': 'POST'},
            'response': {'body': 'a response', 'status': 200},
        }
        self.assertEqual(self._parse(stub), {
            'request':
                {'bodyPatterns': {
                    'contains':
                        ['get my stub', 'and another']},
                    'method': 'POST'},
            'response': {'body': 'a response', 'status': 200},
            'args': {}
        })

    def test_default_response(self):
        stub = {
            'request':
                {'bodyPatterns': {'contains': ['get my stub', 'and another']},
                 'method': 'POST'},
        }
        # Do we really support an empty response body?
        self.assertEqual(self._parse(stub), {
            'request':
                {'bodyPatterns': {'contains': ['get my stub', 'and another']},
                 'method': 'POST'},
            'response': {'body': '', 'status': 200},
            'args': {}
        })

    def test_stub_missing_matcher(self):
        with self.assertRaises(ValueError):
            self._parse({
                'response': {'body': 'a response', 'status': 200},
            })


class TestLegacyStubParser(unittest.TestCase):
    def _get_stub_parser(self):
        from stubo.model.stub import LegacyStubParser

        return LegacyStubParser()

    def _parse(self, body, **url_args):
        return self._get_stub_parser().parse(body, url_args)

    def test_ctor(self):
        parser = self._get_stub_parser()
        self.assertTrue(parser)

    def test_normal_stub(self):
        stub = '||textMatcher||get my stub||textMatcher||and another||response||a response'
        self.assertEqual(self._parse(stub, foo='bar'),
                         {'request':
                             {'bodyPatterns': {
                                 'contains': ['get my stub', 'and another']},
                                 'method': 'POST'},
                             'response': {'body': 'a response', 'status': 200},
                             'args': {'foo': 'bar'}
                         }
                         )

    def test_no_args(self):
        stub = '||textMatcher||get my stub||textMatcher||and another||response||a response'
        self.assertEqual(self._parse(stub), {'request':
                                                 {'bodyPatterns': {'contains': ['get my stub', 'and another']},
                                                  'method': 'POST'},
                                             'response': {'body': 'a response', 'status': 200},
                                             'args': {}
                                             })

    def test_stub_missing_response(self):
        with self.assertRaises(ValueError):
            self._parse('||textMatcher||get my stub||textMatcher||and another')

    def test_stub_missing_response2(self):
        with self.assertRaises(ValueError):
            self._parse('||textMatcher||get my stub||textMatcher||and another||response||')

    def test_stub_missing_matcher(self):
        with self.assertRaises(ValueError):
            self._parse('and another||response||a response')


class TestParse(unittest.TestCase):
    def _func(self, request, scenario, json=True, **url_args):
        from stubo.model.stub import parse_stub

        return parse_stub(request, scenario, url_args)

    def test_json(self):
        import json

        request = json.dumps({
            'request':
                {'bodyPatterns': {'contains': ['get my stub', 'and another']},
                 'method': 'POST'},
            'response': {'body': 'a response', 'status': 200},
        })
        stub = self._func(request, 'foo')
        self.assertEqual(stub.args(), {})
        self.assertEqual(stub.contains_matchers(), [u'get my stub', u'and another'])
        self.assertEquals(stub.request_method(), 'POST')
        self.assertEqual(stub.response_body()[0], 'a response')
        self.assertEqual(stub.response_status(), 200)

    def test_json_args(self):
        import json

        request = json.dumps({
            'request':
                {'bodyPatterns': {'contains': ['get my stub', 'and another']},
                 'method': 'POST'},
            'response': {'body': 'a response', 'status': 200},
        })
        stub = self._func(request, 'foo', boring=False)
        self.assertEqual(stub.args(), {'boring': False})
        self.assertEqual(stub.contains_matchers(), [u'get my stub', u'and another'])
        self.assertEquals(stub.request_method(), 'POST')
        self.assertEqual(stub.response_body()[0], 'a response')
        self.assertEqual(stub.response_status(), 200)

    def test_legacy(self):
        request = '||textMatcher||get my stub||textMatcher||and another||response||a response'
        stub = self._func(request, 'foo')
        self.assertEqual(stub.args(), {})
        self.assertEqual(stub.contains_matchers(), [u'get my stub', u'and another'])
        self.assertEquals(stub.request_method(), 'POST')
        self.assertEqual(stub.response_body()[0], 'a response')
        self.assertEqual(stub.response_status(), 200)

    def test_legacy_args(self):
        request = '||textMatcher||get my stub||textMatcher||and another||response||a response'
        stub = self._func(request, 'foo', boring=False)
        self.assertEqual(stub.args(), {'boring': False})
        self.assertEqual(stub.contains_matchers(), [u'get my stub', u'and another'])
        self.assertEquals(stub.request_method(), 'POST')
        self.assertEqual(stub.response_body()[0], 'a response')
        self.assertEqual(stub.response_status(), 200)
