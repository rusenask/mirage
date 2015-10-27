import mock
import unittest

from stubo.testing import (
    DummyCache, DummyScenario, DummyRequestHandler, DummyTracker, make_stub
)


class TestFunctions(unittest.TestCase):

    def test_get_dbenv(self):
        from stubo.service.api import get_dbenv

        request = DummyRequestHandler()
        request.settings['mongo.host'] = 'mongo'
        request.settings['mongo.port'] = 9999
        env = get_dbenv(request)
        self.assertEqual(env['host'], 'mongo')
        self.assertEqual(env['port'], 9999)

    def test_get_dbenv_no_settings(self):
        from stubo.service.api import get_dbenv

        request = DummyRequestHandler()
        self.assertEqual(get_dbenv(request), None)


class TestCmds(unittest.TestCase):
    def setUp(self):
        self.patch = mock.patch('stubo.service.api.TextCommandsImporter',
                                DummyStuboCommandFile)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()

    def test_empty_cmds(self):
        from stubo.service.api import run_commands

        response = run_commands(DummyRequestHandler(), '')
        self.assertEqual(response['data'], {
            'executed_commands': {'commands': []},
            'number_of_requests': 0,
            'number_of_errors': 0})

    def test_unsupported_cmds(self):
        from stubo.service.api import run_commands
        from stubo.exceptions import HTTPClientError

        with self.assertRaises(HTTPClientError):
            run_commands(DummyRequestHandler(), 'get/response')

    def test_1cmd(self):
        from stubo.service.api import run_commands

        cmds_text = 'delete/stubs?scenario=foo'
        response = run_commands(DummyRequestHandler(), cmds_text)
        self.assertEqual(response['data'], {
            'executed_commands': {'commands': [('delete/stubs?scenario=foo', 200)]},
            'number_of_requests': 1,
            'number_of_errors': 0})

    def test_1cmd_spaces(self):
        from stubo.service.api import run_commands

        cmds_text = ' delete/stubs?scenario=foo '
        response = run_commands(DummyRequestHandler(), cmds_text)
        self.assertEqual(response['data'], {
            'executed_commands': {'commands': [('delete/stubs?scenario=foo', 200)]},
            'number_of_requests': 1,
            'number_of_errors': 0})

    def test_2cmds(self):
        from stubo.service.api import run_commands

        cmds_text = 'delete/stubs?scenario=foo\ndelete/stubs?scenario=bar'
        response = run_commands(DummyRequestHandler(), cmds_text)
        self.assertEqual(response['data'], {
            'executed_commands': {'commands': [('delete/stubs?scenario=foo', 200),
                                               ('delete/stubs?scenario=bar', 200)]},
            'number_of_requests': 2, 'number_of_errors': 0})

    def test_2cmds_spaces(self):
        from stubo.service.api import run_commands

        cmds_text = ' delete/stubs?scenario=foo\n delete/stubs?scenario=bar '
        response = run_commands(DummyRequestHandler(), cmds_text)
        self.assertEqual(response['data'], {
            'executed_commands': {'commands': [('delete/stubs?scenario=foo', 200),
                                               ('delete/stubs?scenario=bar', 200)]},
            'number_of_requests': 2, 'number_of_errors': 0})

    def test_export_cmd(self):
        from stubo.service.api import run_commands

        cmds_text = 'get/export?scenario=foo'
        response = run_commands(DummyRequestHandler(), cmds_text)
        self.assertEqual(response['data'], {
            'export_links': [('get/export?scenario=foo',
                              [('foo.zip', 'http://localhost:8001/static/exports/localhost_foo/foo.zip'),
                               ('foo.tar.gz', 'http://localhost:8001/static/exports/localhost_foo/foo.tar.gz'),
                               ('foo.jar', 'http://localhost:8001/static/exports/localhost_foo/foo.jar')])],
            'executed_commands': {'commands': [('get/export?scenario=foo', 200)]},
            'number_of_requests': 1,
            'number_of_errors': 0})


class TestSession(unittest.TestCase):
    def setUp(self):
        self.cache = DummyCache('localhost')
        self.patch = mock.patch('stubo.service.api.Cache', self.cache)
        self.patch.start()
        self.scenario = DummyScenario()
        self.db_patch = mock.patch('stubo.service.api.Scenario', self.scenario)
        self.db_patch.start()
        self.db_patch2 = mock.patch('stubo.cache.Scenario', self.scenario)
        self.db_patch2.start()

    def tearDown(self):
        self.patch.stop()
        self.db_patch.stop()
        self.db_patch2.stop()

    def make_request(self, **kwargs):
        return DummyRequestHandler(**kwargs)

    def _make_scenario(self, name, **kwargs):
        doc = dict(name=name, **kwargs)
        self.scenario.insert(**doc)

    def test_record_dup_scenario(self):
        from stubo.service.api import begin_session
        from stubo.exceptions import HTTPClientError

        self._make_scenario('localhost:foo')
        session_payload = {
            'status': 'dormant',
            'scenario': 'localhost:foo',
            'session': '1'
        }
        self.cache.set_session('foo', '1', session_payload)
        with self.assertRaises(HTTPClientError):
            begin_session(self.make_request(), 'foo', '1', 'record',
                          system_date=None, warm_cache=False)

    def test_record(self):
        from stubo.service.api import begin_session
        response = begin_session(self.make_request(), 'foo', '1', 'record',
                                 system_date=None, warm_cache=False)
        response['data'].pop('scenario_id')
        self.assertEqual(response['data'], {
            'status': 'record',
            'message': 'Record mode initiated....',
            'session': '1',
            'scenario': 'localhost:foo'
        })

    def test_bad_mode(self):
        from stubo.service.api import begin_session
        from stubo.exceptions import HTTPClientError

        self._make_scenario('localhost:foo')
        with self.assertRaises(HTTPClientError):
            begin_session(self.make_request(), 'foo', '1', 'xxx',
                          system_date=None, warm_cache=False)

    def test_play(self):
        from stubo.service.api import begin_session
        self._make_scenario('localhost:foo')
        from stubo.model.stub import Stub

        doc = dict(scenario='localhost:foo', stub=Stub({
            "request": {
                "method": "POST",
                "bodyPatterns":
                    {"contains": ["<status>OK</status>"]}
            },
            "response": {
                "status": 200,
                "body": "<response>YES</response>"
            }
        }, 'localhost:foo'))

        self.scenario.insert_stub(doc, stateful=True)
        response = begin_session(self.make_request(), 'foo', '1', 'playback',
                                 system_date=None, warm_cache=False)
        self.assertEqual(response['data'], {
            'status': 'playback',
            'message': 'Playback mode initiated....',
            'session': '1',
            'scenario': 'localhost:foo'
        })

    def test_play_no_scenario(self):
        from stubo.service.api import begin_session
        from stubo.exceptions import HTTPClientError

        with self.assertRaises(HTTPClientError):
            begin_session(self.make_request(), 'foo', '1', 'playback',
                          system_date=None, warm_cache=False)

    def test_play_in_record_mode(self):
        from stubo.service.api import begin_session
        from stubo.exceptions import HTTPClientError

        self._make_scenario('localhost:foo')
        session_payload = {
            'status': 'record',
            'scenario': 'localhost:foo',
            'session': '1'
        }
        self.cache.set_session('foo', '1', session_payload)
        with self.assertRaises(HTTPClientError):
            begin_session(self.make_request(), 'foo', '1', 'playback',
                          system_date=None, warm_cache=False)


