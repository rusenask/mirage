# -*- coding: utf-8 -*-
"""  
    :copyright: (c) 2015 by OpenCredo.
    :license: GPLv3, see LICENSE for more details.
"""
import sys
import logging
import datetime
import csv
from StringIO import StringIO
import re

from tornado.web import RequestHandler, asynchronous, gen
import tornado.ioloop
from plop.collector import Collector
import yappi
from tornado.util import ObjectDict

from stubo.service.handlers_mt import (
    export_stubs_request, list_stubs_request,
    command_handler_request, delay_policy_request,
    stub_count_request, begin_session_request, end_session_request,
    put_stub_request, get_response_request, delete_stubs_request,
    status_request, get_delay_policy_request,
    delete_delay_policy_request, put_module_request,
    delete_module_request, list_module_request, delete_modules_request,
    stats_request, analytics_request, put_setting_request, get_setting_request,
    end_sessions_request, list_scenarios_request
)
from stubo.utils.track import TrackRequest
from stubo import version
from stubo.exceptions import StuboException, exception_response

DummyModel = ObjectDict
from handlers_mt import rename_scenario

log = logging.getLogger(__name__)


class HandlerFactory(object):
    @classmethod
    def make(cls, handler_name):
        """Return the relevant handler class"""
        this_module = sys.modules[cls.__module__]
        return getattr(this_module, handler_name)


class BeginSessionHandler(TrackRequest):
    def get(self):
        self.post()

    def post(self):
        begin_session_request(self)


class EndSessionHandler(TrackRequest):
    def get(self):
        self.post()

    def post(self):
        end_session_request(self)


class EndSessionsHandler(TrackRequest):
    def get(self):
        self.post()

    def post(self):
        end_sessions_request(self)


class GetResponseHandler(TrackRequest):
    def post(self):
        get_response_request(self)

    def get(self):
        self.set_status(405)
        emsg = 'Not allowed to use HTTP GET for get/response, use POST instead.'
        response = dict(version=version, error=dict(code=404, message=emsg))
        self.write(response)
        self.track.stubo_response = response
        self.finish()


class DeleteStubsHandler(TrackRequest):
    def compute_etag(self):
        return None

    def get(self):
        self.post()

    def post(self):
        delete_stubs_request(self)


class PutStubHandler(TrackRequest):
    def get(self):
        self.set_status(405)
        emsg = 'Not allowed to use HTTP GET for put/stub, use POST instead.'
        response = dict(version=version, error=dict(code=404, message=emsg))
        self.write(response)
        self.track.stubo_response = response
        self.finish()

    def post(self):
        put_stub_request(self)


class PutModuleHandler(TrackRequest):
    def get(self):
        self.post()

    def post(self):
        put_module_request(self)


class DeleteModuleHandler(TrackRequest):
    """  Delete named user exit module 
    """

    def get(self):
        self.post()

    def post(self):
        delete_module_request(self)


class DeleteModulesHandler(TrackRequest):
    """ Delete all user exit modules 
    """

    def get(self):
        self.post()

    def post(self):
        delete_modules_request(self)


class GetModuleListHandler(TrackRequest):
    def get(self):
        self.post()

    def post(self):
        list_module_request(self)


class HomeHandler(RequestHandler):
    def get(self):
        response = self.render_string("home.html", page_title='Stub-O-Matic')
        self.write(response)
        self.set_header('x-stubo-version', version)
        self.finish()


class GetVersionHandler(TrackRequest):
    def get(self):
        response = {'version': self.settings['stubo_version']}
        self.write(response)
        self.track.stubo_response = response
        self.finish()

    def post(self):
        self.get()


class StuboCommandHandler(TrackRequest):
    def compute_etag(self):
        # override tornado default which will return a 304 (not modified)
        # if the response contents of a GET call with the same signature matches
        return None

    @tornado.gen.coroutine
    def get(self):
        stubo_response = dict(version=version)
        try:
            executor = self.settings['process_executor']
            cmd_file_url = self.get_argument('cmdfile', None)
            if not cmd_file_url:
                # LEGACY
                cmd_file_url = self.get_argument('cmdFile', None)
            if not cmd_file_url:
                raise exception_response(400,
                                         title="'cmdfile' parameter not supplied.")

            request = DummyModel(protocol=self.request.protocol,
                                 host=self.request.host,
                                 arguments=self.request.arguments)
            stubo_response = yield executor.submit(command_handler_request,
                                                   cmd_file_url,
                                                   request,
                                                   self.settings['static_path'])
        except StuboException, err:
            stubo_response['error'] = dict(code=err.code, message=err.title)
            if hasattr(err, 'traceback'):
                stubo_response['error']['traceback'] = err.traceback
            self.set_status(err.code)
        except Exception, e:
            status = self.get_status()
            if not status or status == 200:
                # if error has not been or set to ok set it to internal server error
                stubo_response['error'] = dict(code=500, message=str(e))
                self.set_status(500)
            else:
                stubo_response['error'] = dict(code=status, message=str(e))
            if hasattr(e, 'traceback'):
                stubo_response['error']['traceback'] = e.traceback

        self.write(stubo_response)
        self.set_header('x-stubo-version', version)
        self.finish()

    @tornado.gen.coroutine
    def post(self):
        stubo_response = dict(version=version)
        try:
            executor = self.settings['process_executor']
            cmd_file_url = self.get_argument('cmdfile', None)
            if not cmd_file_url:
                # LEGACY
                cmd_file_url = self.get_argument('cmdFile', None)
            if not cmd_file_url:
                raise exception_response(400,
                                         title="'cmdfile' parameter not supplied.")

            request = DummyModel(protocol=self.request.protocol,
                                 host=self.request.host,
                                 arguments=self.request.arguments)
            stubo_response = yield executor.submit(command_handler_request,
                                                   cmd_file_url,
                                                   request,
                                                   self.settings['static_path'])
        except StuboException, err:
            stubo_response['error'] = dict(code=err.code, message=err.title)
            if hasattr(err, 'traceback'):
                stubo_response['error']['traceback'] = err.traceback
            self.set_status(err.code)
        except Exception, e:
            status = self.get_status()
            if not status or status == 200:
                # if error has not been or set to ok set it to internal server error
                stubo_response['error'] = dict(code=500, message=str(e))
                self.set_status(500)
            else:
                stubo_response['error'] = dict(code=status, message=str(e))
            if hasattr(e, 'traceback'):
                stubo_response['error']['traceback'] = e.traceback

        self.write(stubo_response)
        self.set_header('x-stubo-version', version)
        self.finish()


class GetStubExportHandler(TrackRequest):
    def get(self):
        export_stubs_request(self)

    def post(self):
        self.get()


class GetStubListHandler(TrackRequest):
    def compute_etag(self):
        return None

    def get(self):
        list_stubs_request(self)

    def post(self):
        self.get()


class GetScenariosHandler(TrackRequest):
    def compute_etag(self):
        return None

    def get(self):
        list_scenarios_request(self)

    def post(self):
        self.get()


