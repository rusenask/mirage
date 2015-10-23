"""  
    :copyright: (c) 2015 by OpenCredo.
    :license: GPLv3, see LICENSE for more details.
"""

# -*- coding: utf-8 -*-
import json
from stubo.testing import Base
import logging
import datetime
import os
import requests
from stubo import stubo_path

log = logging.getLogger(__name__)

stub_body = {
    "request": {
        "method": "POST",
        "bodyPatterns": [
            {"contains": ["<status>IS_OK</status>"]}
        ]
    },
    "response": {
        "status": 200,
        "body": "<response>YES</response>"
    }
}

stub_body_2 = {
    "request": {
        "method": "POST",
        "bodyPatterns": [
            {"contains": ["<status>IS_OK_2</status>"]}
        ]
    },
    "response": {
        "status": 200,
        "body": "<response>YES</response>"
    }
}


def get_stub(body_contains=None):
    if body_contains is None:
        response = {
            "request": {
                "method": "POST",
                "bodyPatterns": [
                    {"contains": ["<status>IS_OK</status>"]}
                ]
            },
            "response": {
                "status": 200,
                "body": "<response>YES</response>"
            }
        }
    else:
        response = {
            "request": {
                "method": "POST",
                "bodyPatterns": [
                    {"contains": body_contains}
                ]
            },
            "response": {
                "status": 200,
                "body": "<response>YES</response>"
            }
        }
    return response


class TestScenarioOperations(Base):
    def test_put_scenario(self):
        """

        Test scenario insertion with correct details
        """
        response = self._test_insert_scenario()
        self.assertEqual(response.code, 201)
        self.assertEqual(response.headers["Content-Type"],
                         'application/json; charset=UTF-8')
        payload = json.loads(response.body)
        # check if scenario ref link and name are available in payload
        self.assertEqual(payload['scenarioRef'], '/stubo/api/v2/scenarios/objects/localhost:scenario_0001')
        self.assertEqual(payload['name'], 'localhost:scenario_0001')

    def _test_insert_scenario(self, name="scenario_0001"):
        """
        Inserts test scenario
        :return: response from future
        """
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios'), self.stop,
                               method="PUT", body='{"scenario": "%s"}' % name)

        response = self.wait()
        return response

    def test_put_scenario_no_body(self):
        """

        Test scenario insertion with empty body
        """
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios'), self.stop,
                               method="PUT", body="")
        response = self.wait()
        self.assertEqual(response.code, 415, response.reason)
        self.assertEqual(response.reason, 'No JSON body found')

    def test_put_scenario_wrong_body(self):
        """

        Pass a JSON body to put scenario function although do not supply "scenario" key with name
        """
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios'), self.stop,
                               method="PUT", body='{"foo": "bar"}')
        response = self.wait()
        self.assertEqual(response.code, 400, response.reason)
        self.assertEqual(response.reason, 'Scenario name not supplied')

    def test_put_duplicate_scenario(self):
        """

        Test duplicate insertion and error handling
        """
        response = self._test_insert_scenario()
        self.assertEqual(response.code, 201)
        # insert it second time
        response = self._test_insert_scenario()
        self.assertEqual(response.code, 422, response.reason)
        self.assertTrue('already exists' in response.reason)

    def test_put_scenario_name_none(self):
        """

        Test blank scenario name insertion
        """
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios'), self.stop,
                               method="PUT", body='{"scenario": "" }')
        response = self.wait()
        self.assertEqual(response.code, 400, response.reason)
        self.assertTrue('name is blank or contains illegal characters' in response.reason)

    def test_put_scenario_name_w_illegal_chars(self):
        """

        Test scenario name with illegal characters insertion
        """
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios'), self.stop,
                               method="PUT", body='{"scenario": "@foo" }')
        response = self.wait()
        self.assertEqual(response.code, 400, response.reason)
        self.assertTrue('name is blank or contains illegal characters' in response.reason)
        self.assertTrue('@foo' in response.reason)

    def test_put_scenario_name_w_hostname(self):
        """

        Test override function - providing hostname for stubo to create a scenario with it
        """
        response = self._test_insert_scenario(name="hostname:scenario_name_x")
        self.assertEqual(response.code, 201)
        payload = json.loads(response.body)
        # check if scenario ref link and name are available in payload
        self.assertEqual(payload['scenarioRef'], '/stubo/api/v2/scenarios/objects/hostname:scenario_name_x')
        self.assertEqual(payload['name'], 'hostname:scenario_name_x')

    def test_get_all_scenarios(self):
        """

        Test getting multiple scenarios
        """
        # creating some scenarios
        for scenario_number in xrange(5):
            response = self._test_insert_scenario(name="scenario_name_with_no_%s" % scenario_number)
            self.assertEqual(response.code, 201)

        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios'), self.stop, method="GET")
        response = self.wait()
        self.assertEqual(response.code, 200)
        payload = json.loads(response.body)
        self.assertTrue('data' in payload)
        self.assertEqual(len(payload['data']), 5)

    def test_get_all_scenarios_with_details(self):
        """

        Test getting multiple scenarios with details
        """
        # creating some scenarios
        for scenario_number in xrange(5):
            response = self._test_insert_scenario(name="scenario_name_with_no_%s" % scenario_number)
            self.assertEqual(response.code, 201)

        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/detail'), self.stop, method="GET")
        response = self.wait()
        self.assertEqual(response.code, 200)
        payload = json.loads(response.body)
        self.assertTrue('data' in payload)
        self.assertTrue('name' in payload['data'][1])
        self.assertTrue('recorded' in payload['data'][1])
        self.assertTrue('space_used_kb' in payload['data'][1])
        self.assertTrue('stub_count' in payload['data'][1])
        self.assertEqual(len(payload['data']), 5)

    def test_get_all_scenarios_with_post_method(self):
        """

        Test getting multiple scenarios with details using POST, PUT methods
        """
        # using PUT method
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/detail'), self.stop,
                               method="PUT", body='{"foo": "bar"}')
        response = self.wait()
        self.assertEqual(response.code, 405, response.reason)

        # using POST method
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/detail'), self.stop,
                               method="POST", body='{"foo": "bar"}')
        response = self.wait()
        self.assertEqual(response.code, 405, response.reason)

        # using DELETE method
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/detail'), self.stop,
                               method="DELETE")
        response = self.wait()
        self.assertEqual(response.code, 405, response.reason)

    def test_get_scenario_details(self):
        """

        Test get scenario details, should also do a basic check of details provided
        """
        response = self._test_insert_scenario("new_scenario_details")
        self.assertEqual(response.code, 201)

        # get inserted scenario
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/objects/new_scenario_details'),
                               self.stop, method="GET")
        response = self.wait()
        self.assertEqual(response.code, 200, response.reason)
        payload = json.loads(response.body)
        self.assertEqual(payload['scenarioRef'], '/stubo/api/v2/scenarios/objects/localhost:new_scenario_details')
        self.assertEqual(payload['name'], 'localhost:new_scenario_details')
        self.assertEqual(payload['space_used_kb'], 0)

    def test_delete_scenario(self):
        """

        Test scenario deletion
        """
        response = self._test_insert_scenario("new_scenario_for_deletion")
        self.assertEqual(response.code, 201)

        # delete scenario
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/objects/new_scenario_for_deletion'),
                               self.stop, method="DELETE")
        response = self.wait()
        self.assertEqual(response.code, 200, response.reason)

    def test_non_existing_delete_scenario(self):
        """

        Test scenario deletion
        """
        response = self._test_insert_scenario("new_scenario_for_deletion")
        self.assertEqual(response.code, 201)

        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/objects/new_scenario_for_deletion'),
                               self.stop, method="DELETE")
        response = self.wait()
        self.assertEqual(response.code, 200, response.reason)

        # trying to delete scenario again
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/objects/new_scenario_for_deletion'),
                               self.stop, method="DELETE")
        response = self.wait()
        # expecting to get "precondition failed"
        self.assertEqual(response.code, 412, response.reason)