class TestDeleteStubs(unittest.TestCase):
    def setUp(self):
        self.cache = DummyCache('localhost')
        self.patch = mock.patch('stubo.service.api.Cache', self.cache)
        self.patch.start()
        self.scenario = DummyScenario()
        self.db_patch = mock.patch('stubo.service.api.Scenario', self.scenario)
        self.db_patch.start()
        self.db_patch2 = mock.patch('stubo.cache.Scenario', self.scenario)
        self.db_patch2.start()

    def tearDown(self):
        self.patch.stop()
        self.db_patch.stop()
        self.db_patch2.stop()

    def _make_scenario(self, name, **kwargs):
        doc = dict(name=name, **kwargs)
        self.scenario.insert(**doc)

    def test_scenario_arg(self):
        from stubo.service.api import delete_stubs

        handler = DummyRequestHandler()
        self._make_scenario('localhost:conversation')
        response = delete_stubs(handler, scenario_name='conversation')
        self.assertEqual(response.get('data'), {'scenarios': ['localhost:conversation'], 'message': 'stubs deleted.'})

    def test_active_sessions_playback(self):
        from stubo.service.api import delete_stubs
        from stubo.exceptions import HTTPClientError

        scenario_name = 'conversation'
        handler = DummyRequestHandler()
        self._make_scenario('localhost:conversation')
        session_payload = {
            'status': 'playback',
            'scenario': 'localhost:conversation',
            'session': 'joe'
        }
        self.cache.set_session(scenario_name, 'joe', session_payload)
        with self.assertRaises(HTTPClientError):
            delete_stubs(handler, scenario_name=scenario_name)

    def test_active_sessions_record(self):
        from stubo.service.api import delete_stubs
        from stubo.exceptions import HTTPClientError

        scenario_name = 'conversation'
        handler = DummyRequestHandler()
        self._make_scenario('localhost:conversation')
        session_payload = {
            'status': 'record',
            'scenario': 'localhost:conversation',
            'session': 'joe'
        }
        self.cache.set_session(scenario_name, 'joe', session_payload)
        with self.assertRaises(HTTPClientError):
            delete_stubs(handler, scenario_name=scenario_name)

    def test_with_force(self):
        from stubo.service.api import delete_stubs

        scenario_name = 'conversation'
        handler = DummyRequestHandler()
        self._make_scenario('localhost:conversation')
        session_payload = {
            'status': 'record',
            'scenario': 'localhost:conversation',
            'session': 'joe'
        }
        self.cache.set_session(scenario_name, 'joe', session_payload)
        response = delete_stubs(handler, scenario_name=scenario_name,
                                force=True)
        self.assertEqual(response.get('data'), {'scenarios': ['localhost:conversation'], 'message': 'stubs deleted.'
                                                })
        self.assertEqual(self.cache._hash.values('localhost:conversation'), {})

    def test_delete_one_scenario(self):
        from stubo.service.api import delete_stubs

        handler = DummyRequestHandler()
        self._make_scenario('localhost:conversation')
        self._make_scenario('localhost:conversation2')
        response = delete_stubs(handler, scenario_name='conversation',
                                host='localhost')
        self.assertEqual(response.get('data'),
                         {'scenarios': ['localhost:conversation'], 'message': 'stubs deleted.'})
        result = list(self.scenario.get_all())
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'localhost:conversation2')

    def test_host_arg(self):
        from stubo.service.api import delete_stubs

        self._make_scenario('localhost:conversation')
        self._make_scenario('localhost:conversation2')
        response = delete_stubs(DummyRequestHandler(), host='localhost')
        self.assertEqual(response.get('data').get('message'), 'stubs deleted.')
        self.assertEqual(sorted(response['data'].get('scenarios')),
                         sorted(['localhost:conversation', 'localhost:conversation2']))
        self.assertEqual(list(self.scenario.get_all()), [])

    def test_host_arg2(self):
        from stubo.service.api import delete_stubs

        handler = DummyRequestHandler()
        self._make_scenario('localhost:conversation')
        self._make_scenario('someotherhost:conversation2')
        response = delete_stubs(handler, host='localhost')
        self.assertEqual(response.get('data').get('message'), 'stubs deleted.')
        self.assertEqual(response['data'].get('scenarios'),
                         ['localhost:conversation'])
        result = list(self.scenario.get_all())
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'someotherhost:conversation2')

    def test_host_arg3(self):
        from stubo.service.api import delete_stubs

        handler = DummyRequestHandler()
        self._make_scenario('localhost:conversation')
        self._make_scenario('someotherhost:conversation2')
        response = delete_stubs(handler, host='someotherhost')
        self.assertEqual(response.get('data').get('message'), 'stubs deleted.')
        self.assertEqual(response['data'].get('scenarios'),
                         ['someotherhost:conversation2'])
        result = list(self.scenario.get_all())
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'localhost:conversation')

    def test_host_all_arg(self):
        from stubo.service.api import delete_stubs

        handler = DummyRequestHandler()
        self._make_scenario('localhost:conversation')
        self._make_scenario('someotherhost:conversation2')
        response = delete_stubs(handler, host='all')
        self.assertEqual(response.get('data').get('message'), 'stubs deleted.')
        self.assertEqual(sorted(response['data'].get('scenarios')),
                         sorted(['localhost:conversation',
                                 'someotherhost:conversation2']))
        self.assertEqual(list(self.scenario.get_all()), [])