class PutScenarioHandler(TrackRequest):
    """
    /stubo/api/put/scenarios/(?P<scenario_name>[^\/]+)?new_name=some_new_name

    """

    def compute_etag(self):
        return None

    def get(self, scenario_name):
        new_scenario_name = RequestHandler.get_query_arguments(self, 'new_name')
        # checking whether scenario name and new scenario name values are supplied
        if new_scenario_name and scenario_name and new_scenario_name != ['']:
            if re.match(r'[\w-]*$', new_scenario_name[0]):
                rename_scenario(self, scenario_name=scenario_name, new_name=new_scenario_name[0])
            else:
                self.set_status(400, "Illegal characters supplied. Name provided: %s" % new_scenario_name[0])
        else:
            self.set_status(412, "Precondition failed: name not supplied")


class GetStubCountHandler(TrackRequest):
    def compute_etag(self):
        return None

    def get(self):
        stub_count_request(self)

    def post(self):
        self.get()


class GetStatsHandler(TrackRequest):
    def compute_etag(self):
        return None

    def get(self):
        stats_request(self)

    def post(self):
        self.get()


class PutDelayPolicyHandler(TrackRequest):
    def get(self):
        self.post()

    def post(self):
        delay_policy_request(self)


class PutSettingHandler(TrackRequest):
    def get(self):
        self.post()

    def post(self):
        put_setting_request(self)


class GetSettingHandler(RequestHandler):
    def get(self):
        self.post()

    def post(self):
        get_setting_request(self)


class GetDelayPolicyHandler(TrackRequest):
    def get(self):
        get_delay_policy_request(self)

    def post(self):
        self.get()


class DeleteDelayPolicyHandler(TrackRequest):
    def get(self):
        self.post()

    def post(self):
        delete_delay_policy_request(self)


class GetStatusHandler(RequestHandler):
    def compute_etag(self):
        return None

    def get(self):
        status_request(self)

    def post(self):
        self.get()


class AnalyticsHandler(RequestHandler):
    def get(self):
        analytics_request(self)


class ProfileHandler(RequestHandler):
    PROF_COLUMNS = (
        'name',
        'n',
        'tsub',
        'ttot',
        'tavg'
    )

    def __init__(self, application, request, **kwargs):
        super(ProfileHandler, self).__init__(application, request, **kwargs)
        self.interval = 60
        self.limit = 100

    @asynchronous
    def get(self):
        self.interval = int(self.get_argument('interval', self.interval))
        self.sort_type = yappi.SORT_TYPES_FUNCSTATS[self.get_argument(
            'sort_type', 'tsub')]
        self.limit = self.get_argument('limit', self.limit)
        yappi.start()
        tornado.ioloop.IOLoop.instance().add_timeout(
            datetime.timedelta(seconds=self.interval), self.finish_profile)

    def finish_profile(self):
        msg = 'stop profile using interval={0}'.format(self.interval)
        log.debug(msg)
        fd = StringIO()
        out_csv = csv.DictWriter(fd, self.PROF_COLUMNS)
        out_csv.writerow(dict([(name, name) for name in self.PROF_COLUMNS]))
        stats = yappi.get_func_stats()
        for row in stats:
            out_csv.writerow(dict(name=str(row[0]), n=str(row[1]),
                                  tsub=str(row[2]), ttot=str(row[3]),
                                  tavg=str(row[4])))
        yappi.stop()
        yappi.clear_stats()

        # save the file
        fd.seek(0)
        now = datetime.datetime.utcnow()
        report_name = 'prof-report-%s.csv' % (now.strftime('%y%m%d.%H%M'))
        body = fd.getvalue()
        self.write(body)
        self.set_header('Content-type', 'text/csv')
        self.set_header('Content-disposition',
                        'attachment;filename=%s' % report_name)
        self.finish()


class PlopProfileHandler(RequestHandler):
    def __init__(self, application, request, **kwargs):
        super(PlopProfileHandler, self).__init__(application, request, **kwargs)
        self.interval = 60
        self.output = '/tmp/plop.out'
        self.collector = Collector()

    @asynchronous
    def get(self):
        self.interval = int(self.get_argument('interval', self.interval))
        self.output = self.get_argument('output', self.output)
        self.collector.start()
        tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(
            seconds=self.interval), self.finish_profile)

    def finish_profile(self):
        log.debug('stop profile using interval={0} and output={1}'.format(
            self.interval, self.output))
        self.collector.stop()
        with open(self.output, 'w') as f:
            stats = repr(dict(self.collector.stack_counts))
            f.write(stats)
        self.finish(stats)


"""
Manage Handlers
"""


class ManageScenariosHandler(RequestHandler):
    """
    /manage/scenarios

    """

    def get(self):
        self.render('manageScenarios.html')


class ManageScenarioDetailsHandler(RequestHandler):
    """
    /manage/scenarios/details?scenario=<href to scenario>

    """

    def get(self):
        self.render('manageScenarioDetails.html')


class ManageScenarioExportHandler(RequestHandler):
    """
   /manage/scenarios/export?scenario=<href to scenario>

   """

    def get(self):
        self.render('manageExportScenario.html')


class ManageDelayPoliciesHandler(RequestHandler):
    def get(self):
        self.render('manageDelayPolicies.html')


class ManageCommandsHandler(RequestHandler):
    def get(self):
        self.render('manageCommands.html')


class ManageModulesHandler(RequestHandler):
    def get(self):
        self.render('manageModules.html')


"""
Tracker Handlers
"""


class TrackerHandler(RequestHandler):
    def get(self):
        self.render('trackerRecords.html')


class TrackerDetailsHandler(RequestHandler):
    def get(self):
        self.render('trackerRecordDetails.html')


"""
-------------------------------------------------------------------
------------------ below are handlers for API v2 ------------------
-------------------------------------------------------------------

"""
import json
from stubo.utils import get_hostname
from tornado import websocket
from pymongo.errors import DuplicateKeyError
from stubo.model.db import Tracker
from bson import ObjectId
import pymongo
from stubo.model.db import Scenario
from stubo.model.db import motor_driver
from stubo.service.handlers_mt import stubo_async
from stubo.cache import Cache
from stubo.service.api_v2 import begin_session as api_v2_begin_session
from stubo.service.api_v2 import update_delay_policy as api_v2_update_delay_policy
from stubo.service.api_v2 import get_delay_policy as api_v2_get_delay_policy
from stubo.service.api_v2 import end_sessions as api_v2_end_all_sessions
from stubo.service.api_v2 import end_session as api_v2_end_session
from stubo.service.api_v2 import MagicFiltering

from stubo.utils.command_queue import InternalCommandQueue
from stubo.service.api import delete_module

from stubo.service.api import delete_delay_policy, put_stub, get_response
from stubo.utils.track import BaseHandler
from stubo.utils import asbool
from stubo.model.exporter import Exporter
from stubo.model.export_commands import export_stubs_to_commands_format, get_export_links
from stubo.model.exporter import YAML_FORMAT_SUBDIR
from stubo.service.api import run_command_file, run_commands
import zipfile
from stubo.utils import make_temp_dir
import os
import yaml
from stubo.model.stub import Stub