class TestSessionOperations(Base):
    def _test_insert_scenario(self, name="scenario_0001"):
        """
        Inserts test scenario
        :return: response from future
        """
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios'), self.stop,
                               method="PUT", body='{"scenario": "%s"}' % name)

        response = self.wait()
        return response

    def test_begin_n_end_session(self):
        """

        Test begin session
        """
        response = self._test_insert_scenario("new_scenario_0x")
        self.assertEqual(response.code, 201)

        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/objects/new_scenario_0x/action'),
                               self.stop,
                               method="POST",
                               body='{ "begin": null, "session": "session_name", "mode": "record" }')
        response = self.wait()
        self.assertEqual(response.code, 200, response.reason)
        body_dict = json.loads(response.body)['data']
        self.assertEqual(body_dict['status'], 'record')
        self.assertEqual(body_dict['session'], 'session_name')
        # splitting scenario name and comparing only scenario name (removing hostname)
        self.assertEqual(body_dict['scenario'].split(":")[1], 'new_scenario_0x')
        self.assertTrue('scenarioRef' in body_dict)
        self.assertTrue('message' in body_dict)

        # ending session
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/objects/new_scenario_0x/action'),
                               self.stop,
                               method="POST",
                               body='{ "end": null, "session": "session_name" }')
        response = self.wait()
        self.assertEqual(response.code, 200, response.reason)

    def test_begin_n_end_session_for_another_host(self):
        """

        Test begin and end session for different host
        """

        # creating scenario for host with hostname "some_host"
        response = self._test_insert_scenario("some_host:new_scenario_0x")
        self.assertEqual(response.code, 201)

        # starting session
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/objects/some_host:new_scenario_0x/action'),
                               self.stop,
                               method="POST",
                               body='{ "begin": null, "session": "session_name", "mode": "record" }')
        response = self.wait()
        self.assertEqual(response.code, 200, response.reason)
        body_dict = json.loads(response.body)['data']
        self.assertEqual(body_dict['status'], 'record')
        self.assertEqual(body_dict['session'], 'session_name')
        # splitting scenario name and comparing only scenario name (removing hostname)
        self.assertEqual(body_dict['scenario'].split(":")[1], 'new_scenario_0x')
        self.assertTrue('scenarioRef' in body_dict)
        self.assertTrue('message' in body_dict)

        # ending session
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/objects/some_host:new_scenario_0x/action'),
                               self.stop,
                               method="POST",
                               body='{ "end": null, "session": "session_name" }')
        response = self.wait()
        self.assertEqual(response.code, 200, response.reason)
        self.assertTrue('"data": {"message": "Session ended"}' in response.body)

    def test_end_all_sessions(self):
        """

        Test end all sessions - creating scenario, then multiple sessions setting to record, then to dormant.
        """
        response = self._test_insert_scenario("new_scenario_0x")
        self.assertEqual(response.code, 201)

        session_count = 10
        # inserting some sessions
        for session_number in xrange(session_count):
            self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/objects/new_scenario_0x/action'),
                                   self.stop,
                                   method="POST",
                                   body='{ "begin": null, "session": "session_name_%s", "mode": "record" }'
                                        % session_number)
            response = self.wait()
            self.assertEqual(response.code, 200, response.reason)

        # ordering stubo to finish them all!
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/objects/new_scenario_0x/action'),
                               self.stop,
                               method="POST",
                               body='{ "end": "sessions"}')
        response = self.wait()
        self.assertEqual(response.code, 200, response.reason)
        # checking whether 10 sessions were affected
        self.assertEqual(len(json.loads(response.body)['data']), 10)

    def test_end_all_sessions_for_another_host(self):
        """

        Test end all sessions for another host -
        creating scenario, then multiple sessions setting to record, then to dormant.
        """
        response = self._test_insert_scenario("new_host:new_scenario_0x")
        self.assertEqual(response.code, 201)

        session_count = 10
        # inserting some sessions
        for session_number in xrange(session_count):
            self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/objects/new_host:new_scenario_0x/action'),
                                   self.stop,
                                   method="POST",
                                   body='{ "begin": null, "session": "session_name_%s", "mode": "record" }'
                                        % session_number)
            response = self.wait()
            self.assertEqual(response.code, 200, response.reason)

        # ordering stubo to finish them all!
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/objects/new_host:new_scenario_0x/action'),
                               self.stop,
                               method="POST",
                               body='{ "end": "sessions"}')
        response = self.wait()
        self.assertEqual(response.code, 200, response.reason)
        # checking whether 10 sessions were affected
        self.assertEqual(len(json.loads(response.body)['data']), 10)