class TestPutStub(unittest.TestCase):
    def setUp(self):
        self.cache = DummyCache('localhost')
        self.patch = mock.patch('stubo.service.api.Cache', self.cache)
        self.patch.start()
        self.scenario = DummyScenario()
        self.db_patch = mock.patch('stubo.service.api.Scenario', self.scenario)
        self.db_patch.start()
        self.db_patch2 = mock.patch('stubo.cache.Scenario', self.scenario)
        self.db_patch2.start()
        self.tracker = DummyTracker()
        self.tracker_patch = mock.patch('stubo.service.api.Tracker', self.tracker)
        self.tracker_patch.start()

    def tearDown(self):
        self.patch.stop()
        self.db_patch.stop()
        self.db_patch2.stop()
        self.tracker_patch.stop()

    def _make_scenario(self, name, **kwargs):
        doc = dict(name=name, **kwargs)
        self.scenario.insert(**doc)

    def make_request(self, **kwargs):
        return DummyRequestHandler(**kwargs)

    def test_put(self):
        from stubo.service.api import put_stub, begin_session
        from datetime import date

        body = {
            "request": {
                "method": "POST",
                "bodyPatterns":
                    {"contains": ["get my stub"]}
            },
            "response": {
                "status": 200,
                "body": "a response"
            }
        }
        handler = DummyRequestHandler()
        handler.request.headers = {
            'Content-Type': 'application/json; charset=UTF-8'
        }
        import json

        handler.request.body = json.dumps(body)
        begin_session(self.make_request(), 'conversation', 'joe', 'record', system_date=None, warm_cache=False)

        response = put_stub(handler, 'joe', delay_policy=None, stateful=True,
                            priority=1)
        self.assertTrue('error' not in response)
        stubs = self.scenario.get_stubs('localhost:conversation')
        stubs = list(stubs)
        self.assertTrue(len(stubs) == 1)
        from stubo.model.stub import Stub

        stub = Stub(stubs[0]['stub'], 'localhost:conversation')
        self.assertEqual(stub.contains_matchers(), ['get my stub'])
        self.assertEqual(stub.response_body(), ['a response'])
        self.assertEqual(stub.recorded(), str(date.today()))
        self.assertEqual(stub.priority(), 1)

    def test_put_with_module(self):
        from stubo.service.api import put_stub, begin_session
        from datetime import date

        body = {
            "request": {
                "method": "POST",
                "bodyPatterns":
                    {"contains": ["get my stub"]}
            },
            "response": {
                "status": 200,
                "body": "a response"
            }
        }
        module = {
            u'name': u'mangler',
            u'recorded_system_date': u'2014-08-06',
            u'system_date': u'2014-08-06'
        }
        body['module'] = module
        handler = DummyRequestHandler()
        handler.request.headers = {
            'Content-Type': 'application/json; charset=UTF-8'
        }
        import json

        handler.request.body = json.dumps(body)
        begin_session(self.make_request(), 'conversation', 'joe', 'record', system_date=None, warm_cache=False)

        response = put_stub(handler, 'joe', delay_policy=None, stateful=True,
                            priority=2)
        self.assertTrue('error' not in response)
        stubs = list(self.scenario.get_stubs('localhost:conversation'))
        self.assertTrue(len(stubs) == 1)
        from stubo.model.stub import Stub

        stub = Stub(stubs[0]['stub'], 'localhost:conversation')
        self.assertEqual(stub.module(), module)
        self.assertEqual(stub.contains_matchers(), ['get my stub'])
        self.assertEqual(stub.response_body(), ['a response'])
        self.assertEqual(stub.recorded(), str(date.today()))
        self.assertEqual(stub.priority(), 2)

    def test_put_with_delay(self):
        from stubo.service.api import put_stub, begin_session
        from datetime import date

        body = {
            "request": {
                "method": "POST",
                "bodyPatterns":
                    {"contains": ["get my stub"]}
            },
            "response": {
                "status": 200,
                "body": "a response",
                "delayPolicy": "slow"
            }
        }
        handler = DummyRequestHandler()
        handler.request.headers = {'Content-Type': 'application/json'}
        import json

        handler.request.body = json.dumps(body)
        begin_session(self.make_request(), 'conversation', 'joe', 'record',
                      system_date=None, warm_cache=False)
        response = put_stub(handler, 'joe', delay_policy=None, stateful=True,
                            priority=1)
        self.assertTrue('error' not in response)
        stubs = list(self.scenario.get_stubs('localhost:conversation'))
        self.assertTrue(len(stubs) == 1)
        from stubo.model.stub import Stub

        stub = Stub(stubs[0]['stub'], 'localhost:conversation')
        self.assertEqual(stub.contains_matchers(), ['get my stub'])
        self.assertEqual(stub.response_body(), ['a response'])
        self.assertEqual(stub.recorded(), str(date.today()))
        self.assertEqual(stub.delay_policy(), 'slow')
        self.assertEqual(stub.priority(), 1)

    def test_put_with_delay_arg_override(self):
        from stubo.service.api import put_stub, begin_session
        from datetime import date

        body = {
            "request": {
                "method": "POST",
                "bodyPatterns":
                    {"contains": ["get my stub"]}
            },
            "response": {
                "status": 200,
                "body": "a response",
                "delayPolicy": "slow"
            }
        }
        handler = DummyRequestHandler()
        handler.request.headers = {'Content-Type': 'application/json'}
        import json

        handler.request.body = json.dumps(body)
        begin_session(self.make_request(), 'conversation', 'joe', 'record',
                      system_date=None, warm_cache=False)
        response = put_stub(handler, 'joe', delay_policy='fast',
                            stateful=True, priority=1)
        self.assertTrue('error' not in response)
        stubs = list(self.scenario.get_stubs('localhost:conversation'))
        self.assertTrue(len(stubs) == 1)
        from stubo.model.stub import Stub

        stub = Stub(stubs[0]['stub'], 'localhost:conversation')
        self.assertEqual(stub.contains_matchers(), ['get my stub'])
        self.assertEqual(stub.response_body(), ['a response'])
        self.assertEqual(stub.recorded(), str(date.today()))
        self.assertEqual(stub.delay_policy(), 'fast')
        self.assertEqual(stub.priority(), 1)

    def test_put_in_dormant(self):
        from stubo.service.api import put_stub, begin_session, end_session
        from stubo.exceptions import HTTPClientError

        body = {
            "request": {
                "method": "POST",
                "bodyPatterns":
                    {"contains": ["get my stub"]}
            },
            "response": {
                "status": 200,
                "body": "a response",
                "delayPolicy": "slow"
            }
        }
        handler = DummyRequestHandler()
        handler.request.headers = {'Content-Type': 'application/json'}
        import json

        handler.request.body = json.dumps(body)
        begin_session(self.make_request(), 'conversation', 'joe', 'record',
                      system_date=None, warm_cache=False)
        self.tracker.insert(dict(scenario='localhost:conversation',
                                 request_text=handler.request.body,
                                 request_params=dict(scenario='conversation'),
                                 function='put/stub',
                                 stubo_response='<test>OK</test>'))
        end_session(self.make_request(), 'joe')

        with self.assertRaises(HTTPClientError):
            put_stub(handler, 'joe', delay_policy=None, stateful=True,
                     priority=1)

    def test_put_in_playback(self):
        from stubo.service.api import put_stub, begin_session
        from stubo.exceptions import HTTPClientError

        body = {
            "request": {
                "method": "POST",
                "bodyPatterns":
                    {"contains": ["get my stub"]}
            },
            "response": {
                "status": 200,
                "body": "a response",
                "delayPolicy": "slow"
            }
        }
        handler = DummyRequestHandler()
        handler.request.headers = {'Content-Type': 'application/json'}
        import json

        handler.request.body = json.dumps(body)
        self._make_scenario('localhost:conversation')
        from stubo.model.stub import create, Stub

        stub = Stub(create('<test>match this</test>', '<test>OK</test>'),
                    'localhost:conversation')
        doc = dict(scenario='localhost:conversation', stub=stub)
        self.scenario.insert_stub(doc, stateful=True)

        begin_session(self.make_request(), 'conversation', 'joe', 'playback',
                      system_date=None, warm_cache=False)
        with self.assertRaises(HTTPClientError):
            put_stub(handler, 'joe', delay_policy=None, stateful=True,
                     priority=1)

    def test_put_no_session(self):
        from stubo.service.api import put_stub
        from stubo.exceptions import HTTPClientError

        handler = DummyRequestHandler()
        from stubo.model.stub import create

        handler.request.headers = {'Content-Type': 'application/json'}
        import json

        handler.request.body = json.dumps(create(request_body='x',
                                                 response_body='y'))
        with self.assertRaises(HTTPClientError):
            put_stub(handler, 'bogus', delay_policy=None, stateful=True,
                     priority=1)

    def test_put_empty_payload(self):
        from stubo.service.api import put_stub, begin_session
        from stubo.exceptions import HTTPClientError

        body = {}
        handler = DummyRequestHandler()
        handler.request.headers = {'Content-Type': 'application/json'}
        import json

        handler.request.body = json.dumps(body)
        begin_session(self.make_request(), 'conversation', 'joe', 'record',
                      system_date=None, warm_cache=False)
        with self.assertRaises(HTTPClientError):
            put_stub(handler, 'joe', delay_policy=None, stateful=True,
                     priority=1)