NOT_ALLOWED_MSG = 'Method not allowed'


class BaseScenarioHandler(RequestHandler):
    """
    /api/v2/scenarios
    """

    def initialize(self):
        """

        Initializing database and setting header. Using global tornado settings that are generated
        during startup to acquire database client
        """
        # setting header
        self.set_header('x-stub-o-matic-version', version)
        self.db = motor_driver(self.settings)

    def compute_etag(self):
        return None

    @gen.coroutine
    def get(self):
        """
        Gets all scenarios from the database. Response contains names and paths to resources

        {
            scenarios:
              {
                scenarioRef: "/api/v2/scenarios/objects/127.0.0.1:scenario_0001"
                name: "127.0.0.1:scenario_0001"
                },
                {
                scenarioRef: "/api/v2/scenarios/objects/localhost:scenario_1"
                name: "localhost:scenario_1"
                },
                {
                scenarioRef: "/api/v2/scenarios/objects/localhost:scenario_10"
                name: "localhost:scenario_10"
                },
                ..
                ..
              }
        }

        """

        if len(self.request.body) > 0:
            self.send_error(status_code=405, reason="Trying to create scenario? Use PUT method instead.")
        else:
            # getting all scenarios
            cursor = self.db.scenario.find()
            # sorting based on name
            cursor.sort([('name', pymongo.ASCENDING)])
            scenarios = []
            result_dict = {}
            while (yield cursor.fetch_next):
                document = cursor.next_object()
                try:
                    scenarios.append({'name': document['name'],
                                      'scenarioRef': '/api/v2/scenarios/objects/%s' % document['name']})
                except KeyError:
                    log.warn('Scenario name not found for object: %s' % document['_id'])
            result_dict['data'] = scenarios
            self.write(result_dict)

    def put(self):
        """
        Call example:
        curl -i -H "Content-Type: application/json" -X PUT -d '{"scenario":"scenario_0001"}'
                                                                         http://127.0.0.1:8001/api/v2/scenarios

        Creates a scenario and returns a link to it: query example:
        { “scenario”: “scenario_name” }
        :return:  returns a JSON response that contains information about created object,
        example success (201 response code):
        {"scenarioRef": "/api/v2/scenarios/objects/127.0.0.1:scenario_0001",
         "name": "127.0.0.1:scenario_0001"}

        example duplicate error (422 response code):
        <html>
            <title>
                 422: Scenario (127.0.0.1:scenario_0001) already exists.
            </title>
            <body>
                 422: Scenario (127.0.0.1:scenario_0001) already exists.
            </body>
        </html>
        """

        body_dict = None
        # get body
        try:
            body_dict = json.loads(self.request.body)
        except ValueError as ex:
            log.debug(ex)
            self.send_error(status_code=415, reason="No JSON body found")
        except Exception as ex:
            log.debug(ex)
            self.send_error(status_code=415, reason="Failed to get JSON body: %s" % ex.message)

        # check if scenario name is supplied
        full_name = None

        if body_dict:
            if 'scenario' not in body_dict:
                self.send_error(status_code=400,
                                reason="Scenario name not supplied")
            # check if scenario contains illegal characters or is blank
            else:
                name = body_dict['scenario']
                # check if hostname is provided
                if ":" in name:
                    scenario_name = name.split(':')[1]
                    if re.match(r'[\w-]*$', scenario_name) and scenario_name != "":
                        full_name = name
                # check if name is not empty string and only allowed characters are in this string
                elif name != "":
                    if re.match(r'[\w-]*$', name):
                        # form a full name
                        host = get_hostname(self.request)
                        full_name = '%s:%s' % (host, name)

                # if full name is validated and formed
                if full_name is not None:
                    self.insert_scenario(full_name)
                else:
                    self.send_error(status_code=400,
                                    reason="Scenario name is blank or contains illegal characters. Name supplied: %s"
                                           % body_dict['scenario'])

    @tornado.web.asynchronous
    @gen.coroutine
    def insert_scenario(self, name):

        scenario_document = {'name': name}
        try:
            # inserting scenario document, adding index and unique constraint
            yield self.db.scenario.insert(scenario_document)
            self.db.scenario.create_index('name', unique=True)
            # creating result dict
            result_dict = {'name': name,
                           'scenarioRef': '/api/v2/scenarios/objects/{0}'.format(name)}
            self.set_status(201)
            self.write(result_dict)
        except DuplicateKeyError as ex:
            log.debug(ex)
            self.send_error(status_code=422,
                            reason="Scenario (%s) already exists." % name)
        except Exception as ex:
            log.warn(ex)
            self.send_error(status_code=400,
                            reason="Failed to create scenario resource. Exception: %s" % ex.message)


class GetAllScenariosHandler(RequestHandler):
    """
    /api/v2/scenarios/detail

    """

    def initialize(self):
        """

        Initializing database and setting header. Using global tornado settings that are generated
        during startup to acquire database client
        """
        # setting header
        self.set_header('x-stub-o-matic-version', version)
        # get motor driver
        self.db = motor_driver(self.settings)

    def compute_etag(self):
        return None

    @gen.coroutine
    def get(self):
        """

        Returns a list with all scenarios (and URL paths to these resources),
        stub count
        """
        all_hosts = asbool(self.get_argument("all-hosts", True))

        # getting scenarios for the current host
        if not all_hosts:
            current_host = get_hostname(self.request)
            query = {'name': {'$regex': current_host + '.*'}}
            cursor = self.db.scenario.find(query)
        else:
            # getting all scenarios
            cursor = self.db.scenario.find()

        # # getting all scenarios
        # cursor = self.db.scenario.find()
        # sorting based on name
        cursor.sort([('name', pymongo.ASCENDING)])

        # get size
        scenario_cl = Scenario()
        scenarios_sizes = scenario_cl.size()
        scenarios_recorded = scenario_cl.recorded()
        scenarios_stub_counts = scenario_cl.stub_counts()

        # start mapping data
        scenarios = []
        result_dict = {}
        while (yield cursor.fetch_next):
            document = cursor.next_object()
            try:
                # getting information about recorded, sizes and stub counts
                scenario_recorded = scenarios_recorded.get(document['name'], '-')
                scenario_size = int(scenarios_sizes.get(document['name'], 0))
                scenario_stub_count = scenarios_stub_counts.get(document['name'], 0)
                scenario_name = document['name']
                host, scenario = scenario_name.split(':')
                # getting session data
                sessions = []
                cache = Cache(host)
                for session_info in cache.get_scenario_sessions_information(scenario):
                    sessions.append(session_info)

                scenarios.append({'name': scenario_name,
                                  'recorded': scenario_recorded,
                                  'space_used_kb': scenario_size,
                                  'stub_count': scenario_stub_count,
                                  'sessions': sessions,
                                  'scenarioRef': '/api/v2/scenarios/objects/%s' % document['name']})
            except KeyError:
                log.warn('Scenario name not found for object: %s' % document['_id'])
        result_dict['data'] = scenarios
        self.set_status(200)
        self.write(result_dict)

    def post(self):
        self.clear()
        self.send_error(status_code=405, reason=NOT_ALLOWED_MSG)


