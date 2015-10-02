from stubo.testing import Base


class TestHome(Base):
    def test_page_exists(self):
        self.http_client.fetch(self.get_url('/'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers["Content-Type"],
                         'text/html; charset=UTF-8')
        self.assertIn(self.app.settings.get('stubo_version'), response.body)


class TestTracker(Base):
    def get_url(self, path, host=None):
        host = host or 'localhost'
        """Returns an absolute url for the given path on the test server."""
        return '%s://%s:%s%s' % (self.get_protocol(), host,
                                 self.get_http_port(), path)

    def test_page_exists(self):
        self.http_client.fetch(self.get_url('/tracker'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers["Content-Type"],
                         'text/html; charset=UTF-8')
        self.assertIn(self.app.settings.get('stubo_version'), response.body)


class TestAnalytics(Base):
    def test_page_exists(self):
        self.http_client.fetch(self.get_url('/analytics'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers["Content-Type"],
                         'text/html; charset=UTF-8')