class TestPutStubLegacy(unittest.TestCase):
    def setUp(self):
        self.cache = DummyCache('localhost')
        self.patch = mock.patch('stubo.service.api.Cache', self.cache)
        self.patch.start()
        self.scenario = DummyScenario()
        self.db_patch = mock.patch('stubo.service.api.Scenario', self.scenario)
        self.db_patch.start()
        self.db_patch2 = mock.patch('stubo.cache.Scenario', self.scenario)
        self.db_patch2.start()

    def tearDown(self):
        self.patch.stop()
        self.db_patch.stop()
        self.db_patch2.stop()

    def _make_scenario(self, name, **kwargs):
        doc = dict(name=name, **kwargs)
        self.scenario.insert(**doc)

    def make_request(self, **kwargs):
        return DummyRequestHandler(**kwargs)

    def test_put(self):
        from stubo.service.api import put_stub, begin_session
        from datetime import date

        body = '||textMatcher||get my stub||response||a response'
        handler = DummyRequestHandler()
        handler.request.body = body
        begin_session(self.make_request(), 'conversation', 'joe', 'record',
                      system_date=None, warm_cache=False)
        response = put_stub(handler, 'joe', delay_policy=None, stateful=True,
                            priority=1)
        self.assertTrue('error' not in response)
        stubs = list(self.scenario.get_stubs('localhost:conversation'))
        self.assertTrue(len(stubs) == 1)
        from stubo.model.stub import Stub

        stub = Stub(stubs[0]['stub'], 'localhost:conversation')
        self.assertEqual(stub.contains_matchers(), ['get my stub'])
        self.assertEqual(stub.response_body(), ['a response'])
        self.assertEqual(stub.recorded(), str(date.today()))
        self.assertEqual(stub.priority(), 1)

    def test_put_with_delay(self):
        from stubo.service.api import put_stub, begin_session
        from datetime import date

        handler = DummyRequestHandler()
        handler.request.body = '||textMatcher||get my stub||response||a response'
        begin_session(self.make_request(), 'conversation', 'joe', 'record',
                      system_date=None, warm_cache=False)
        put_stub(handler, 'joe', delay_policy='slow', stateful=True, priority=1)
        stubs = list(self.scenario.get_stubs('localhost:conversation'))
        self.assertTrue(len(stubs) == 1)
        from stubo.model.stub import Stub

        stub = Stub(stubs[0]['stub'], 'localhost:conversation')
        self.assertEqual(stub.contains_matchers(), ['get my stub'])
        self.assertEqual(stub.response_body(), ['a response'])
        self.assertEqual(stub.recorded(), str(date.today()))
        self.assertEqual(stub.delay_policy(), 'slow')
        self.assertEqual(stub.priority(), 1)

    def test_put_no_session(self):
        from stubo.service.api import put_stub
        from stubo.exceptions import HTTPClientError

        handler = DummyRequestHandler()
        handler.request.body = '||textMatcher||get my stub||response||a response'
        with self.assertRaises(HTTPClientError):
            put_stub(handler, 'bogus', delay_policy=None, stateful=True,
                     priority=1)

    def test_put_no_text_in_body(self):
        from stubo.service.api import put_stub, begin_session
        from stubo.exceptions import HTTPClientError

        body = ''
        handler = DummyRequestHandler()
        handler.request.body = body
        begin_session(self.make_request(), 'conversation', 'joe', 'record',
                      system_date=None, warm_cache=False)
        with self.assertRaises(HTTPClientError):
            put_stub(handler, 'joe', delay_policy=None, stateful=True,
                     priority=1)

    def test_put_bad_text_in_body(self):
        from stubo.service.api import put_stub, begin_session
        from stubo.exceptions import HTTPClientError

        body = 'textMatcher||get my stub||response||a response'
        handler = DummyRequestHandler()
        handler.request.body = body
        begin_session(self.make_request(), 'conversation', 'joe', 'record',
                      system_date=None, warm_cache=False)
        with self.assertRaises(HTTPClientError):
            put_stub(handler, 'joe', delay_policy=None, stateful=True,
                     priority=1)

    def test_put_bad_text_in_body2(self):
        from stubo.service.api import put_stub, begin_session
        from stubo.exceptions import HTTPClientError

        body = '||textMatcher||get my stub||a response'
        handler = DummyRequestHandler()
        handler.request.body = body
        begin_session(self.make_request(), 'conversation', 'joe', 'record',
                      system_date=None, warm_cache=False)
        with self.assertRaises(HTTPClientError):
            put_stub(handler, 'joe', delay_policy=None, stateful=True,
                     priority=1)