class GetScenarioDetailsHandler(RequestHandler):
    """
    /api/v2/scenarios/objects/(?P<scenario_name>[^\/]+)

    """

    def initialize(self):
        """

        Initializing database and setting header. Using global tornado settings that are generated
        during startup to acquire database client
        """
        # setting header
        self.set_header('x-stub-o-matic-version', version)
        # get motor driver
        self.db = motor_driver(self.settings)

    def compute_etag(self):
        return None

    @gen.coroutine
    def get(self, scenario_name):
        """

        Returns scenario name, current sessions and their states,
        stub count, total, document size. Also, provides direct URL link to stub list.
        :param scenario_name: <string> scenario name

        Response JSON:
        {
            "stubs": 32,
             "space_used_kb": 840,
             "recorded": "2015-07-15",
             "name": "localhost:scenario_16",
             "scenarioRef": "/api/v2/scenarios/objects/localhost:scenario_16"
         }
        """

        # check if hostname is supplied - if not, override scenario name with new value
        scenario_name = _get_scenario_full_name(self, scenario_name)
        # query MongoDB
        document = yield self.db.scenario.find_one({'name': scenario_name})

        # form a result dictionary
        if document is not None:
            # get stub count
            stub_count = yield self.db.scenario_stub.find({'scenario': scenario_name}).count()
            # get size
            scenario_cl = Scenario()
            size = scenario_cl.size(scenario_name)
            # check if size is None
            if size is None:
                size = 0
            recorded = scenario_cl.recorded(scenario_name)
            if recorded is None:
                recorded = '-'

            host, scenario = scenario_name.split(':')
            # getting session data
            sessions = []
            cache = Cache(host)
            for session_info in cache.get_scenario_sessions_information(scenario):
                sessions.append(session_info)

            result_dict = {'name': scenario_name,
                           'stub_count': stub_count,
                           'recorded': recorded,
                           'space_used_kb': int(size),
                           'scenarioRef': '/api/v2/scenarios/objects/{0}'.format(scenario_name),
                           'sessions': sessions}
            self.set_status(200)
            self.write(result_dict)
        else:
            self.send_error(404)

    @gen.coroutine
    def delete(self, scenario_name):
        """

        Deletes scenario object from database. Fails if there are existing stubs
        in the database
        :param scenario_name: <string> scenario name
        """
        scenario_name = _get_scenario_full_name(self, scenario_name)

        query = {'name': scenario_name}
        # query MongoDB
        document = yield self.db.scenario.find_one(query)

        if document is not None:

            # scenario name contains host, splitting it and using this value to clear cache
            host, name = scenario_name.split(":")
            cache = Cache(host)

            active_sessions = cache.get_active_sessions(name, local=False)
            if active_sessions:
                self.send_error(422, reason='Sessons in playback/record, can not delete. '
                                            'Found the following active sessions: {0} '
                                            'for scenario: {1}'.format(active_sessions, name))
                return
            # no active sessions found, deleting everything
            try:
                # delete document
                yield self.db.scenario.remove(query)
                # deleting stubs and pre stubs
                yield self.db.scenario_stub.remove({"scenario": scenario_name})
                yield self.db.pre_scenario_stub.remove({"scenario": scenario_name})
            except Exception as ex:
                log.error("Failed to delete scenario %s/stubs from database. Got error: %s" % (scenario_name, ex))
            try:
                # delete cache
                cache.delete_caches(name)
                log.debug("scenario and stubs removed")
            except Exception as ex:
                log.warn("Failed to delete caches for scenario: %s. Got error: %s" % (scenario_name, ex))

            self.set_status(200)
        else:
            self.send_error(412, reason="Precondition failed - scenario (%s) does not exist." % scenario_name)



