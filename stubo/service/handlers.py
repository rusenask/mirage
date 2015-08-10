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
from tornado.web import RequestHandler, asynchronous
import tornado.ioloop
from plop.collector import Collector
import yappi

from stubo.service.handlers_mt import (
    export_stubs_request, list_stubs_request,
    command_handler_request, command_handler_form_request, delay_policy_request,
    stub_count_request, begin_session_request, end_session_request,
    put_stub_request, get_response_request, delete_stubs_request,
    status_request, manage_request, tracker_request,
    tracker_detail_request, get_delay_policy_request,
    delete_delay_policy_request, put_module_request,
    delete_module_request, list_module_request, delete_modules_request,
    put_bookmark_request, get_bookmark_request, jump_bookmark_request,
    get_bookmarks_request, delete_bookmark_request, import_bookmarks_request,
    stats_request, analytics_request, put_setting_request, get_setting_request,
    end_sessions_request, list_scenarios_request
)
from stubo.utils.track import TrackRequest
from stubo import version
from stubo.exceptions import StuboException, exception_response
from handlers_mt import rename_scenario
from tornado.util import ObjectDict


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

class PutBookmarkHandler(TrackRequest):
    '''/api/put/bookmark?session=joe&session=mary&name=mary_and_joe_fri_2pm
    Note the sessions need to be in playback mode.
    The only state saved is the request_index for the sessions supplied
    which can belong to different scenarios. The request_index is formed of
    session_name:{hash of request text} so a later reset of this state using
    /api/get/bookmark?name=mary_and_joe_fri_2pm assumes the stubs have not been
    changed as the request hash needs to exist in "{host}:{scenario}:request"
    and the response index needs to be consistent with the value of that
    key which is a list of response hashs as shown below

 redis 127.0.0.1:6379> hgetall "localhost:conv:request"    
 1) "joe:8daae6e2f064b50c80e5d91720043364219e0453cfc3630f2b21a5c5"
 2) "[[\"78f09c29288b74bc9986e34574e45f596df96c1abd1b2c0247166b12\", \"d68f0e02d042a2e6118a06cf20b56450d37b97ca9c4a6e9135d99fb2\", \"e121cfd777bfc56585ec86a04af60b8e5433dc3d5a8192ac981a9cd2\"], \"\", \"2013-10-25\", \"2013-10-25\", {}]"
 3) "joe:2cf00b76334fb16c640bb11a99adad49beafd2edf67c34a52218d9c0"
 4) "[[\"9f50aad95323947a75a330e2115854bade723ca424f60f2089710da1\", \"d3ae99681978575e40a94881f5fe66079d7ab862ff2e0de51046c0cf\", \"4a8ccf33d16d45f98ad9152063b0d38bca449aeaa2c178c27c3fbca0\"], \"\", \"2013-10-25\", \"2013-10-25\", {}]"
 5) "joe:f2022a5438c084278ec23c400b2a0551203b8d0320e071ff981f9ec4"
 6) "[[\"8a63cd9b720c32b82835c0a30e8d8799626ba3768ebf6136f4b1e1b8\", \"4cff130013f4833e81613b3a44d669040b33c9030e312f339e0b5661\", \"c8c48e8fcc8d1784cfa92745895595415d35b51725e8b8ead796cd4d\"], \"\", \"2013-10-25\", \"2013-10-25\", {}]"
 7) "mary:8daae6e2f064b50c80e5d91720043364219e0453cfc3630f2b21a5c5"
 8) "[[\"78f09c29288b74bc9986e34574e45f596df96c1abd1b2c0247166b12\", \"d68f0e02d042a2e6118a06cf20b56450d37b97ca9c4a6e9135d99fb2\", \"e121cfd777bfc56585ec86a04af60b8e5433dc3d5a8192ac981a9cd2\"], \"\", \"2013-10-25\", \"2013-10-25\", {}]"
 9) "mary:2cf00b76334fb16c640bb11a99adad49beafd2edf67c34a52218d9c0"
10) "[[\"9f50aad95323947a75a330e2115854bade723ca424f60f2089710da1\", \"d3ae99681978575e40a94881f5fe66079d7ab862ff2e0de51046c0cf\", \"4a8ccf33d16d45f98ad9152063b0d38bca449aeaa2c178c27c3fbca0\"], \"\", \"2013-10-25\", \"2013-10-25\", {}]"
11) "mary:f2022a5438c084278ec23c400b2a0551203b8d0320e071ff981f9ec4"
12) "[[\"8a63cd9b720c32b82835c0a30e8d8799626ba3768ebf6136f4b1e1b8\", \"4cff130013f4833e81613b3a44d669040b33c9030e312f339e0b5661\", \"c8c48e8fcc8d1784cfa92745895595415d35b51725e8b8ead796cd4d\"], \"\", \"2013-10-25\", \"2013-10-25\", {}]"   
    '''

    def get(self):
        self.post()

    def post(self):
        put_bookmark_request(self)

class GetBookmarksHandler(TrackRequest):

    def get(self):
        self.post()

    def post(self):
        get_bookmark_request(self)

class JumpBookmarkHandler(TrackRequest):

    def get(self):
        self.post()

    def post(self):
        jump_bookmark_request(self)

class DeleteBookmarkHandler(TrackRequest):

    def get(self):
        self.post()

    def post(self):
        delete_bookmark_request(self)

class ImportBookmarksHandler(TrackRequest):

    def get(self):
        self.post()

    def post(self):
        import_bookmarks_request(self)

class BookmarkHandler(RequestHandler):

    def compute_etag(self):
        return None

    def get(self):
        get_bookmarks_request(self)

    def post(self):
        self.get()

class ViewTrackerHandler(RequestHandler):

    def compute_etag(self):
        return None

    def get(self):
        tracker_request(self)

class ViewATrackerHandler(RequestHandler):

    def get(self, tracker_id, **kwargs):
        tracker_detail_request(self, tracker_id)

class HomeHandler(RequestHandler):
    def get(self):
        response = self.render_string("home.html", page_title='Stub-O-Matic')
        self.write(response)
        self.set_header('x-stubo-version', version)
        self.finish()

class DocsHandler(RequestHandler):
    def get(self):
        self.redirect('http://stubo-app.readthedocs.org/en/latest/',
                      permanent=True)

class GetVersionHandler(TrackRequest):

    def get(self):
        response = {'version' : self.settings['stubo_version']}
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

class StuboCommandHandlerHTML(TrackRequest):

    def compute_etag(self):
        # override tornado default which will return a 304 (not modified)
        # if the response contents of a GET call with the same signature matches
        return None

    def get(self):
        # handle form from the GUI (/manage page) 
        command_handler_form_request(self)

    def post(self):
        self.get()

class GetStubExportHandler(TrackRequest):

    def get(self):
        export_stubs_request(self)

    def post(self):
        self.get()

class GetStubListHandlerHTML(RequestHandler):

    def get(self):
        list_stubs_request(self, html=True)

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

class ManageHandler(RequestHandler):

    def get(self):
        manage_request(self)

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