class TestStubCount(unittest.TestCase):
    def setUp(self):
        self.scenario = DummyScenario()
        self.db_patch = mock.patch('stubo.service.api.Scenario', self.scenario)
        self.db_patch.start()

    def tearDown(self):
        self.db_patch.stop()

    def _make_scenario(self, name, **kwargs):
        doc = dict(name=name, **kwargs)
        self.scenario.insert(**doc)

    def test_2stubs(self):
        from stubo.service.api import stub_count

        self._make_scenario('localhost:2stub1matcher')
        from stubo.model.stub import create, Stub

        stub = Stub(create('<test>match this</test>', '<test>OK</test>'),
                    'localhost:2stub1matcher')
        doc = dict(scenario='localhost:2stub1matcher', stub=stub)
        self.scenario.insert_stub(doc, stateful=True)

        from stubo.model.stub import create, Stub

        stub = Stub(create('<test>match this 2</test>', '<test>OK</test>'),
                    'localhost:2stub1matcher')
        doc = dict(scenario='localhost:2stub1matcher', stub=stub)
        self.scenario.insert_stub(doc, stateful=True)

        response = stub_count('localhost', '2stub1matcher')
        self.assertEqual(response['data']['count'], 2)

    def test_no_scenario(self):
        from stubo.service.api import stub_count

        response = stub_count('localhost', 'bogus')
        self.assertEqual(response['data']['count'], 0)

    """ FIXME
    def test_regex_scenario(self): 
        from stubo.service.api import stub_count
        response = stub_count('localhost')
        self.assertEqual(response['data']['count'], 0)"""


class TestStubList(unittest.TestCase):
    def setUp(self):
        self.scenario = DummyScenario()
        self.db_patch = mock.patch('stubo.service.api.Scenario', self.scenario)
        self.db_patch.start()

    def tearDown(self):
        self.db_patch.stop()

    def _make_scenario(self, name, **kwargs):
        doc = dict(name=name, **kwargs)
        self.scenario.insert(**doc)

    def test_1stub_1matcher(self):
        from stubo.service.api import list_stubs

        self._make_scenario('localhost:1stub1matcher')
        from stubo.model.stub import create, Stub

        stub = Stub(create('<test>match this</test>', '<test>OK</test>'),
                    'localhost:1stub1matcher')
        doc = dict(scenario='localhost:1stub1matcher', stub=stub)
        self.scenario.insert_stub(doc, stateful=True)
        response = list_stubs(DummyRequestHandler(), '1stub1matcher')
        self.assertTrue('stubs' in response.get('data'))
        stubs = response['data']['stubs']
        self.assertTrue(len(stubs) == 1)
        from stubo.model.stub import Stub

        stub = Stub(stubs[0], 'localhost:1stub1matcher')
        self.assertEqual(stub.contains_matchers(), ['<test>match this</test>'])
        self.assertEqual(stub.response_body(), ['<test>OK</test>'])

    def test_2stub_1matcher(self):
        from stubo.service.api import list_stubs

        self._make_scenario('localhost:2stub1matcher')
        from stubo.model.stub import create, Stub

        stub = Stub(create('<test>match this</test>', '<test>OK</test>'),
                    'localhost:2stub1matcher')
        doc = dict(scenario='localhost:2stub1matcher', stub=stub)
        self.scenario.insert_stub(doc, stateful=True)

        from stubo.model.stub import create, Stub

        stub2 = Stub(create('<test>match this 2</test>', '<test>OK</test>'),
                     'localhost:2stub1matcher')
        doc2 = dict(scenario='localhost:2stub1matcher', stub=stub2)
        self.scenario.insert_stub(doc2, stateful=True)

        response = list_stubs(DummyRequestHandler(), '2stub1matcher')
        self.assertTrue('stubs' in response.get('data'))
        stubs = response['data']['stubs']
        self.assertTrue(len(stubs) == 2)

        # ming insert not in doc order all the time?
        # from stubo.model.stub import Stub
        # stub = Stub(stubs[0], 'localhost:2stub1matcher')
        # self.assertEqual(stub.contains_matchers(), ['<test>match this</test>'])
        # stub2 = Stub(stubs[1], 'localhost:2stub1matcher')
        # self.assertEqual(stub2.contains_matchers(), ['<test>match this 2</test>'])