class ScenarioActionHandler(TrackRequest):
    """
    /api/v2/scenarios/objects/(?P<scenario_name>[^\/]+)/action
    """

    def initialize(self):
        """
        Setting version header
        """

    def compute_etag(self):
        return None

    def get(self, scenario_name):
        self.clear()
        self.send_error(status_code=405, reason=NOT_ALLOWED_MSG)

    def post(self, scenario_name):
        """

        Launches actions such as export, begin session, end session. Examples:
        body parameter:
        { “export”: null }
        You can also add these optional parameters during export to override defaults:
        { “session”: “session_name”,
         “export_dir”: “export_dir_name”,
         “runnable”: true,
         “playback_session”: “session_to_use(required when runnable)”}

        Begin session:
        { "begin": null, "session": "session_name", "mode": "record" }

        End session:
        { “end”: null,
          “session”: “session_name” }

        End all sessions:
        { “end”: “sessions” }


        """
        # get body
        try:
            # checking request body
            body_dict = json.loads(self.request.body)
        except ValueError as ex:
            log.debug(ex)
            self.send_error(status_code=415, reason="No JSON body found")
            return
        except Exception as ex:
            log.debug(ex)
            self.send_error(status_code=415, reason="Failed to get JSON body: %s" % ex.message)
            return

        if body_dict:
            self.scenario_name = scenario_name

            # setting scenario name for tracking
            self.track.scenario = scenario_name

            # begin session
            if 'begin' in body_dict:
                # getting variables
                self.session_name = body_dict.get('session', None)
                self.mode = body_dict.get('mode', None)

                # Check whether session name and mode variables supplied
                if not (self.session_name and self.mode):
                    self.send_error(412, reason="Precondition failed, session name or mode is missing.")
                else:
                    self._begin_session()

            # end session
            elif 'end' in body_dict:

                if body_dict['end'] == "sessions":
                    # ending all sessions
                    self._end_all_sessions()
                elif 'session' in body_dict:
                    # ending session
                    self.session_name = body_dict['session']
                    self._end_session()
                else:
                    self.send_error(status_code=400, reason="Can't determine which session to end.")

            # export scenario
            elif 'export' in body_dict:
                self._export_scenario(body_dict)

            else:
                self.send_error(status_code=400)
        else:
            self.send_error(status_code=400)

    @stubo_async
    def _begin_session(self):
        """

        Begins session
        :raise exception_response:

        Example output:
        Record new session
        {
         "version": "0.6.3",
         "data":
            {"status": "record",
            "scenario": "localhost:scenario_rest_api",
            "scenarioRef": "/api/v2/scenarios/objects/localhost:scenario_rest_api",
            "scenario_id": "55acba53fc456205eaf7e258",
            "session": "new_session_rest2",
            "message": "Record mode initiated...."}
        }
        """
        warm_cache = asbool(self.get_argument('warm_cache', False))
        if not self.mode:
            raise exception_response(400,
                                     title="'mode' of playback or record required")
        # passing parameters to api v2 handler, it avoids creating scenario if there is an existing one,
        # since all scenarios should be existing!
        response = api_v2_begin_session(self, self.scenario_name,
                                        self.session_name,
                                        self.mode,
                                        self.get_argument('system_date', None),
                                        warm_cache)
        # adding scenarioRef key for easier resource access.
        response['data']['scenarioRef'] = '/api/v2/scenarios/objects/%s' % response['data']['scenario']
        self.write(response)

    def _end_all_sessions(self):
        """
        {
         "version": "0.6.3",
         "data": {
             "session_name_5": {
                 "message": "Session ended"
                 },
             "session_name_4": {
                 "message": "Session ended"
                 },
             "session_name_6": {
                 "message": "Session ended"
                 }
                 }
        }
        :return:
        """
        try:
            # need to pass scenario name without hostname
            # if ":" in self.scenario_name:
            #     scenario_name = self.scenario_name.split(":")[1]
            # else:
            #     scenario_name = self.scenario_name
            response = api_v2_end_all_sessions(self, self.scenario_name)
            self.write(response)
        except Exception as ex:
            log.warn("Failed to end all sessions for scenario: %s. Got error: %s" % (self.scenario_name, ex))

    def _end_session(self):
        """

        Ends session

        Example output:
        {
         "version": "0.6.3",
         "data": {
             "message": "Session ended"
             }
        }
        """
        try:
            if ":" not in self.scenario_name:
                hostname = get_hostname(self.request)
            else:
                # removing hostname from scenario name
                hostname = self.scenario_name.split(":")[0]
            response = api_v2_end_session(hostname, self.session_name)
            self.write(response)
        except Exception as ex:
            log.warn("Failed to end session %s for scenario: %s. Got error: %s" % (self.session_name,
                                                                                   self.scenario_name,
                                                                                   ex))

    @stubo_async
    def _export_scenario(self, body_dict):
        """
        Standard export functionality example request:
        {
          "export": null
        }
        Example response:
        {
            "version": "0.6.6", "data": {
                "yaml_links": [
                    ["scenario_1_1443437153_0.json", "http:/host:port/static/exports/localhost_scenario_1/yaml_format/
                                                      scenario_1_1443437153_0.json?v=c0edf1d9ded15b97c6d083d2128b9945"],
                        ...
                ],
                "command_links": [
                    ["scenario_1_1443437153_0.response", "http://host:port/static/exports/localhost_scenario_1/
                                                  scenario_1_1443437153_0.response?v=55c4a49780ed085e7a5f9176e90aef60"],
                ...
                ],
                "scenario": "scenario_1",
                "export_dir_path": "/Users/karolisrusenas/IdeaProjects/mirage/stubo/static/exports/localhost_scenario_1/
                                    yaml_format"
            }
        }

        Example export runnable scenario request body:
        {
          "export": null,
          "runnable": true,
          "playback_session": "response_play"
        }

        All optional parameters:
        Optional:
        {
             “session”: “session_name(if None - will default to current time”,
             “export_dir”: “export_dir_name”,
             “runnable”: true,
             “playback_session”: “session_to_use(required when runnable)”
         }

        In addition to usual export links to files there will be created another object (runnable):
        ...
        runnable: {
            last_used: {
                    start_time: "2015-09-25 17:12:03.133000+00:00"
                    remote_ip: "::1"
                }
            playback_session: "response_play"
            number_of_playback_requests: 1
            }
        ...

        """
        # checking whether scenario name was supplied
        if ':' in self.scenario_name:
            scenario_name_key = self.scenario_name
            _, self.scenario_name = self.scenario_name.split(':')
        else:
            scenario_name_key = _get_scenario_full_name(self, self.scenario_name)

        static_dir = self.settings['static_path']

        exporter = Exporter(static_dir=static_dir)
        runnable = body_dict.get('runnable', False)
        playback_session = body_dict.get('playback_session', None)
        session = body_dict.get('session', None)
        export_dir = body_dict.get('export_dir', None)

        # exporting to commands format
        command_links = export_stubs_to_commands_format(handler=self,
                                                        scenario_name_key=scenario_name_key,
                                                        scenario_name=self.scenario_name,
                                                        session_id=session,
                                                        runnable=runnable,
                                                        playback_session=playback_session,
                                                        static_dir=static_dir,
                                                        export_dir=export_dir)

        # doing the export
        export_dir_path, files, runnable_info = exporter.export(scenario_name_key,
                                                                runnable=runnable,
                                                                playback_session=playback_session,
                                                                session_id=session,
                                                                export_dir=export_dir)

        # getting export links
        yaml_links = get_export_links(self, scenario_name_key + "/" + YAML_FORMAT_SUBDIR, files)

        payload = dict(scenario=self.scenario_name, export_dir_path=export_dir_path,
                       command_links=command_links, yaml_links=yaml_links)
        if runnable_info:
            payload['runnable'] = runnable_info
        return dict(version=version, data=payload)


class CreateDelayPolicyHandler(BaseHandler):
    """
    /api/v2/delay-policy
    """

    def compute_etag(self):
        return None

    def put(self):
        """

        Creates a delay policy. Examples:
        { “name”: “delay_name”,
          “delay_type”: “fixed”,
          “milliseconds”: 50}
        or
        { “name”: “delay_name”,
          “delay_type”: “normalvariate”,
          “mean”: “mean_val”,
          “stddev”: “val”}
        or
        { "name": "weighted_delay_name",
         "delay_type": "weighted",
         "delays": "fixed,30000,5:normalvariate,5000,1000,15:normalvariate,1000,500,70"}

        Returns 201 status code if successful or 409 if request body options
        are wrong (type fixed provided with mean and stddev options)
        """
        # loading json arguments and making them available in self.request.arguments
        self.load_json()

        # delay parameters are now stored in BaseHandler, passing them to update function
        response = api_v2_update_delay_policy(self)

        self.set_status(response['status_code'])

        self.write(response)


class GetAllDelayPoliciesHandler(RequestHandler):
    """
    /api/v2/delay-policy/detail
    """

    def compute_etag(self):
        return None

    def get(self):
        """

        Returns a list with all delay policies (and URL paths to these resources),
        stub count

        Example output:
        {"version": "0.6.4",
        "data":
            {"my_delay":
                {"delay_type": "fixed",
                "name": "my_delay",
                "delayPolicyRef": "/api/v2/delay-policy/objects/my_delay",
                "milliseconds": 50},
            "pcent_random_samples":
                {"delay_type": "weighted",
                "delays": "fixed,30000,5:normalvariate,5000,1000,15:normalvariate,1000,500,70",
                "name": "pcent_random_samples",
                "delayPolicyRef": "/api/v2/delay-policy/objects/pcent_random_samples"},
            "delay_1":
                 {"delay_type": "fixed",
                  "name": "delay_1",
                  "delayPolicyRef": "/api/v2/delay-policy/objects/delay_1",
                  "milliseconds": "0"}
            }
        }
        """
        response, status_code = api_v2_get_delay_policy(self, None, "main")
        self.set_status(status_code)
        self.write(response)