class TestDelayOperations(Base):
    """
    Test case for testing delay operations (add, update, delete)
    """

    def test_add_new_fixed_delay_policy(self):
        """

        Tests fixed delay policy creation and checks status, name, delay type
        """
        name = "new_delay"
        response = self._add_fixed_delay_policy(name=name)
        self.assertEqual(response.code, 201, response.reason)
        json_body = json.loads(response.body)
        self.assertEqual(json_body['data']['name'], name)
        self.assertEqual(json_body['data']['status'], 'new')
        self.assertEqual(json_body['data']['delay_type'], 'fixed')

    def test_add_whitespace_to_name(self):
        """

        Tests adding whitespace to delay policy name - should result in bad request 400
        """
        name = "new delay"
        response = self._add_fixed_delay_policy(name=name)
        self.assertEqual(response.code, 400, response.reason)

    def test_update_fixed_delay_policy(self):
        """

        Checking update function's status code and status message (should be "updated")
        """
        name = "fixed_for_update"
        # creating first delay policy
        self._add_fixed_delay_policy(name=name)
        # updating it and checking status
        response = self._add_fixed_delay_policy(name=name)
        self.assertEqual(response.code, 200, response.reason)
        json_body = json.loads(response.body)
        self.assertEqual(json_body['data']['name'], name)
        self.assertEqual(json_body['data']['status'], 'updated')
        self.assertEqual(json_body['data']['delay_type'], 'fixed')

    def _add_fixed_delay_policy(self, name="my_delay"):
        """

        Creates new fixed delay (or not, if something goes wrong, does not process response)
        :param name:
        :return:
        """
        self.http_client.fetch(self.get_url('/stubo/api/v2/delay-policy'),
                               self.stop,
                               method="PUT",
                               body='{ "name": "%s", "delay_type": "fixed", "milliseconds": 50 }' % name)
        response = self.wait()
        return response

    def test_add_new_normalvariate_delay_policy(self):
        """

        Tests normalvariate delay policy creation and checks status, name, delay type
        """
        name = "normal_variate"
        response = self._add_normalvariate_delay_policy(name=name)
        self.assertEqual(response.code, 201, response.reason)
        json_body = json.loads(response.body)
        self.assertEqual(json_body['data']['name'], name)
        self.assertEqual(json_body['data']['status'], 'new')
        self.assertEqual(json_body['data']['delay_type'], 'normalvariate')

    def test_update_normalvariate_delay_policy(self):
        """

        Checking update function's status code and status message (should be "updated")
        """
        name = "normal_variate_for_update"
        # creating first delay policy
        self._add_normalvariate_delay_policy(name=name)
        # updating it and checking status
        response = self._add_normalvariate_delay_policy(name=name)
        self.assertEqual(response.code, 200, response.reason)
        json_body = json.loads(response.body)
        self.assertEqual(json_body['data']['name'], name)
        self.assertEqual(json_body['data']['status'], 'updated')
        self.assertEqual(json_body['data']['delay_type'], 'normalvariate')

    def _add_normalvariate_delay_policy(self, name="my_delay_normv"):
        """

        Creates new normalvariate delay (or not, if something goes wrong, does not process response)
        :param name:
        :return:
        """
        self.http_client.fetch(self.get_url('/stubo/api/v2/delay-policy'),
                               self.stop,
                               method="PUT",
                               body='{ "name": "%s", "delay_type": "normalvariate", '
                                    '"mean": 50, "stddev": 10 }' % name)
        response = self.wait()
        return response

    def test_add_new_weighted_delay_policy(self):
        name = "weighted_delay"
        response = self._add_weighted_delay_policy(name=name)
        self.assertEqual(response.code, 201, response.reason)
        json_body = json.loads(response.body)
        self.assertEqual(json_body['data']['name'], name)
        self.assertEqual(json_body['data']['status'], 'new')
        self.assertEqual(json_body['data']['delay_type'], 'weighted')

    def test_update_weighted_delay_policy(self):
        """

        Checking update function's status code and status message (should be "updated")
        """
        name = "weighted_for_update"
        # creating first delay policy
        self._add_fixed_delay_policy(name=name)
        # updating it and checking status
        response = self._add_weighted_delay_policy(name=name)
        self.assertEqual(response.code, 200, response.reason)
        json_body = json.loads(response.body)
        self.assertEqual(json_body['data']['name'], name)
        self.assertEqual(json_body['data']['status'], 'updated')
        self.assertEqual(json_body['data']['delay_type'], 'weighted')

    def _add_weighted_delay_policy(self, name="my_delay_weighted"):
        """

        Creates new normalvariate delay (or not, if something goes wrong, does not process response)
        :param name:
        :return:
        """
        self.http_client.fetch(self.get_url('/stubo/api/v2/delay-policy'),
                               self.stop,
                               method="PUT",
                               body='{ "name": "%s", "delay_type": "weighted", '
                                    '"delays": "fixed,30000,5:normalvariate,5000,1000,15:normalvariate,1000,500,70" }'
                                    % name)
        response = self.wait()
        return response

    def test_bad_delay_type_key(self):
        """

        Passing malformed request body with bad keys to update delay policy handler
        """
        self.http_client.fetch(self.get_url('/stubo/api/v2/delay-policy'),
                               self.stop,
                               method="PUT",
                               body='{ "name": "malformed_delay", "delayyy_type": "fixed", "milliseconds": 50 }')
        response = self.wait()
        self.assertEqual(response.code, 400, response.reason)

    def test_bad_delay_name_key(self):
        """
        Skipping delay name when creating
        """
        self.http_client.fetch(self.get_url('/stubo/api/v2/delay-policy'),
                               self.stop,
                               method="PUT",
                               body='{ "foo": "malformed_delay", "delay_type": "fixed", "milliseconds": 50 }')
        response = self.wait()
        self.assertEqual(response.code, 400, response.reason)

    def test_mixed_params_normalvariate(self):
        """
        Skipping mean and stddev when creating normalvariate delay
        """
        self.http_client.fetch(self.get_url('/stubo/api/v2/delay-policy'),
                               self.stop,
                               method="PUT",
                               body='{ "name": "mixed_params", "delay_type": "normalvariate", "milliseconds": 50 }')
        response = self.wait()
        self.assertEqual(response.code, 409, response.reason)

    def test_mixed_params_fixed_wo_milliseconds(self):
        """

        Supplying mean parameter instead of milliseconds when creating fixed delay
        """
        self.http_client.fetch(self.get_url('/stubo/api/v2/delay-policy'),
                               self.stop,
                               method="PUT",
                               body='{ "name": "mixed_params", "delay_type": "fixed", "mean": 50 }')
        response = self.wait()
        self.assertEqual(response.code, 409, response.reason)

    def test_get_all_delays(self):
        """

        Testing multiple delay policies creation and then getting them all, checking length
        :return:
        """
        count = 10
        for name_fix in xrange(count):
            name = "new_delay_%s" % name_fix
            self._add_fixed_delay_policy(name=name)

        # getting delay list
        self.http_client.fetch(self.get_url('/stubo/api/v2/delay-policy/detail'),
                               self.stop,
                               method="GET")
        response = self.wait()
        bd = json.loads(response.body)
        self.assertEqual(len(bd['data']), count)

    def test_get_specific_delay(self):
        """

        Tests getting specific delay details
        """
        name = "specific_delay"
        self._add_fixed_delay_policy(name=name)

        self.http_client.fetch(self.get_url('/stubo/api/v2/delay-policy/objects/%s' % name),
                               self.stop,
                               method="GET")
        response = self.wait()
        self.assertEqual(response.code, 200, response.reason)
        self.assertTrue(name in response.body)

    def test_get_non_existing_specific_delay(self):
        """

        Tests getting specific delay details
        """
        name = "specific_missing_delay"
        self.http_client.fetch(self.get_url('/stubo/api/v2/delay-policy/objects/%s' % name),
                               self.stop,
                               method="GET")
        response = self.wait()
        self.assertEqual(response.code, 404, response.reason)
        self.assertTrue(name in response.body)

    def test_delete_delay_policy(self):
        """

        Test deleting specific delay policy
        """
        name = "specific_delay_for_deletion"
        self._add_fixed_delay_policy(name=name)

        self.http_client.fetch(self.get_url('/stubo/api/v2/delay-policy/objects/%s' % name),
                               self.stop,
                               method="GET")
        response = self.wait()
        # check whether it is already there
        self.assertEqual(response.code, 200, response.reason)
        self.assertTrue(name in response.body)

        # delete delay policy
        self.http_client.fetch(self.get_url('/stubo/api/v2/delay-policy/objects/%s' % name),
                               self.stop,
                               method="DELETE")
        response = self.wait()
        self.assertEqual(response.code, 200, response.reason)
        self.assertTrue(name in response.body)
        self.assertTrue("Deleted" in response.body)


