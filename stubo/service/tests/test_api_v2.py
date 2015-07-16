"""  
    :copyright: (c) 2015 by OpenCredo.
    :license: GPLv3, see LICENSE for more details.
"""

# -*- coding: utf-8 -*-
import json
from stubo.testing import Base
import logging

log = logging.getLogger(__name__)


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
        self.assertEqual(response.code, 400)
        self.assertEqual(response.reason, 'No JSON body found')

    def test_put_scenario_wrong_body(self):
        """

        Pass a JSON body to put scenario function although do not supply "scenario" key with name
        """
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios'), self.stop,
                               method="PUT", body='{"foo": "bar"}')
        response = self.wait()
        self.assertEqual(response.code, 400)
        self.assertEqual(response.reason, 'Scenario name not supplied')

    def test_put_duplicate_scenario(self):
        """

        Test duplicate insertion and error handling
        """
        response = self._test_insert_scenario()
        self.assertEqual(response.code, 201)
        # insert it second time
        response = self._test_insert_scenario()
        self.assertEqual(response.code, 422)
        self.assertTrue('already exists' in response.reason)

    def test_put_stub_name_none(self):
        """

        Test blank scenario name insertion
        """
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios'), self.stop,
                               method="PUT", body='{"scenario": "" }')
        response = self.wait()
        self.assertEqual(response.code, 400)
        self.assertTrue('name is blank or contains illegal characters' in response.reason)

    def test_put_stub_name_w_illegal_chars(self):
        """

        Test scenario name with illegal characters insertion
        """
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios'), self.stop,
                               method="PUT", body='{"scenario": "@foo" }')
        response = self.wait()
        self.assertEqual(response.code, 400)
        self.assertTrue('name is blank or contains illegal characters' in response.reason)
        self.assertTrue('@foo' in response.reason)

    def test_get_all_scenarios(self):

        # creating some scenarios
        for scenario_number in xrange(5):
            response = self._test_insert_scenario(name="scenario_name_with_no_%s" % scenario_number)
            self.assertEqual(response.code, 201)

        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios'), self.stop, method="GET")
        response = self.wait()
        payload = json.loads(response.body)
        self.assertTrue('scenarios' in payload)
        self.assertEqual(len(payload['scenarios']), 5)