class GetDelayPolicyDetailsHandler(RequestHandler):
    """
    /api/v2/delay-policy/objects/(?P<delay_policy_name>[^\/]+)

    """

    def compute_etag(self):
        return None

    def get(self, delay_policy_name):
        """

        Returns delay policy name and all details about his resource
        :param delay_policy_name: <string> delay policy name
        """
        response, status_code = api_v2_get_delay_policy(self, delay_policy_name, "main")
        self.set_status(status_code)
        self.write(response)

    def delete(self, delay_policy_name):
        """

        Deletes delay policy object from database
        :param delay_policy_name: <string> delay policy name
        """
        response = delete_delay_policy(self, [delay_policy_name])
        self.write(response)


class GetStuboAPIversion(RequestHandler):
    """

    """

    def compute_etag(self):
        return None

    def get(self):
        self.write({'Mirage version': version,
                    'API version': 'v2'})


class StubHandler(TrackRequest):
    """
    /api/v2/scenarios/objects/(?P<scenario_name>[^\/]+)/stubs

    """

    def initialize(self):
        """

        Initializing database and setting header. Using global tornado settings that are generated
        during startup to acquire database client
        """
        # get motor driver
        self.db = motor_driver(self.settings)

    def compute_etag(self):
        return None

    @gen.coroutine
    def get(self, scenario_name):
        """
        Gets all stubs for specified scenario. Returns raw documents, although skips Mongo specific ObjectID fields
        :param scenario_name:
        """
        stubs = []
        response = {
            'version': version
        }
        # checking for supplied headers
        host = None
        if 'target_host' in self.request.headers:
            host = self.request.headers['target_host']
        # getting full scenario database
        scenario_name = _get_scenario_full_name(self, scenario_name, host)

        # getting all stubs for selected scenario, skipping object ID field
        cursor = self.db.scenario_stub.find({'scenario': scenario_name}, {'_id': False})

        while (yield cursor.fetch_next):
            document = cursor.next_object()
            try:
                stubs.append(document)
            except KeyError:
                log.warn('Stub could not be added to result list: %s' % document['_id'])
        response['data'] = stubs
        self.write(response)

    @gen.coroutine
    def delete(self, scenario_name):
        """
        Deletes specified scenario. If force is not supplied - checks for active sessions and if there are any - stops
        deletion. If force is supplied or there are no active sessions - deletes all stubs for scenario
        :param scenario_name:
        :return:
        """
        response = {
            'version': version
        }
        # checking for supplied headers
        host = None
        force = False
        if 'target_host' in self.request.headers:
            host = self.request.headers['target_host']

        if 'force' in self.request.headers:
            force = asbool(self.request.headers['force'])

        # getting full scenario database
        scenario_name = _get_scenario_full_name(self, scenario_name, host)

        host, scenario = scenario_name.split(':')
        cache = Cache(host)
        # if force is False or absent - checking for active sessions and if there are any - aborting deletion
        if not force:
            active_sessions = cache.get_active_sessions(scenario,
                                                        local=False)
            if active_sessions:
                self.set_status(409)
                error = 'Sessons in playback/record, can not delete. Found the ' \
                        'following active sessions: {0} for scenario: {1}'.format(active_sessions, scenario_name)
                response['error'] = error
                self.write(response)
                return
        # asynchronous deletion of stubs, returns two params - "ok" and "n" (deleted items count)
        result = yield self.db.scenario_stub.remove({'scenario': scenario_name})
        # deleting scenario from cache
        cache.delete_caches(scenario)
        response['data'] = "Deleted stubs count: %s" % result['n']
        self.write(response)

    @stubo_async
    def put(self, scenario_name):
        """
        Inserts stub into selected scenario

        Example request headers:
        session: session_test

        Example request JSON body:
         {
             "request": {
                 "method": "POST",
                 "bodyPatterns": [
                     { "contains": ["<status>IS_OK2</status>"] }
                 ]
                 },
             "response": {
                 "status": 200,
                 "body": "<response>YES</response>"
             }
         }
         Example output:
         {
            version: "0.6.6"
            data: {
            message: "updated with stateful response"
            }-
         }
         or:
         {
            version: "0.6.6"
            data: {
            message: "inserted scenario_stub: 55d5e7ebfc4562fb398dc697"
         }-

         After new stub insertion - it returns stub's ID in database
        """
        session = self.request.headers.get('session', None)
        delay_policy = self.request.headers.get('delay_policy', None)
        stateful = asbool(self.request.headers.get('stateful', True))
        recorded = self.request.headers.get('stub_created_date', None)
        module_name = self.request.headers.get('ext_module', None)

        recorded_module_system_date = self.request.headers.get('stubbedSystemDate', None)
        priority = int(self.request.headers.get('priority', -1))

        response = put_stub(self, session, delay_policy=delay_policy,
                            stateful=stateful, priority=priority, recorded=recorded,
                            module_name=module_name,
                            recorded_module_system_date=recorded_module_system_date)
        # adding status code based on response
        status = response['data']['message']['status']
        if status == 'created':
            self.set_status(201)

        elif status == 'updated':
            self.set_status(200)

        elif status == 'ignored':
            # this status code could be changed
            self.set_status(200)

        return response

    @stubo_async
    def post(self, scenario_name):
        """
        Gets response for specified "response contains" data. Equivalent to:
        http://stubo-app.readthedocs.org/en/latest/pages/api.html#get-response

        Example:
        Insert stub via PUT call:

         {
             "request": {
                 "method": "POST",
                 "bodyPatterns": [
                     { "contains": ["<status>IS_OK</status>"] }
                 ]
                 },
             "response": {
                 "status": 200,
                 "body": "<response>YES</response>"
             }
         }


        after having your stub inserted just use POST calls:
        header:
            session: session_test
        body:
            data: <status>IS_OK</status>

        Example response:
            <response>YES</response>



        :param scenario_name: string - should be used to speed up stub search
        :return: :raise exception_response:
        """
        session_name = self.request.headers.get('session', None)
        if session_name is None:
            session_name = self.request.headers.get('Stubo-Request-Session', None)

        if not session_name:
            raise exception_response(400, title="Session name not found in headers.")

        request = self.request
        self.track.function = 'get/response'
        log.debug('Found session: {0}, for route: {1}'.format(session_name,
                                                              request.path))
        return get_response(self, session_name)

from stubo.service.api_v2 import get_response_v2

class ScenarioStubMatcher(TrackRequest):
    """
    /api/v2/matcher
    """

    def initialize(self):
        """
        Initializing database. Using global tornado settings that are generated
        during startup to acquire database client
        """
        # get motor driver
        self.db = motor_driver(self.settings)

    def compute_etag(self):
        return None

    def post(self):
        scenario_session = self.request.headers.get('session', None)
        slices = scenario_session.split(":")
        if len(slices) < 2:
            self.set_status(400, reason="Session or scenario not provided, use format: 'scenario_name:session_name'")
        scenario_name = slices[0]
        session_name = slices[1]

        full_scenario_name = _get_scenario_full_name(self, scenario_name)
        self.track.function = 'get/response'

        data = get_response_v2(self, full_scenario_name, session_name)
        self.write(data)