class TestGetStubs(unittest.TestCase):
    def setUp(self):
        self.scenario = DummyScenario()
        self.db_patch = mock.patch('stubo.service.api.Scenario', self.scenario)
        self.db_patch.start()

    def tearDown(self):
        self.db_patch.stop()

    def _make_scenario(self, name, **kwargs):
        doc = dict(name=name, **kwargs)
        self.scenario.insert(**doc)

    def test_get_stubs(self):
        from stubo.service.api import get_stubs

        self._make_scenario('localhost:1stub1matcher')
        from stubo.model.stub import create, Stub

        stub = Stub(create('<test>match this</test>', '<test>OK</test>'),
                    'localhost:1stub1matcher')
        doc = dict(scenario='localhost:1stub1matcher', stub=stub)
        self.scenario.insert_stub(doc, stateful=True)
        response = get_stubs('localhost', '1stub1matcher')
        response = list(response)
        self.assertEqual(len(response), 1)
        response = response[0]
        response.pop('_id')
        test_dict = {u'matchers_hash': u'ed9351449fd0d98abd79c2aa2436f392',
                     u'scenario': u'localhost:1stub1matcher',
                     u'space_used': 146,
                     u'stub': {u'request': {u'bodyPatterns': {u'contains': [u'<test>match this</test>']},
                                            u'method': u'POST'},
                               u'response': {u'body': u'<test>OK</test>', u'status': 200}}}
        self.assertEqual(response, test_dict)

    def test_get_stubs_host_arg(self):
        from stubo.service.api import get_stubs

        self._make_scenario('localhost:1stub1matcher')
        from stubo.model.stub import create, Stub

        stub = Stub(create('<test>match this</test>', '<test>OK</test>'),
                    'localhost:1stub1matcher')
        doc = dict(scenario='localhost:1stub1matcher', stub=stub)
        self.scenario.insert_stub(doc, stateful=True)
        response = get_stubs('localhost')
        response = list(response)
        self.assertEqual(len(response), 1)
        response = response[0]
        response.pop('_id')
        test_dict = {u'matchers_hash': u'ed9351449fd0d98abd79c2aa2436f392',
                     u'scenario': u'localhost:1stub1matcher',
                     u'space_used': 146,
                     u'stub': {u'request': {u'bodyPatterns': {u'contains': [u'<test>match this</test>']},
                                            u'method': u'POST'},
                               u'response': {u'body': u'<test>OK</test>', u'status': 200}}}
        self.assertEqual(response, test_dict)


