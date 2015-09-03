import unittest


class TestHTTPClientError(unittest.TestCase):
    def _makeOne(self, **kwargs):
        from stubo.exceptions import HTTPClientError

        return HTTPClientError(**kwargs)

    def test_empty_ctor(self):
        e = self._makeOne()
        self.assertEqual(e.code, 400)
        self.assertTrue(hasattr(e, 'title'))
        self.assertTrue(hasattr(e, 'explanation'))

    def test_title(self):
        e = self._makeOne(title='help!')
        self.assertEqual(e.code, 400)
        self.assertEqual(e.title, 'help!')
        self.assertTrue(hasattr(e, 'explanation'))

    def test_code(self):
        e = self._makeOne(code=405)
        self.assertEqual(e.code, 405)
        self.assertTrue(hasattr(e, 'title'))
        self.assertTrue(hasattr(e, 'explanation'))

    def test_str(self):
        e = self._makeOne(code=405)
        self.assertTrue(len(str(e)) != 0)


class TestHTTPServerError(unittest.TestCase):
    def _makeOne(self, **kwargs):
        from stubo.exceptions import HTTPServerError

        return HTTPServerError(**kwargs)

    def test_empty_ctor(self):
        e = self._makeOne()
        self.assertEqual(e.code, 500)
        self.assertTrue(hasattr(e, 'title'))
        self.assertTrue(hasattr(e, 'explanation'))

    def test_title(self):
        e = self._makeOne(title='help!')
        self.assertEqual(e.code, 500)
        self.assertEqual(e.title, 'help!')

    def test_str(self):
        e = self._makeOne(code=500)
        self.assertTrue(len(str(e)) != 0)


class TestExceptionResponse(unittest.TestCase):
    def test_client_error(self):
        from stubo.exceptions import exception_response, HTTPClientError

        e = exception_response(404)
        self.assertTrue(isinstance(e, HTTPClientError))

    def test_client_error_with_title(self):
        from stubo.exceptions import exception_response, HTTPClientError

        e = exception_response(404, title='help!')
        self.assertTrue(isinstance(e, HTTPClientError))
        self.assertEqual(e.title, 'help!')

    def test_server_error(self):
        from stubo.exceptions import exception_response, HTTPServerError

        e = exception_response(500)
        self.assertTrue(isinstance(e, HTTPServerError))

    def test_server_error_with_title_arg(self):
        from stubo.exceptions import exception_response, HTTPServerError

        e = exception_response(500, title='help!')
        self.assertTrue(isinstance(e, HTTPServerError))
        self.assertEqual(e.title, 'help!')

    def test_server_error_with_code_arg(self):
        from stubo.exceptions import exception_response

        self.assertRaises(ValueError, exception_response, 200)