class ScenarioUploadHandler(BaseHandler):

    def initialize(self):
        """

        Initializing database and setting header. Using global tornado settings that are generated
        during startup to acquire database client
        """
        # get motor driver
        self.db = motor_driver(self.settings)

    @gen.coroutine
    def post(self):
        # process file
        for _, content in self.request.files.iteritems():
            # content contains a list with a single element (file)
            content = content[0]
            import_dir = os.path.join(self.application.settings['static_path'], 'imports')
            # currently only zip supported
            if content['content_type'] == 'application/zip':
                with make_temp_dir(dirname=import_dir) as temp_dir:
                    with zipfile.ZipFile(StringIO(content['body'])) as zipf:
                        zipf.extractall(path=temp_dir)
                        yield self._process_config(temp_dir, zipf.namelist())
            else:
                self.send_error(415, reason="Content type not supported. Accepted format: .zip")

    @gen.coroutine
    def _process_config(self, tmp_dir, files):
        """

        Processing extracted configuration - searching for yaml file.
        :param tmp_dir: temporary directory with extracted stubs
        :param files: list of files to process
        """
        # getting config file, usually .yaml is in the end of the list
        session = "default_session"
        scenario = "default_scenario"
        stub_list = []
        found = False

        for f in reversed(files):
            # collecting stub files
            if f.endswith(".json"):
                stub_list.append(f)

            # looking for configuration file
            if f.endswith(".yaml"):
                # reading yaml file
                with open(tmp_dir + "/" + f, 'r') as stream:
                    found = True
                    try:
                        config = yaml.load(stream)
                        session = config['recording'].get('session', session)
                        scenario = config['recording'].get('scenario', scenario)
                    except Exception as ex:
                        self.send_error(400, reason="Configuration file found, however, "
                                                    "failed to read it. Got error: %s" % ex)
        if found:
            yield self._process_stubs(tmp_dir, scenario, session, stub_list)
        else:
            self.send_error(400, reason="Configuration file not found.")

    @gen.coroutine
    def _process_stubs(self, tmp_dir, scenario, session, stub_list):
        """

        Creates scenario, imports stubs and puts a session into playback mode.
        :param tmp_dir: directory where all the stub json files are stored
        :param scenario: scenario name
        :param session:  session name
        :param stub_list: a list of file names for this import
        :return:
        """
        # creating scenario
        try:
            yield self.db.scenario.insert({'name': _get_scenario_full_name(self, scenario)})
        except DuplicateKeyError as ex:
            log.debug(ex)
            self.send_error(status_code=422,
                            reason="Scenario (%s) already exists." % scenario)
            return

        # creating session, currently using current hostname
        cache = Cache(get_hostname(self.request))
        try:
            cache.assert_valid_session(scenario, session)
        except Exception as ex:
            self.send_error(status_code=400,
                            reason=ex)
            return
        scenario_name_key = cache.scenario_key_name(scenario)

        # prepare stub payload
        scenario_collection = Scenario()

        # status list
        status = []

        for stub in stub_list:
            full_file_name = tmp_dir + "/" + stub
            try:
                with open(full_file_name) as data_file:
                    data = json.load(data_file)
                    stub_obj = Stub(data, scenario_name_key)
                    doc = {
                        'stub': stub_obj,
                        'scenario': scenario_name_key
                    }
                    # inserting prepared document into the database
                    yield self.db.scenario_stub.insert(scenario_collection.get_stub_document(doc))
            except Exception as ex:
                msg = "Failed to process request/response %s. Got error: %s" % (stub['file'], ex)
                log.warn(msg)
                status.append(msg)

        # if there are any stubs - creating a session
        if stub_list:
            try:
                cache.create_session_cache(scenario, session)
            except Exception as ex:
                msg = "Failed to begin session for scenario %s, session %s. Got error: %s" % (scenario, session, ex)
                log.warn(msg)
                status.append(msg)

        result = {
            "scenario": scenario,
            "session": session,
            "total": len(stub_list),
        }
        if status:
            result["status"] = status
        self.set_status(200)
        self.write(result)

class TrackerRecordsHandler(BaseHandler):
    """
    /api/v2/tracker/records
    """

    def initialize(self):
        """

        Initializing database and setting header. Using global tornado settings that are generated
        during startup to acquire database client
        """
        # setting header
        self.set_header('x-stub-o-matic-version', version)
        # get motor driver
        self.db = motor_driver(self.settings)

    def compute_etag(self):
        return None

    @gen.coroutine
    def get(self):
        # getting pagination info
        skip = int(self.get_argument('skip', 0))
        limit = int(self.get_argument('limit', 100))

        query = self.get_argument('q', None)

        all_hosts = asbool(self.get_argument("all-hosts", True))

        # getting scenarios for the current host
        if not all_hosts:
            current_host = get_hostname(self.request)
            hostname = current_host
        else:
            # getting all scenarios
            hostname = '.*'

        tracker = Tracker(self.db)

        mf = MagicFiltering(query=query, hostname=hostname)
        tracker_filter = mf.get_filter()

        # getting total items
        total_items = yield tracker.item_count(tracker_filter)

        cursor = tracker.find_tracker_data(tracker_filter, skip, limit)

        tracker_objects = []
        while (yield cursor.fetch_next):
            try:
                document = cursor.next_object()
                # converting datetime object to string
                document['start_time'] = document['start_time'].strftime('%Y-%m-%d %H:%M:%S')
                # converting document ID to string
                obj_id = str(ObjectId(document['_id']))
                document['id'] = obj_id
                # adding object ref ID
                document['href'] = "/api/v2/tracker/records/objects/%s" % obj_id
                # removing BSON object
                document.pop('_id')
                tracker_objects.append(document)
            except Exception as ex:
                log.warn('Failed to fetch document: %s' % ex)

        # --- Pagination ---

        # skip forward
        skip_forward = skip
        skip_forward += limit

        # skip backwards
        skip_backwards = skip - limit
        if skip_backwards < 0:
            skip_backwards = 0

        # previous, removing link if there are no pages
        if skip != 0:
            previous_page = "/api/v2/tracker/records?skip=" + str(skip_backwards) + "&limit=" + str(limit)
        else:
            previous_page = None

        # next page, removing link if there are no records ahead
        if skip_forward + limit >= total_items:
            next_page = None
        else:
            next_page = "/api/v2/tracker/records?skip=" + str(skip_forward) + "&limit=" + str(limit)

        result = {'data': tracker_objects,
                  'paging': {
                      'previous': previous_page,
                      'next': next_page,
                      'first': "/api/v2/tracker/records?skip=" + str(0) + "&limit=" + str(limit),
                      'last': "/api/v2/tracker/records?skip=" + str(total_items - limit) + "&limit=" + str(limit),
                      'currentLimit': limit,
                      'totalItems': total_items
                  }}

        self.write(result)