class TestStubExport(unittest.TestCase):
    def setUp(self):
        self.cache = DummyCache('localhost')
        self.patch = mock.patch('stubo.service.api.Cache', self.cache)
        self.patch.start()
        self.scenario = DummyScenario()
        self.db_patch0 = mock.patch('stubo.model.export_commands.Scenario', self.scenario)
        self.db_patch0.start()
        self.db_patch = mock.patch('stubo.model.exporter.Scenario', self.scenario)
        self.db_patch.start()
        self.db_patch2 = mock.patch('stubo.cache.Scenario', self.scenario)
        self.db_patch2.start()
        self.tracker = DummyTracker()
        self.tracker_patch0 = mock.patch('stubo.model.export_commands.Tracker', self.tracker)
        self.tracker_patch0.start()
        self.tracker_patch = mock.patch('stubo.model.exporter.Tracker', self.tracker)
        self.tracker_patch.start()

    def tearDown(self):
        self.patch.stop()
        self.db_patch.stop()
        self.db_patch0.stop()
        self.db_patch2.stop()
        self.tracker_patch0.stop()
        self.tracker_patch.stop()

    def _make_scenario(self, name, **kwargs):
        doc = dict(name=name, **kwargs)
        self.scenario.insert(**doc)

    def _delete_tmp_export_dir(self, scenario_dir):
        import shutil

        shutil.rmtree(scenario_dir)

    def test_runnable_requires_playback_session(self):
        from stubo.service.api import export_stubs
        from stubo.exceptions import HTTPClientError

        request_handler = DummyRequestHandler(session_id=['1'], runnable=['true'])
        self._make_scenario('localhost:1stub1matcher')
        from stubo.model.stub import create, Stub

        stub = Stub(create('<test>match this</test>', '<test>OK</test>'),
                    'localhost:1stub1matcher')
        doc = dict(scenario='localhost:1stub1matcher', stub=stub)
        self.scenario.insert_stub(doc, stateful=True)
        self.scenario.insert_pre_stub('localhost:1stub1matcher', stub)
        with self.assertRaises(HTTPClientError):
            export_stubs(request_handler, '1stub1matcher')

    def test_runnable_requires_playback(self):
        from stubo.service.api import export_stubs
        from stubo.exceptions import HTTPClientError

        request_handler = DummyRequestHandler(session_id=['1'],
                                              runnable=['true'],
                                              playback_session=['myrunnable'])
        self._make_scenario('localhost:1stub1matcher')
        from stubo.model.stub import create, Stub

        stub = Stub(create('<test>match this</test>', '<test>OK</test>'),
                    'localhost:1stub1matcher')
        doc = dict(scenario='localhost:1stub1matcher', stub=stub)
        self.scenario.insert_stub(doc, stateful=True)
        self.scenario.insert_pre_stub('localhost:1stub1matcher', stub)
        with self.assertRaises(HTTPClientError):
            export_stubs(request_handler, '1stub1matcher')

    def test_runnable(self):
        from stubo.service.api import export_stubs

        request_handler = DummyRequestHandler(session_id=['1'],
                                              runnable=['true'],
                                              playback_session=['myrunnable'])
        self._make_scenario('localhost:1stub1matcher')
        from stubo.model.stub import create, Stub

        stub = Stub(create('<test>match this</test>', '<test>OK</test>'),
                    'localhost:1stub1matcher')
        doc = dict(scenario='localhost:1stub1matcher', stub=stub)
        self.scenario.insert_stub(doc, stateful=True)
        import json

        payload = json.dumps(stub.payload)
        self.tracker.insert(dict(scenario='localhost:1stub1matcher',
                                 request_text=payload,
                                 request_params=dict(scenario='1stub1matcher'),
                                 request_headers=dict(),
                                 function='put/stub',
                                 stubo_response='<test>OK</test>'))
        response = export_stubs(request_handler, '1stub1matcher')
        self.assertTrue('runnable' in response['data'])
        runnable = response['data']['runnable']
        self.assertEqual(runnable.get('playback_session'), 'myrunnable')
        self.assertEqual(runnable.get('number_of_playback_requests'), 1)

    def test_1stub_1matcher(self):
        from stubo.service.api import export_stubs
        import os.path

        request_handler = DummyRequestHandler(session_id=['1'])
        self._make_scenario('localhost:1stub1matcher')
        from stubo.model.stub import create, Stub

        stub = Stub(create('<test>match this</test>', '<test>OK</test>'),
                    'localhost:1stub1matcher')
        self.scenario.insert_pre_stub('localhost:1stub1matcher', stub)

        response = export_stubs(request_handler, '1stub1matcher').get('data')
        self.assertEqual(response['scenario'], '1stub1matcher')
        self.assertTrue(len(response['yaml_links']), 5)
        local_server = 'http://{0}:{1}'.format(request_handler.track.server,
                                               request_handler.track.port)
        self.assertEqual(response['yaml_links'], [
            ('1stub1matcher_1_0.json',
             local_server + '/static/exports/localhost_1stub1matcher/yaml_format/1stub1matcher_1_0.json'),
            ('1stub1matcher.yaml',
             local_server + '/static/exports/localhost_1stub1matcher/yaml_format/1stub1matcher.yaml'),
            ('1stub1matcher.zip',
             local_server + '/static/exports/localhost_1stub1matcher/yaml_format/1stub1matcher.zip'),
            ('1stub1matcher.tar.gz',
             local_server + '/static/exports/localhost_1stub1matcher/yaml_format/1stub1matcher.tar.gz'),
            ('1stub1matcher.jar',
             local_server + '/static/exports/localhost_1stub1matcher/yaml_format/1stub1matcher.jar')])

        scenario_dir = response['export_dir_path']
        files = [os.path.join(scenario_dir, x[0]) for x in response['yaml_links']]
        for f in files:
            self.assertTrue(os.path.exists(f))

        expected = ['recording:\n', '  scenario: 1stub1matcher\n', '  session: 1stub1matcher_1\n', '  stubs:\n',
                    '  - file: 1stub1matcher_1_0.json\n']

        with open(os.path.join(scenario_dir, '1stub1matcher.yaml')) as f:
            lines = f.readlines()
            self.assertEqual([x.strip() for x in lines[1:]],
                             [x.strip() for x in expected])

        with open(os.path.join(scenario_dir, '1stub1matcher_1_0.json')) as f:
            payload = f.read()
            self.assertEqual(payload, """{
   "args": {}, 
   "request": {
      "bodyPatterns": {
         "contains": [
            "<test>match this</test>"
         ]
      }, 
      "method": "POST"
   }, 
   "response": {
      "body": "<test>OK</test>", 
      "status": 200
   }
}""")
        self._delete_tmp_export_dir(scenario_dir)

    def test_1stub_2matcher(self):
        from stubo.service.api import export_stubs
        import os.path

        scenario_name = 'x'
        handler = DummyRequestHandler(session_id=['1'])
        self._make_scenario('localhost:x')
        from stubo.model.stub import Stub

        stub = Stub(make_stub(['<test>match this</test>',
                               '<test>and this</test>'], '<test>OK</test>',
                              delay_policy='slow'), scenario=scenario_name)
        self.scenario.insert_pre_stub('localhost:x', stub)
        response = export_stubs(handler, scenario_name).get('data')
        self.assertEqual(response['scenario'], scenario_name)
        self.assertTrue(len(response['yaml_links']), 6)
        local_server = 'http://{0}:{1}'.format(handler.track.server,
                                               handler.track.port)
        self.assertEqual(response['yaml_links'], [
            ('x_1_0.json', local_server + '/static/exports/localhost_x/yaml_format/x_1_0.json'),
            ('x.yaml', local_server + '/static/exports/localhost_x/yaml_format/x.yaml'),
            ('x.zip', local_server + '/static/exports/localhost_x/yaml_format/x.zip'),
            ('x.tar.gz', local_server + '/static/exports/localhost_x/yaml_format/x.tar.gz'),
            ('x.jar', local_server + '/static/exports/localhost_x/yaml_format/x.jar')])

        scenario_dir = response['export_dir_path']
        files = [os.path.join(scenario_dir, x[0]) for x in response['yaml_links']]
        for f in files:
            self.assertTrue(os.path.exists(f))

        self._delete_tmp_export_dir(scenario_dir)

    def test_2stub_2matcher(self):
        from stubo.service.api import export_stubs
        import os.path

        scenario_name = 'x'
        self._make_scenario('localhost:x')
        from stubo.model.stub import Stub

        stub = Stub(make_stub(['<test>match this</test>',
                               '<test>and this</test>'], '<test>OK</test>',
                              delay_policy='slow'), scenario=scenario_name)
        self.scenario.insert_pre_stub('localhost:x', stub)

        stub2 = Stub(make_stub(['<test>match this 2</test>',
                                '<test>and this</test>'], '<test>OK</test>',
                               delay_policy='slow'), scenario=scenario_name)
        self.scenario.insert_pre_stub('localhost:x', stub2)

        handler = DummyRequestHandler(session_id=['1'])
        response = export_stubs(handler, scenario_name).get('data')
        self.assertEqual(response['scenario'], scenario_name)
        self.assertTrue(len(response['yaml_links']), 9)
        local_server = 'http://{0}:{1}'.format(handler.track.server,
                                               handler.track.port)
        self.assertEqual(response['yaml_links'], [
            ('x_1_0.json', local_server + '/static/exports/localhost_x/yaml_format/x_1_0.json'),
            ('x_1_1.json', local_server + '/static/exports/localhost_x/yaml_format/x_1_1.json'),
            ('x.yaml', local_server + '/static/exports/localhost_x/yaml_format/x.yaml'),
            ('x.zip', local_server + '/static/exports/localhost_x/yaml_format/x.zip'),
            ('x.tar.gz', local_server + '/static/exports/localhost_x/yaml_format/x.tar.gz'),
            ('x.jar', local_server + '/static/exports/localhost_x/yaml_format/x.jar')])

        scenario_dir = response['export_dir_path']
        files = [os.path.join(scenario_dir, x[0]) for x in response['yaml_links']]
        for f in files:
            self.assertTrue(os.path.exists(f))

        self._delete_tmp_export_dir(scenario_dir)

    def test_0stub_0matcher(self):
        from stubo.service.api import export_stubs
        import os.path

        request_handler = DummyRequestHandler(session_id=['1'])
        self._make_scenario('localhost:0stub0matcher')

        response = export_stubs(request_handler, '0stub0matcher').get('data')
        self.assertEqual(response['scenario'], '0stub0matcher')
        self.assertTrue(len(response['yaml_links']), 5)
        self.assertTrue(len(response['command_links']), 4)
        local_server = 'http://{0}:{1}'.format(request_handler.track.server,
                                               request_handler.track.port)

        self.assertEqual(response['yaml_links'], [
            ('0stub0matcher_1_0.json',
             local_server + '/static/exports/localhost_0stub0matcher/yaml_format/0stub0matcher_1_0.json'),
            ('0stub0matcher.yaml',
             local_server + '/static/exports/localhost_0stub0matcher/yaml_format/0stub0matcher.yaml'),
            ('0stub0matcher.zip',
             local_server + '/static/exports/localhost_0stub0matcher/yaml_format/0stub0matcher.zip'),
            ('0stub0matcher.tar.gz',
             local_server + '/static/exports/localhost_0stub0matcher/yaml_format/0stub0matcher.tar.gz'),
            ('0stub0matcher.jar',
             local_server + '/static/exports/localhost_0stub0matcher/yaml_format/0stub0matcher.jar')
        ])
        scenario_dir = response['export_dir_path']
        files = [os.path.join(scenario_dir, x[0]) for x in response['yaml_links']]
        for f in files:
            self.assertTrue(os.path.exists(f))

        expected = ['recording:\n', '  scenario: 0stub0matcher\n', '  session: 0stub0matcher_1\n', '  stubs: []\n']

        with open(os.path.join(scenario_dir, '0stub0matcher.yaml')) as f:
            lines = f.readlines()
            self.assertEqual([x.strip() for x in lines[1:]],
                             [x.strip() for x in expected])

        self._delete_tmp_export_dir(scenario_dir)


