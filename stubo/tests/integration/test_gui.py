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


class TestManage(Base):
    def test_page_exists(self):
        self.http_client.fetch(self.get_url('/manage'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers["Content-Type"],
                         'text/html; charset=UTF-8')
        self.assertIn(self.app.settings.get('stubo_version'), response.body)

    def test_view_stubs(self):
        self.http_client.fetch(self.get_url('/stubo/api/exec/cmds?cmdfile=/static/cmds/demo/first.commands'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)

        self.http_client.fetch(self.get_url('/manage'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        self.assertIn("first_1", response.body)

    def test_run_cmd(self):
        self.http_client.fetch(self.get_url('/manage/exec_cmds?cmdfile=/static/cmds/demo/first.commands&html=true'),
                               self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)

        self.http_client.fetch(self.get_url('/manage'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers['Content-Type'], 'text/html; charset=UTF-8')
        self.assertIn("first_1", response.body)

    def test_run_cmds(self):
        self.http_client.fetch(self.get_url('/manage/exec_cmds?html=true&cmds=delete/stubs?scenario=foo'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)

        self.http_client.fetch(self.get_url('/manage'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers['Content-Type'], 'text/html; charset=UTF-8')
        self.assertIn("delete/stubs?scenario=foo", response.body)

    def test_view_delay_policies(self):
        self.http_client.fetch(self.get_url('/stubo/api/put/delay_policy?name=bob&delay_type=fixed&milliseconds=200'),
                               self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)

        self.http_client.fetch(self.get_url('/manage'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        self.assertIn("bob", response.body)

    def test_view_modules(self):
        self.http_client.fetch(self.get_url('/stubo/api/put/module?name=/static/cmds/tests/ext/cache/text/example.py'),
                               self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)

        self.http_client.fetch(self.get_url('/manage'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        self.assertIn("example", response.body)

    def test_end_sessions_action(self):
        self.http_client.fetch(self.get_url('/stubo/api/exec/cmds?cmdfile=/static/cmds/demo/first.commands'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)

        self.http_client.fetch(self.get_url('/manage'), self.stop)
        response = self.wait()
        self.assertTrue('End all active sessions' not in response.body)
        self.assertTrue('End a session' not in response.body)

        self.http_client.fetch(self.get_url('/stubo/api/begin/session?scenario=first&session=playme&mode=playback'),
                               self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)

        self.http_client.fetch(self.get_url('/manage'), self.stop)
        response = self.wait()
        self.assertTrue('End all active sessions' in response.body)

    def test_delay_policy_delete_action(self):
        self.http_client.fetch(self.get_url('/stubo/api/put/delay_policy?name=bob&delay_type=fixed&milliseconds=200'),
                               self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)

        self.http_client.fetch(self.get_url('/manage?action=delete&type=delay_policy&name=bob'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers["Content-Type"],
                         'text/html; charset=UTF-8')
        self.assertTrue("""'data': {'message': "Deleted 1 delay policies from [u'bob']"}""" in response.body)

    def test_module_delete_action(self):
        self.http_client.fetch(self.get_url('/stubo/api/put/module?name=/static/cmds/tests/ext/cache/text/example.py'),
                               self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)

        self.http_client.fetch(self.get_url('/manage?action=delete&type=module&name=example'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        self.assertTrue("{'deleted': ['localhost:example']" in response.body)

    def test_action_arg_error(self):
        self.http_client.fetch(self.get_url('/manage?action=delete&type=module&namexxx=example'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        self.assertTrue("""<div class="alert alert-danger fade in">
<button type="button" class="close" data-dismiss="alert">&times;</button>
<h4>Error: HTTP 400: Bad Request (Missing argument name)</h4>
</div>""" in response.body)


class TestAnalytics(Base):
    def test_page_exists(self):
        self.http_client.fetch(self.get_url('/analytics'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers["Content-Type"],
                         'text/html; charset=UTF-8')