class TrackerWebSocket(websocket.WebSocketHandler):
    def open(self):
        print("WebSocket opened")

    @gen.coroutine
    def on_message(self, query_json):
        query_dict = json.loads(query_json)
        self.db = motor_driver(self.settings)
        # getting pagination info
        skip = query_dict.get('skip', 0)
        limit = query_dict.get('limit', 25)
        query = query_dict.get('q', None)

        all_hosts = asbool(self.get_argument("all-hosts", True))

        # getting scenarios for the current host
        if not all_hosts:
            current_host = get_hostname(self.request)
            hostname = current_host
        else:
            # getting all scenarios
            hostname = '.*'

        tracker = Tracker(self.db)

        mf = MagicFiltering(query=query, hostname=hostname)
        tracker_filter = mf.get_filter()

        # getting total items
        total_items = yield tracker.item_count(tracker_filter)

        cursor = tracker.find_tracker_data(tracker_filter, skip, limit)

        tracker_objects = []
        while (yield cursor.fetch_next):
            try:
                document = cursor.next_object()
                # converting datetime object to string
                document['start_time'] = document['start_time'].strftime('%Y-%m-%d %H:%M:%S')
                # converting document ID to string
                obj_id = str(ObjectId(document['_id']))
                document['id'] = obj_id
                # adding object ref ID
                document['href'] = "/api/v2/tracker/records/objects/%s" % obj_id
                # removing BSON object
                document.pop('_id')
                tracker_objects.append(document)
            except Exception as ex:
                log.warn('Failed to fetch document: %s' % ex)

        # --- Pagination ---

        # skip forward
        skip_forward = skip
        skip_forward += limit

        # skip backwards
        skip_backwards = skip - limit
        if skip_backwards < 0:
            skip_backwards = 0

        # previous, removing link if there are no pages
        if skip != 0:
            previous_page = "/api/v2/tracker/records?skip=" + str(skip_backwards) + "&limit=" + str(limit)
        else:
            previous_page = None

        # next page, removing link if there are no records ahead
        if skip_forward + limit >= total_items:
            next_page = None
        else:
            next_page = "/api/v2/tracker/records?skip=" + str(skip_forward) + "&limit=" + str(limit)

        result = {'data': tracker_objects,
                  'paging': {
                      'previous': previous_page,
                      'next': next_page,
                      'first': "/api/v2/tracker/records?skip=" + str(0) + "&limit=" + str(limit),
                      'last': "/api/v2/tracker/records?skip=" + str(total_items - limit) + "&limit=" + str(limit),
                      'currentLimit': limit,
                      'totalItems': total_items
                  }}

        self.write_message(result)

    def on_close(self):
        print("WebSocket closed")


class TrackerRecordDetailsHandler(BaseHandler):
    """
    /api/v2/tracker/records/objects/<record_id>
    Gets tracker record details
    """

    def initialize(self):
        """

        Initializing database and setting header. Using global tornado settings that are generated
        during startup to acquire database client
        """
        # setting header
        self.set_header('x-stub-o-matic-version', version)
        # get motor driver
        self.db = motor_driver(self.settings)

    def compute_etag(self):
        return None

    @gen.coroutine
    def get(self, record_id):
        tracker = Tracker(self.db)

        # getting tracker obj
        obj = yield tracker.find_tracker_data_full(record_id)
        if obj is not None:
            obj['start_time'] = obj['start_time'].strftime('%Y-%m-%d %H:%M:%S')
            # converting document ID to string
            obj_id = str(ObjectId(obj['_id']))
            obj['id'] = obj_id
            # removing BSON object
            obj.pop('_id')

            result = {
                'data': obj
            }
            self.write(result)
        else:
            self.set_status(404)
            self.write("Record with ID: %s not found." % record_id)


from stubo.service.api_v2 import list_available_modules


class ExternalModulesHandler(BaseHandler):
    """
    /api/v2/modules/

    example output:
    {
    version: "0.6.6"
    data: {
        info: {
            response: {
                loaded_sys_versions: [0]
                latest_code_version: 1
            }-
        }-
        message: "list modules"
        }-
    }
    """

    def get(self):
        self.write(list_available_modules(get_hostname(self.request)))


class ExternalModuleDeleteHandler(BaseHandler):
    """
    /api/v2/modules/objects/<module_name>

    """

    def delete(self, module_name):
        # complying to current api
        names = [module_name]

        # deleting modules in subordinate redis
        cmdq = InternalCommandQueue()
        # Note: delete and unload from all subordinates not just the executing one
        cmdq.add(get_hostname(self.request),
                 'delete/module?name={0}'.format(module_name))
        result = delete_module(self.request, names)
        self.write(result)


class ExecuteCommandsHandler(TrackRequest):
    """
    /manage/execute

    example output:
    {
        'data': {'executed_commands':
                      {'commands': [
                             ('delete/stubs?scenario=response&force=true',
                              200),
                             ('put/module?name=/static/cmds/date/response.py',
                              200),
                             ('begin/session?scenario=response&session=response_rec&mode=record',
                              200),
                             ('put/stub?session=response_rec&ext_module=response&recorded_on=2014-06-01
                                                                    ,response.request.xml,response.xml',
                              200),
                             ('end/session?session=response_rec',
                              200),
                             ('begin/session?scenario=response&session=response_play&mode=playback',
                              200),
                             ('get/response?session=response_play&ext_module=response&played_on=2014-06-03
                                                                                    ,response.request.xml',
                              200),
                             ('end/session?session=response_play',
                              200)
                          ]},
              'number_of_errors': 0,
              'number_of_requests': 8},
        'version': '0.6.6'
    }
    """

    @stubo_async
    def post(self):

        response = None
        # parsing body
        try:
            bd = json.loads(self.request.body)
        except Exception as ex:
            log.warning("Failed to parse submited request to execute commands: %s" % ex)
            # returning bad request
            raise exception_response(400,
                                     title="Valid JSON not found in submitted request")

        # getting parameters
        cmds = bd.get('command', None)
        cmd_file_url = bd.get('commandFile', None)

        # looking for command file url
        if cmd_file_url:
            request = DummyModel(protocol=self.request.protocol,
                                 host=self.request.host,
                                 arguments=self.request.arguments)
            response = run_command_file(cmd_file_url, request,
                                        self.settings['static_path'])
        # looking for plain command
        elif cmds:
            response = run_commands(self, cmds)

        # checking whether we have a valid response
        if response:
            log.debug(u'command_handler_form_request: cmd_file={0},cmds={1}'.format(
                cmd_file_url, cmds))

            return response
        else:
            raise exception_response(400,
                                     title="'cmds' or 'cmdFile' parameter not supplied.")


def _get_scenario_full_name(handler, name, host=None):
    """
    Gets full name hostname:scenario_name
    :param name:
    :return:
    """
    # check if hostname is supplied - if not, override scenario name with new value
    if ":" not in name:
        if host is None:
            host = get_hostname(handler.request)
        name = '%s:%s' % (host, name)
    return name