class TestDelayPolicy(unittest.TestCase):
    def setUp(self):
        self.cache = DummyCache('localhost')
        self.patch = mock.patch('stubo.service.api.Cache', self.cache)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()

    def make_request(self, **kwargs):
        return DummyRequestHandler(**kwargs)

    def test_get_empty(self):
        from stubo.service.api import get_delay_policy

        response = get_delay_policy(self.make_request(), 'bogus', True)
        self.assertEqual(response['data'], {})

    def test_get(self):
        from stubo.service.api import get_delay_policy

        self.cache.set_delay_policy('slow', {u'delay_type': u'fixed', u'name': u'slow', u'milliseconds': u'200'})
        response = get_delay_policy(self.make_request(), 'slow', True)
        self.assertEqual(response['data'], {u'delay_type': u'fixed', u'name': u'slow', u'milliseconds': u'200'})

    def test_delete(self):
        from stubo.service.api import delete_delay_policy

        self.cache.set_delay_policy('slow', {u'delay_type': u'fixed',
                                             u'name': u'slow', u'milliseconds': u'200'})
        response = delete_delay_policy(self.make_request(), ['slow'])
        self.cache.get_delay_policy('slow')
        self.assertEqual(self.cache.get_delay_policy(self.make_request(),
                                                     'slow'), None)
        self.assertEqual(response['data'].get('message'),
                         "Deleted 1 delay policies from ['slow']")

    def test_multi_delete(self):
        from stubo.service.api import delete_delay_policy

        self.cache.set_delay_policy('slow', {u'delay_type': u'fixed',
                                             u'name': u'slow', u'milliseconds': u'200'})
        self.cache.set_delay_policy('fast', {u'delay_type': u'fixed',
                                             u'name': u'slow', u'milliseconds': u'1'})

        response = delete_delay_policy(self.make_request(), ['slow', 'fast'])
        self.assertEqual(response['data'].get('message'),
                         "Deleted 2 delay policies from ['slow', 'fast']")

    def test_put_fixed(self):
        from stubo.service.api import update_delay_policy

        args = {
            'delay_type': 'fixed',
            'name': 'x',
            'milliseconds': '700'
        }
        response = update_delay_policy(self.make_request(), args)
        self.assertEqual(response['data']['message'],
                         "Put Delay Policy Finished")
        self.assertEqual(self.cache.get_delay_policy('x'),
                         {'delay_type': 'fixed', 'name': 'x', 'milliseconds': '700'})

    def test_put_normalvariate(self):
        from stubo.service.api import update_delay_policy

        args = {
            'delay_type': 'normalvariate',
            'name': 'x',
            'mean': '100',
            'stddev': '50'
        }
        response = update_delay_policy(self.make_request(), args)
        self.assertEqual(response['data']['message'],
                         "Put Delay Policy Finished")
        self.assertEqual(self.cache.get_delay_policy('x'),
                         {'delay_type': 'normalvariate', 'name': 'x',
                          'mean': '100', 'stddev': '50'})

    def test_put_weighted(self):
        from stubo.service.api import update_delay_policy

        args = {
            'delay_type': 'weighted',
            'name': 'x',
            'delays': 'fixed,30000,5:normalvariate,1000,1000,15:normalvariate,500,1000,70'
        }
        response = update_delay_policy(self.make_request(), args)
        self.assertEqual(response['data']['message'],
                         "Put Delay Policy Finished")
        self.assertEqual(self.cache.get_delay_policy('x'),
                         {'delay_type': 'weighted', 'name': 'x',
                          'delays': 'fixed,30000,5:normalvariate,1000,1000,15:normalvariate,500,1000,70'})

    def test_invalid_args(self):
        from stubo.service.api import update_delay_policy
        from stubo.exceptions import HTTPClientError

        args = {
            'delay_type': 'normalvariate',
            'name': 'x',
            'milliseconds': '700'
        }
        with self.assertRaises(HTTPClientError):
            update_delay_policy(self.make_request(), args)

    def test_invalid_args2(self):
        from stubo.service.api import update_delay_policy
        from stubo.exceptions import HTTPClientError

        args = {
            'delay_type': 'fixed',
            'name': 'x',
            'mean': '700'
        }
        with self.assertRaises(HTTPClientError):
            update_delay_policy(self.make_request(), args)

    def test_invalid_args3(self):
        from stubo.service.api import update_delay_policy
        from stubo.exceptions import HTTPClientError

        args = {
            'delay_type': 'weighted',
            'name': 'x',
        }
        with self.assertRaises(HTTPClientError):
            update_delay_policy(self.make_request(), args)

    def test_invalid_args4(self):
        from stubo.service.api import update_delay_policy
        from stubo.exceptions import HTTPClientError

        args = {
            'delay_type': 'weighted',
            'delays': 'baddata',
        }
        with self.assertRaises(HTTPClientError):
            update_delay_policy(self.make_request(), args)


class TestGetStatus(unittest.TestCase):
    def test_call(self):
        from stubo.service.api import get_status

        response = get_status(DummyRequestHandler())
        self.assertEqual(response.keys(), ['version', 'data'])


from stubo.model.cmds import TextCommandsImporter


class DummyStuboCommandFile(TextCommandsImporter):
    def run_command(self, url, priority):
        return 200