class TestStubOperations(Base):
    """
    Test case for testing delay operations (add, update, delete)
    """

    def test_get_scenario_stubs(self):
        """
        Tests scenario/stubs functionality (outputs all stubs for specified scenario

        """
        scenario_name = "scenario_stub_test_x"
        session_name = "session_stub_test_x"

        # insert scenario
        self._insert_scenario(scenario_name)
        # begin recording
        self._begin_session_(session_name, scenario_name, "record")

        # inserting stub
        response = self._add_stub(session=session_name, scenario=scenario_name, body=get_stub())
        # after insertion there should be one stub and since it's a creation - response code should be 201
        self.assertEqual(response.code, 201, response.reason)

        # getting stubs
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/objects/%s/stubs' % scenario_name),
                               self.stop,
                               method="GET")
        response = self.wait()
        self.assertEqual(200, response.code, response.reason)
        self.assertTrue('data' in response.body)

        # checking whether there is one stub in response body
        body_dict = json.loads(response.body)
        self.assertEqual(len(body_dict['data']), 1)

        # wiping stubs
        self._delete_stubs(scenario_name)

    def test_update_stateful_stub(self):
        """
        Tests update stateful stub

        """
        scenario_name = "scenario_stub_stateful_test_x"
        session_name = "session_stub_stateful_test_x"

        # insert scenario
        self._insert_scenario(scenario_name)
        # begin recording
        self._begin_session_(session_name, scenario_name, "record")

        # inserting stub
        response = self._add_stub(session=session_name, scenario=scenario_name, body=get_stub())
        # after insertion there should be one stub and since it's a creation - response code should be 201
        self.assertEqual(response.code, 201, response.reason)

        # inserting stub second time, should result in update
        response = self._add_stub(session=session_name, scenario=scenario_name, body=get_stub())
        # after insertion there should be one stub and since it's a creation - response code should be 201
        self.assertEqual(response.code, 200, response.reason)

        # getting stubs
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/objects/%s/stubs' % scenario_name),
                               self.stop,
                               method="GET")
        response = self.wait()
        self.assertEqual(200, response.code, response.reason)
        self.assertTrue('data' in response.body)

        # checking whether there is one stub in response body, should be still 1
        body_dict = json.loads(response.body)
        self.assertEqual(len(body_dict['data']), 1)

        # wiping stubs
        self._delete_stubs(scenario_name)

    def test_insert_multiple_stubs(self):
        """
        Test for insert multiple stubs

        """
        scenario_name = "scenario_stub_multi_test_x"
        session_name = "session_stub_multi_test_x"

        # insert scenario
        self._insert_scenario(scenario_name)
        # begin recording
        self._begin_session_(session_name, scenario_name, "record")

        for stub in xrange(10):
            body = get_stub(["<status>IS_OK%s</status>" % stub])
            # inserting stub
            response = self._add_stub(session=session_name, scenario=scenario_name, body=body)
            # after insertion there should be one stub and since it's a creation - response code should be 201
            self.assertEqual(response.code, 201, response.reason)
        # getting stubs
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/objects/%s/stubs' % scenario_name),
                               self.stop,
                               method="GET")
        response = self.wait()
        self.assertEqual(200, response.code, response.reason)
        self.assertTrue('data' in response.body)

        # checking whether there is one stub in response body, should be 10
        body_dict = json.loads(response.body)
        self.assertEqual(len(body_dict['data']), 10)

        # wiping stubs
        self._delete_stubs(scenario_name)

    def test_export_scenario_stubs(self):
        """
        Test scenario export functionality. Creates a scenario, inserts stubs, ends session.
        Then exports scenario and checks for contents. Deletes scenario in the end.

        """
        scenario_name = "scenario_stub_multi_test_x"
        session_name = "session_stub_multi_test_x"

        # insert scenario
        self._insert_scenario(scenario_name)
        # begin recording
        self._begin_session_(session_name, scenario_name, "record")

        for stub in xrange(10):
            body = get_stub(["<status>IS_OK%s</status>" % stub])
            # inserting stub
            response = self._add_stub(session=session_name, scenario=scenario_name, body=body)
            # after insertion there should be one stub and since it's a creation - response code should be 201
            self.assertEqual(response.code, 201, response.reason)
        # getting stubs
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/objects/%s/stubs' % scenario_name),
                               self.stop,
                               method="GET")
        response = self.wait()
        self.assertEqual(200, response.code, response.reason)
        self.assertTrue('data' in response.body)

        # ending session
        self._end_session(session_name, scenario_name)

        # exporting scenario
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/objects/scenario_stub_multi_test_x/action'),
                               self.stop,
                               method="POST",
                               body='{ "export": null}')
        response = self.wait()
        bd = json.loads(response.body)
        # checking response for command, yaml links and scenario name
        self.assertTrue('command_links' in bd['data'])
        # there should be four items in command links: commands, zip, tar.gz, jar
        self.assertEqual(len(bd['data']['command_links']), 4, bd['data']['command_links'])
        self.assertTrue('yaml_links' in bd['data'])

        # there should be five items in yaml links: json, yaml, zip, tar.gz, jar
        self.assertEqual(len(bd['data']['yaml_links']), 5, bd['data']['yaml_links'])

        self.assertEqual(scenario_name, bd['data']['scenario'])

        # wiping stubs
        self._delete_stubs(scenario_name)

    def test_upload_scenario(self):
        """

        Test scenario upload (yaml configuration, zip content type) to /api/v2/scenarios/upload API handler
        """
        # getting file
        stubo_dir = stubo_path()

        test_file = os.path.join(stubo_dir, 'static/cmds/tests/upload/scenario_100.zip')
        f = open(test_file)
        files = [('files', ('scenario_100', f, 'application/zip'))]

        data = {}
        a = requests.Request(url="http://not_important/",
                             files=files, data=data)
        prepare = a.prepare()
        f.close()

        content_type = prepare.headers.get('Content-Type')
        body = prepare.body

        url = "/api/v2/scenarios/upload"
        headers = {
            "Content-Type": content_type,
        }

        response = self.fetch(url, method='POST', body=body, headers=headers)

        self.assertEquals(response.code, 200)
        self.assertEqual('{"total": 200, "session": "scenario_100_1445435070", "scenario": "scenario_100"}',
                         response.body)

    def test_upload_wrong_format(self):
        """

        Testing /api/v2/scenarios/upload handler, supplying wrong format
        """
        # getting file
        stubo_dir = stubo_path()

        test_file = os.path.join(stubo_dir, 'static/cmds/tests/upload/scenario_100.zip')
        f = open(test_file)

        # using not supported file encoding
        files = [('files', ('scenario_100', f, 'application/something_else'))]

        data = {}
        a = requests.Request(url="http://not_important/",
                             files=files, data=data)
        prepare = a.prepare()
        f.close()

        content_type = prepare.headers.get('Content-Type')
        body = prepare.body

        url = "/api/v2/scenarios/upload"
        headers = {
            "Content-Type": content_type,
        }

        response = self.fetch(url, method='POST', body=body, headers=headers)

        # response code should be 400 (bad request)
        self.assertEquals(response.code, 415)

    def test_upload_missing_stub(self):
        """

        Testing /api/v2/scenarios/upload handler, supplying config with one missing file
        """
        # getting file
        stubo_dir = stubo_path()

        test_file = os.path.join(stubo_dir, 'static/cmds/tests/upload/scenario_missing_stub.zip')
        f = open(test_file)

        files = [('files', ('scenario_100', f, 'application/zip'))]

        data = {}
        a = requests.Request(url="http://not_important/",
                             files=files, data=data)
        prepare = a.prepare()
        f.close()

        content_type = prepare.headers.get('Content-Type')
        body = prepare.body

        url = "/api/v2/scenarios/upload"
        headers = {
            "Content-Type": content_type,
        }

        response = self.fetch(url, method='POST', body=body, headers=headers)

        # response code should be 200 (config read successfully however status about failure should appear)
        self.assertEquals(response.code, 200)
        self.assertTrue("Failed to process request/response scenario_100_1445435070_0_missing.json."
                        " Got error: [Errno 2] No such file or directory" in response.body)

    def test_upload_missing_config(self):
        """

        Testing /api/v2/scenarios/upload handler, missing config
        """
        # getting file
        stubo_dir = stubo_path()

        test_file = os.path.join(stubo_dir, 'static/cmds/tests/upload/scenario_no_config.zip')
        f = open(test_file)

        files = [('files', ('scenario_100', f, 'application/zip'))]

        data = {}
        a = requests.Request(url="http://not_important/",
                             files=files, data=data)
        prepare = a.prepare()
        f.close()

        content_type = prepare.headers.get('Content-Type')
        body = prepare.body

        url = "/api/v2/scenarios/upload"
        headers = {
            "Content-Type": content_type,
        }

        response = self.fetch(url, method='POST', body=body, headers=headers)

        # response code should be 200 (config read successfully however status about failure should appear)
        self.assertEquals(response.code, 400)
        self.assertTrue("Configuration file not found" in response.body)

    def test_delete_scenario_stubs(self):
        """
        Test for delete scenario stubs API call
        """
        # inserting 10 stubs into scenario
        self.test_insert_multiple_stubs()

        # ending session before deletion
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/objects/scenario_stub_multi_test_x/action'),
                               self.stop,
                               method="POST",
                               body='{ "end": null, "session": "session_stub_multi_test_x" }')
        response = self.wait()
        self.assertEqual(200, response.code, response.reason)

        # deleting stubs
        response = self._delete_stubs("scenario_stub_multi_test_x")
        self.assertEqual(200, response.code, response.reason)
        self.assertTrue('data' in response.body)

        # getting stubs
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/objects/scenario_stub_multi_test_x/stubs'),
                               self.stop,
                               method="GET")
        response = self.wait()
        # checking whether there is one stub in response body, should be 10
        body_dict = json.loads(response.body)
        self.assertEqual(len(body_dict['data']), 0)

    def test_get_responses(self):
        """
        Tests stubo responses. Firstly, inserts 10 stubs, then ends recording session, starts playback session
        and then uses POST requests with "contains" to get responses from stubo. Each contains is different
        so all 10 stubs are unique.

        """
        # inserting 10 stubs into scenario
        self.test_insert_multiple_stubs()

        # session name from test_insert_multiple_stubs test
        headers = {'session': "session_stub_multi_test_x"}

        # ending session before deletion
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/objects/scenario_stub_multi_test_x/action'),
                               self.stop,
                               method="POST",
                               body='{ "end": null, "session": "session_stub_multi_test_x" }')
        response = self.wait()
        self.assertEqual(200, response.code, response.reason)

        # starting playback mode
        self._begin_session_("session_stub_multi_test_x", "scenario_stub_multi_test_x", "playback")

        # getting responses
        for stub in xrange(10):
            # ending session before deletion
            self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/objects/scenario_stub_multi_test_x/stubs'),
                                   self.stop,
                                   method="POST",
                                   headers=headers,
                                   body="<status>IS_OK%s</status>" % stub)
            response = self.wait()
            self.assertTrue("<response>YES</response>" in response.body)

        # wiping stubs
        self._delete_stubs("scenario_stub_multi_test_x")

    def test_not_found_matches(self):
        """

        Inserts stubs, starts playback session and tries to get some stub with matcher that shouldn't be there
        """
        # inserting 10 stubs into scenario
        self.test_insert_multiple_stubs()

        # session name from test_insert_multiple_stubs test
        headers = {'session': "session_stub_multi_test_x"}

        # ending session before deletion
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/objects/scenario_stub_multi_test_x/action'),
                               self.stop,
                               method="POST",
                               body='{ "end": null, "session": "session_stub_multi_test_x" }')
        response = self.wait()
        self.assertEqual(200, response.code, response.reason)

        # starting playback mode
        self._begin_session_("session_stub_multi_test_x", "scenario_stub_multi_test_x", "playback")

        # ending session before deletion
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/objects/scenario_stub_multi_test_x/stubs'),
                               self.stop,
                               method="POST",
                               headers=headers,
                               body="<status>IS_OK_something_not_expected</status>")
        response = self.wait()
        self.assertEqual(400, response.code)
        self.assertTrue("No matching response found" in response.body)
        # wiping stubs
        self._delete_stubs("scenario_stub_multi_test_x")

    def _delete_stubs(self, name):
        """
        Deletes stubs for specified scenario
        :param name:
        :return:
        """
        # deleting stubs
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/objects/%s/stubs' % name),
                               self.stop,
                               method="DELETE")
        response = self.wait()
        return response

    def _insert_scenario(self, name="scenario_0001"):
        """
        Inserts test scenario
        :return: response from future
        """
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios'), self.stop,
                               method="PUT", body='{"scenario": "%s"}' % name)

        response = self.wait()
        return response

    def _begin_session_(self, session, scenario, mode):
        # starting record session
        """
        Begins session in record mode
        :param session: session name
        :param scenario: scenario name
        """
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/objects/%s/action' % scenario),
                               self.stop,
                               method="POST",
                               body='{ "begin": null, "session": "%s", "mode": "%s" }' % (session, mode))
        response = self.wait()
        self.assertEqual(response.code, 200, response.reason)

    def _end_session(self, session, scenario):
        """
        Ends specified session
        :param session:
        :param scenario:
        """
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/objects/%s/action' % scenario),
                               self.stop,
                               method="POST",
                               body='{ "end": null, "session": "%s" }' % session)
        response = self.wait()
        self.assertEqual(response.code, 200, response.reason)

    def _add_stub(self, session, scenario, body):
        """
        Adds stub for specified scenario
        :param session: session name
        :param scenario: scenario name
        :return: returns a response from Stubo
        """
        headers = {'session': session}
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/objects/%s/stubs' % scenario),
                               self.stop,
                               method="PUT",
                               headers=headers,
                               body=json.dumps(body))
        response = self.wait()
        return response


