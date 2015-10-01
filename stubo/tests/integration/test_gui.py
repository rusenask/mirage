from stubo.testing import Base


class TestHome(Base):
    def test_page_exists(self):
        self.http_client.fetch(self.get_url('/'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers["Content-Type"],
                         'text/html; charset=UTF-8')
        self.assertIn(self.app.settings.get('stubo_version'), response.body)


# TODO: Cleanup
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

    # def test_session_filter(self):
    #     self.http_client.fetch(self.get_url('/stubo/api/exec/cmds?cmdfile=/static/cmds/demo/first.commands'), self.stop)
    #     response = self.wait()
    #     self.assertEqual(response.code, 200)
    #
    #     self.http_client.fetch(self.get_url('/stubo/api/exec/cmds?cmdfile=/static/cmds/tests/accept/smart.commands'),
    #                            self.stop)
    #     response = self.wait()
    #     self.assertEqual(response.code, 200)
    #
    #     self.http_client.fetch(self.get_url('/tracker?session_filter=first_1&start_time=&latency=0&function=all'),
    #                            self.stop)
    #     response = self.wait()
    #     self.assertEqual(response.code, 200)
    #     self.assertTrue('first_1' in response.body)
    #     self.assertFalse('smart_1' in response.body)
    #
    # def test_latency_filter(self):
    #     self.http_client.fetch(self.get_url('/stubo/default/execCmds?cmdFile=/static/cmds/demo/first.commands'),
    #                            self.stop)
    #     response = self.wait()
    #     self.assertEqual(response.code, 200)
    #
    #     # filter over 5 secs
    #     self.http_client.fetch(self.get_url('/tracker?session_filter=first_1&start_time=&latency=5000&function=all'),
    #                            self.stop)
    #     response = self.wait()
    #     self.assertEqual(response.code, 200)
    #     self.assertFalse('<br/>first_1</td>' in u''.join(response.body.split()).strip())
    #
    #     # filter over 0ms
    #     self.http_client.fetch(self.get_url('/tracker?session_filter=&start_time=&latency=0&function=all'), self.stop)
    #     response = self.wait()
    #     self.assertEqual(response.code, 200)
    #     self.assertTrue('<br/>first_1</td>' in u''.join(response.body.split()).strip())
    #
    # def test_ignore200_filter(self):
    #     self.http_client.fetch(self.get_url('/stubo/default/execCmds?cmdFile=/static/cmds/demo/no_match.commands'),
    #                            self.stop)
    #     response = self.wait()
    #     self.assertEqual(response.code, 200)
    #
    #     # no filtering
    #     self.http_client.fetch(self.get_url('/tracker?session_filter=&start_time=&latency=0&function=all'), self.stop)
    #     response = self.wait()
    #     self.assertEqual(response.code, 200)
    #     self.assertTrue('>end/session</a>' in response.body)
    #     self.assertTrue('>get/response</a>' in response.body)
    #
    #     # ignore 200 filtering
    #     self.http_client.fetch(
    #         self.get_url('/tracker?session_filter=&start_time=&latency=0&function=all&show_only_errors=true'),
    #         self.stop)
    #     response = self.wait()
    #     self.assertEqual(response.code, 200)
    #     self.assertFalse('>end/session</a>' in response.body)
    #     self.assertTrue('>get/response</a>' in response.body)
    #
    # def test_allhosts_filter(self):
    #     # create two versions of first.commands from different hosts
    #     self.http_client.fetch(
    #         self.get_url('/stubo/default/execCmds?cmdFile=/static/cmds/demo/first.commands',
    #                      host='localhost'), callback=self.stop)
    #     response = self.wait()
    #     self.assertEqual(response.code, 200)
    #
    #     self.http_client.fetch(self.get_url('/stubo/default/execCmds?cmdFile=/static/cmds/demo/first.commands',
    #                                         host='127.0.0.1'), callback=self.stop)
    #     response = self.wait()
    #     self.assertEqual(response.code, 200)
    #
    #     self.http_client.fetch(
    #         self.get_url('/tracker?session_filter=first_1&start_time=&latency=0&function=get%2Fresponse'), self.stop)
    #     response = self.wait()
    #     self.assertEqual(response.code, 200)
    #     # should find one get/response
    #     self.assertTrue(response.body.count('>get/response</a>') == 1)
    #
    #     # all_hosts = true
    #     self.http_client.fetch(self.get_url(
    #         '/tracker?session_filter=first_1&start_time=&latency=0&function=get%2Fresponse&all_hosts=true&'), self.stop)
    #     response = self.wait()
    #     # should find two get/response calls
    #     self.assertTrue(response.body.count('>get/response</a>') == 2)
    #
    # def test_function_filter(self):
    #     self.http_client.fetch(self.get_url('/stubo/default/execCmds?cmdFile=/static/cmds/demo/first.commands'),
    #                            self.stop)
    #     response = self.wait()
    #     self.assertEqual(response.code, 200)
    #
    #     # show all functions
    #     self.http_client.fetch(self.get_url('/tracker?session_filter=first_1&start_time=&latency=0&function=all'),
    #                            self.stop)
    #     response = self.wait()
    #     self.assertEqual(response.code, 200)
    #     self.assertTrue('>end/session</a>' in response.body)
    #     self.assertTrue('>put/stub</a>' in response.body)
    #
    #     # filter for put/stub
    #     self.http_client.fetch(self.get_url('/tracker?session_filter=&start_time=&latency=0&function=put/stub'),
    #                            self.stop)
    #     response = self.wait()
    #     self.assertEqual(response.code, 200)
    #     self.assertFalse('>end/session</a>' in response.body)
    #     self.assertTrue('>put/stub</a>' in response.body)
    #
    # def test_handles_xml_in_stubo_response(self):
    #     # start record mode
    #     self.http_client.fetch(self.get_url('/stubo/api/begin/session?scenario=first&session=first_1&mode=record'),
    #                            self.stop)
    #     response = self.wait()
    #     self.assertEqual(response.code, 200)
    #
    #     # add a stub with xml in response
    #     self.http_client.fetch(self.get_url('/stubo/api/put/stub?session=first_1'), callback=self.stop,
    #                            method="POST", body="||textMatcher||get my stub||response||<tns:stuff")
    #     response = self.wait()
    #     self.assertEqual(response.code, 200)
    #
    #     # end recording
    #     self.http_client.fetch(self.get_url('/stubo/api/end/session?session=first_1'), self.stop)
    #     response = self.wait()
    #     self.assertEqual(response.code, 200)
    #
    #     # start playback
    #     self.http_client.fetch(self.get_url('/stubo/api/begin/session?scenario=first&session=first_1&mode=playback'),
    #                            self.stop)
    #     response = self.wait()
    #     self.assertEqual(response.code, 200)
    #
    #     # get the  response
    #     self.http_client.fetch(self.get_url('/stubo/api/get/response?session=first_1'), callback=self.stop,
    #                            method="POST", body="get my stub")
    #     response = self.wait()
    #     self.assertEqual(response.code, 200)
    #     self.assertEqual(response.body, "<tns:stuff")
    #
    #     # check the tracker page data
    #     self.http_client.fetch(self.get_url('/tracker'), self.stop)
    #     response = self.wait()
    #     self.assertEqual(response.code, 200)
    #     self.assertNotIn("<tns:", response.body)
    #     self.assertIn("&lt;tns:", response.body)

    # def test_displayed_in_start_time_desc(self):
    #     from datetime import datetime, timedelta
    #
    #     t = datetime.now()
    #     first = dict(duration_ms=1,
    #                  return_code=200,
    #                  start_time=t,
    #                  function='begin/session')
    #     second = dict(duration_ms=1,
    #                   return_code=200,
    #                   start_time=t - timedelta(seconds=1),
    #                   function='delete/stubs')
    #     # inserted out of start_time order but sorted by start_time desc
    #     self.db.tracker.insert(first)
    #     self.db.tracker.insert(second)
    #     from stubo.model.db import Tracker
    #
    #     tracker = Tracker(self.db)
    #     tracks = list(tracker.find_tracker_data({}, 0, 5))
    #     self.assertEqual(tracks[0].get('function'), 'begin/session')
    #     self.assertEqual(tracks[1].get('function'), 'delete/stubs')
    #
    #     self.http_client.fetch(self.get_url('/tracker?all_hosts=true'), self.stop)
    #     response = self.wait()
    #     self.assertEqual(response.code, 200)
    #     html = response.body
    #     first_index = html.find('begin/session</a>')
    #     second_index = html.find('delete/stubs</a>')
    #     self.assertTrue(first_index < second_index)


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