class TestRecords(Base):
    def test_all_records(self):
        """

        Tests all tracker records API handler, inserts some testing stubs, checks whether information appears in tracker
        API call
        """
        self.http_client.fetch(self.get_url('/stubo/api/exec/cmds?cmdfile='
                                            '/static/cmds/tests/encoding/text/1.commands'),
                               self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)

        self.http_client.fetch(self.get_url('/stubo/api/v2/tracker/records'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        json_body = json.loads(response.body)

        # checking body dict keys
        self.assertTrue('data' in json_body)
        self.assertTrue('paging' in json_body)

        # checking whether tracker collection works
        total_items = json_body['paging']['totalItems']
        record_list = len(json_body['data'])
        self.assertEqual(total_items, record_list)

        # checking pagination
        self.assertIsNone(json_body['paging']['next'], 'Should be none')
        self.assertIsNone(json_body['paging']['previous'], 'Should be none')

    def test_pagination(self):
        """

        testing forward pagination
        """
        self._insert_items_to_tracker()

        self.http_client.fetch(self.get_url('/stubo/api/v2/tracker/records'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        json_body = json.loads(response.body)

        # checking body dict keys
        self.assertTrue('data' in json_body)
        self.assertTrue('paging' in json_body)

        # there should be "next" page since we have 200 records and only 100 is currently being displayed
        self.assertTrue('next' in json_body['paging'])

        # there shouldn't be previous page
        self.assertIsNone(json_body['paging']['previous'])
        self.assertEqual(json_body['paging']['totalItems'], 200)

    def test_pagination_backwards(self):
        """

        testing backwards pagination
        """
        self._insert_items_to_tracker()

        self.http_client.fetch(self.get_url('/stubo/api/v2/tracker/records?skip=100&limit=100'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        json_body = json.loads(response.body)

        # checking body dict keys
        self.assertTrue('data' in json_body)
        self.assertTrue('paging' in json_body)

        # there should be "previous" page since we have 200 records and we are skipping 100
        self.assertTrue('previous' in json_body['paging'])

        # there shouldn't be next page
        self.assertIsNone(json_body['paging']['next'])
        self.assertEqual(json_body['paging']['totalItems'], 200)

    def test_last_page(self):
        """

        Testing last page
        """
        self._insert_items_to_tracker(500)

        self.http_client.fetch(self.get_url('/stubo/api/v2/tracker/records'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        json_body = json.loads(response.body)

        # checking body dict keys
        self.assertTrue('data' in json_body)
        self.assertTrue('paging' in json_body)
        self.assertTrue('last' in json_body['paging'])

        last_page = json_body['paging']['last']
        # in the last page we should be skipping 400 items and limiting results to 100
        self.assertTrue('skip=400' in last_page)
        self.assertTrue('limit=100' in last_page)

    def _insert_items_to_tracker(self, items=200):
        mongo_driver = self.db
        tm = datetime.datetime.now()
        # inserting some data
        for i in xrange(items):
            mongo_driver.tracker.insert({"record": i,
                                         "start_time": tm})


import unittest
from stubo.service.api_v2 import MagicFiltering


class MagicFilterTest(unittest.TestCase):
    op_list = ['<', '<=', '>', '>=']

    op_map = {
        '<': '$lt',
        '<=': '$lte',
        '>': '$gt',
        '>=': '$gte'
    }

    def test_keyword_only(self):
        query = 'scenario1'
        mf = MagicFiltering(query, 'localhost')

        tracker_filter = mf.get_filter()
        self.assertTrue({'host': {'$regex': 'localhost'}} in tracker_filter['$and'])
        self.assertTrue({'$or': [
            {'scenario': {'$options': 'i', '$regex': 'scenario1'}},
            {'function': {'$options': 'i', '$regex': 'scenario1'}}]} in tracker_filter['$and'])

    def test_status_code_only(self):
        """

        Testing status code query creation
        """
        query = 'sc:200'
        mf = MagicFiltering(query, 'localhost')

        tracker_filter = mf.get_filter()
        self.assertTrue({'host': {'$regex': 'localhost'}} in tracker_filter['$and'])
        self.assertTrue({'return_code': 200} in tracker_filter['$and'])

    def test_multiple_status_codes(self):
        """

        Test range for response times
        """
        query = 'sc:>200 sc:<500'
        mf = MagicFiltering(query, 'localhost')

        tracker_filter = mf.get_filter()
        self.assertTrue({'host': {'$regex': 'localhost'}} in tracker_filter['$and'], tracker_filter)
        self.assertTrue({'return_code': {'$gt': 200}} in tracker_filter['$and'], tracker_filter)
        self.assertTrue({'return_code': {'$lt': 500}} in tracker_filter['$and'], tracker_filter)

    def test_response_time_only(self):
        """

        Testing response time query creation
        """
        query = 'rt:10'
        mf = MagicFiltering(query, 'localhost')

        tracker_filter = mf.get_filter()
        self.assertTrue({'host': {'$regex': 'localhost'}} in tracker_filter['$and'])
        self.assertTrue({'duration_ms': 10} in tracker_filter['$and'])

    def test_multiple_response_times(self):
        """

        Test range for response times
        """
        query = 'rt:>10 rt:<15'
        mf = MagicFiltering(query, 'localhost')

        tracker_filter = mf.get_filter()
        self.assertTrue({'host': {'$regex': 'localhost'}} in tracker_filter['$and'], tracker_filter)
        self.assertTrue({'duration_ms': {'$gt': 10}} in tracker_filter['$and'], tracker_filter)
        self.assertTrue({'duration_ms': {'$lt': 15}} in tracker_filter['$and'], tracker_filter)

    def test_rt_sc_mix(self):
        """

        Test a mix of response duration ranges with status code ranges
        """
        query = 'rt:>10 rt:<15 sc:>200 sc:<500'
        mf = MagicFiltering(query, 'localhost')

        tracker_filter = mf.get_filter()
        self.assertTrue({'host': {'$regex': 'localhost'}} in tracker_filter['$and'], tracker_filter)
        self.assertTrue({'duration_ms': {'$gt': 10}} in tracker_filter['$and'], tracker_filter)
        self.assertTrue({'duration_ms': {'$lt': 15}} in tracker_filter['$and'], tracker_filter)
        self.assertTrue({'return_code': {'$gt': 200}} in tracker_filter['$and'], tracker_filter)
        self.assertTrue({'return_code': {'$lt': 500}} in tracker_filter['$and'], tracker_filter)

    def test_rt_sc_keyword_mix(self):
        """

        Test a mix of ranges and keyword
        :return:
        """
        query = 'rt:>10 rt:<15 sc:>200 sc:<500 scenario1'
        mf = MagicFiltering(query, 'localhost')

        tracker_filter = mf.get_filter()
        self.assertTrue({'host': {'$regex': 'localhost'}} in tracker_filter['$and'], tracker_filter)
        self.assertTrue({'duration_ms': {'$gt': 10}} in tracker_filter['$and'], tracker_filter)
        self.assertTrue({'duration_ms': {'$lt': 15}} in tracker_filter['$and'], tracker_filter)
        self.assertTrue({'return_code': {'$gt': 200}} in tracker_filter['$and'], tracker_filter)
        self.assertTrue({'return_code': {'$lt': 500}} in tracker_filter['$and'], tracker_filter)
        self.assertTrue({'$or': [
            {'scenario': {'$options': 'i', '$regex': 'scenario1'}},
            {'function': {'$options': 'i', '$regex': 'scenario1'}}]} in tracker_filter['$and'])

    def test_rt_comparison_operators(self):
        """

        Test response code comparison
        """
        for op in self.op_list:
            # creating query from the list
            query = 'rt:' + op + str(50)
            # finding relevant symbol
            mongo_operator = self.op_map[op]

            mf = MagicFiltering(query, 'localhost')

            tracker_filter = mf.get_filter()
            self.assertTrue({'duration_ms': {mongo_operator: 50}} in tracker_filter['$and'], tracker_filter)

    def test_sc_comparison_operators(self):
        """

        Test status code comparison
        """
        for op in self.op_list:
            # creating query from the list
            query = 'sc:' + op + str(50)
            # finding relevant symbol
            mongo_operator = self.op_map[op]

            mf = MagicFiltering(query, 'localhost')

            tracker_filter = mf.get_filter()
            self.assertTrue({'return_code': {mongo_operator: 50}} in tracker_filter['$and'], tracker_filter)

    def test_status_code_wo_code(self):
        """

        'sc:' should not be treated as status code search since there is no status code. Use it as keyword search
        instead
        """
        query = 'sc:'
        mf = MagicFiltering(query, 'localhost')

        tracker_filter = mf.get_filter()
        self.assertTrue({'host': {'$regex': 'localhost'}} in tracker_filter['$and'])
        self.assertFalse({'return_code': ''} in tracker_filter['$and'])

        self.assertTrue({'$or': [
            {'scenario': {'$options': 'i', '$regex': 'sc:'}},
            {'function': {'$options': 'i', '$regex': 'sc:'}}]} in tracker_filter['$and'])

    def test_status_code_w_bad_code(self):
        """

        'sc:aaa' shouldn't be a keyword search, although it can't be used for status code search either since it is not
        integer
        """
        query = 'sc:aaa'
        mf = MagicFiltering(query, 'localhost')

        tracker_filter = mf.get_filter()
        self.assertTrue({'host': {'$regex': 'localhost'}} in tracker_filter['$and'])
        self.assertFalse({'return_code': 'aaa'} in tracker_filter['$and'])

        self.assertFalse({'$or': [
            {'scenario': {'$options': 'i', '$regex': 'sc:aaa'}},
            {'function': {'$options': 'i', '$regex': 'sc:aaa'}}]} in tracker_filter['$and'])

    def test_response_time_wo_code(self):
        """

        'rt:' should not be treated as response time search since there is no duration in ms. Use it as keyword search
        instead
        """
        query = 'rt:'
        mf = MagicFiltering(query, 'localhost')

        tracker_filter = mf.get_filter()
        self.assertTrue({'host': {'$regex': 'localhost'}} in tracker_filter['$and'])
        self.assertFalse({'duration_ms': ''} in tracker_filter['$and'])

        self.assertTrue({'$or': [
            {'scenario': {'$options': 'i', '$regex': 'rt:'}},
            {'function': {'$options': 'i', '$regex': 'rt:'}}]} in tracker_filter['$and'])

    def test_response_time_w_bad_time(self):
        """

        'rt:aaa' shouldn't be a keyword search, although it can't be used for status code search either since it is not
        integer
        """
        query = 'rt:aaa'
        mf = MagicFiltering(query, 'localhost')

        tracker_filter = mf.get_filter()
        self.assertTrue({'host': {'$regex': 'localhost'}} in tracker_filter['$and'])
        self.assertFalse({'duration_ms': 'aaa'} in tracker_filter['$and'])

        self.assertFalse({'$or': [
            {'scenario': {'$options': 'i', '$regex': 'rt:aaa'}},
            {'function': {'$options': 'i', '$regex': 'rt:aaa'}}]} in tracker_filter['$and'])


class ModuleApiTest(Base):
    """
    Tests for v2 API
    """

    def _insert_module_from_archive(self):
        self.http_client.fetch(self.get_url('/stubo/api/exec/cmds?cmdfile='
                                            '/static/cmds/tests/exports/localhost_split/split.zip'),
                               self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)

    def test_list_modules(self):
        """

        Tests API v2 module list functionality (displaying href, name in separate fields).
        First it inserts a module through the API v1 commands file, then calls API v2
        to list the modules and looks for the inserted module.
        """
        # preparing module
        self._insert_module_from_archive()

        # fetching v2 api
        self.http_client.fetch(self.get_url("/api/v2/modules"),
                               self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        bd = json.loads(response.body)
        self.assertTrue("version" in bd, bd)
        # check whether our module is in the list as well

        self.assertTrue('loaded_sys_versions' in bd['data'][0].keys(), bd)
        self.assertTrue('latest_code_version' in bd['data'][0].keys(), bd)
        self.assertTrue('source_raw' in bd['data'][0].keys(), bd)
        self.assertTrue('href' in bd['data'][0].keys(), bd)
        self.assertTrue('name' in bd['data'][0].keys(), bd)

    def test_module_deletion(self):
        """

        Tests API v2 module deletion functionality. First it inserts a module
        from a commands file (using API v1), then deletes it through the API v2.
        Third step is to call API v2 to list modules and check whether inserted module
        was deleted successfully.
        """
        # preparing module
        self._insert_module_from_archive()

        # deleting
        self.http_client.fetch(self.get_url("/api/v2/modules/objects/splitter"),
                               self.stop,
                               method="DELETE")
        response = self.wait()
        self.assertEqual(response.code, 200)
        # querying list to see whether it was deleted
        # fetching v2 api
        self.http_client.fetch(self.get_url("/api/v2/modules"),
                               self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        bd = json.loads(response.body)
        self.assertTrue("version" in bd, bd)
        # check whether our module is in the list as well
        self.assertFalse(
            {u'loaded_sys_versions': [u'localhost_splitter_v1'],
             u'latest_code_version': 1,
             u'href': u'/api/v2/modules/objects/splitter',
             u'name': u'splitter'} in bd['data'], bd)
