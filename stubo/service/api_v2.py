# coding=utf-8
"""
    :copyright: (c) 2015 by OpenCredo.
    :license: GPLv3, see LICENSE for more details.
"""

from stubo.model.db import Scenario

from stubo.service.delay import Delay
from stubo.model.stub import Stub
from stubo import version
from stubo.service.api import get_response
from stubo.utils import get_hostname
from stubo.cache import Cache
from stubo.exceptions import exception_response
import logging
from stubo.ext.module import Module
from stubo.model.request import StuboRequest
from stubo.utils.track import TrackTrace
from stubo.match import match
from stubo.utils import as_date
from stubo.cache import add_request, StubCache
from stubo.ext.transformer import transform

from stubo.cache import get_keys
import sys

log = logging.getLogger(__name__)


def begin_session(handler, scenario_name, session_name, mode, system_date=None,
                  warm_cache=False):
    """
    Begins session for given scenario
    :param handler: request handler class
    :param scenario_name: scenario name
    :param session_name: session name
    :param mode: mode - record, playback
    :param system_date:
    :param warm_cache:
    :return: :raise exception_response:
    """
    log.debug('begin_session')
    response = {
        'version': version
    }
    scenario_manager = Scenario()
    # cache = Cache(get_hostname(handler.request))

    # checking whether full name (with hostname) was passed, if not - getting full name
    # scenario_name_key = "localhost:scenario_1"
    if ":" not in scenario_name:
        cache = Cache(get_hostname(handler.request))
        scenario_name_key = cache.scenario_key_name(scenario_name)
    else:
        # setting scenario full name
        scenario_name_key = scenario_name
        # removing hostname from scenario name
        slices = scenario_name.split(":")
        scenario_name = slices[1]
        cache = Cache(slices[0])

    # get scenario document
    scenario_doc = scenario_manager.get(scenario_name_key)
    if not scenario_doc:
        raise exception_response(404,
                                 title='Scenario not found - {0}. To begin a'
                                       ' session - create a scenario.'.format(scenario_name_key))

    cache.assert_valid_session(scenario_name, session_name)

    if mode == 'record':
        log.debug('begin_session, mode=record')
        # check if there are any existing stubs in this scenario
        if scenario_manager.stub_count(scenario_name_key) > 0:
            err = exception_response(400,
                                     title='Scenario ({0}) has existing stubs, delete them before '
                                           'recording or create another scenario!'.format(scenario_name_key))
            raise err

        scenario_id = scenario_doc['_id']
        log.debug('new scenario: {0}'.format(scenario_id))
        session_payload = {
            'status': 'record',
            'scenario': scenario_name_key,
            'scenario_id': str(scenario_id),
            'session': str(session_name)
        }
        cache.set_session(scenario_name, session_name, session_payload)
        log.debug('new redis session: {0}:{1}'.format(scenario_name_key,
                                                      session_name))
        response["data"] = {
            'message': 'Record mode initiated....',
        }
        response["data"].update(session_payload)
        cache.set_session_map(scenario_name, session_name)
        log.debug('finish record')

    elif mode == 'playback':

        recordings = cache.get_sessions_status(scenario_name,
                                               status='record',
                                               local=False)
        if recordings:
            raise exception_response(400, title='Scenario recordings taking '
                                                'place - {0}. Found the '
                                                'following record sessions: {1}'.format(scenario_name_key, recordings))
        cache.create_session_cache(scenario_name, session_name, system_date)
        if warm_cache:
            # iterate over stubs and call get/response for each stub matchers
            # to build the request & request_index cache
            # reset request_index to 0
            log.debug("warm cache for session '{0}'".format(session_name))
            scenario_manager = Scenario()
            for payload in scenario_manager.get_stubs(scenario_name_key):
                stub = Stub(payload['stub'], scenario_name_key)
                mock_request = " ".join(stub.contains_matchers())
                handler.request.body = mock_request
                get_response(handler, session_name)
            cache.reset_request_index(scenario_name)

        response["data"] = {
            "message": "Playback mode initiated...."
        }
        response["data"].update({
            "status": "playback",
            "scenario": scenario_name_key,
            "session": str(session_name)
        })
    else:
        raise exception_response(400,
                                 title='Mode of playback or record required')
    return response


def end_sessions(handler, scenario_name):
    """
    End all sessions for specified scenario
    :param handler: request handler
    :param scenario_name: scenario name - can be supplied with hostname ("mirage-app:scenario_x")
    :return:
    """
    response = {
        'version': version,
        'data': {}
    }
    # checking whether full name (with hostname) was passed, if not - getting full name
    # scenario_name_key = "localhost:scenario_1"
    if ":" not in scenario_name:
        hostname = get_hostname(handler.request)
        cache = Cache(hostname)
    else:
        # removing hostname from scenario name
        slices = scenario_name.split(":")
        scenario_name = slices[1]
        hostname = slices[0]
        cache = Cache(hostname)

    # cache = Cache(get_hostname(handler.request))
    sessions = list(cache.get_sessions_status(scenario_name,
                                              status=('record', 'playback')))
    # ending all sessions
    for session_name, session in sessions:
        session_response = end_session(hostname, session_name)
        response['data'][session_name] = session_response.get('data')
    return response

from stubo.service.api import store_source_recording

def end_session(hostname, session_name):
    """
    End specific session.
    :param hostname: hostname for this session
    :param session_name: session name
    :return:
    """
    response = {
        'version': version
    }
    cache = Cache(hostname)
    scenario_key = cache.get_scenario_key(session_name)
    if not scenario_key:
        # end/session?session=x called before begin/session
        response['data'] = {
            'message': 'Session ended'
        }
        return response

    host, scenario_name = scenario_key.split(':')

    session = cache.get_session(scenario_name, session_name, local=False)
    if not session:
        # end/session?session=x called before begin/session
        response['data'] = {
            'message': 'Session ended'
        }
        return response

    # handler.track.scenario = scenario_name
    session_status = session['status']
    if session_status not in ('record', 'playback'):
        log.warn('expecting session={0} to be in record or playback for '
                 'end/session'.format(session_name))

    session['status'] = 'dormant'
    # clear stubs cache & scenario session data
    session.pop('stubs', None)
    cache.set(scenario_key, session_name, session)
    cache.delete_session_data(scenario_name, session_name)
    if session_status == 'record':
        log.debug('store source recording to pre_scenario_stub')
        store_source_recording(scenario_key, session_name)

    response['data'] = {
        'message': 'Session ended'
    }
    return response



def update_delay_policy(handler):
    """Record delay policy in redis to be available globally to any
    users for their sessions.
    Creates a delay policy. Examples:
        { “name”: “delay_name”,
          “delay_type”: “fixed”,
          “milliseconds”: 50}
        or
        { “name”: “delay_name”,
          “delay_type”: “normalvariate”,
          “mean”: “mean_val”,
          “stddev”: “val”}

    :return: :response: <dict> with status code (400 - bad request, 409 - something is wrong, conflict of values,
    200 - delay policy updated, 201 - delay policy created)
    """
    cache = Cache(get_hostname(handler.request))
    response = {
        'version': version
    }
    doc = handler.request.arguments
    err = None
    status_code = None
    # checking name
    if 'name' not in doc:
        err = "'name' parameter not found in request"
        status_code = 400
    else:
        if " " in doc['name']:
            err = "'name' parameter should not contain white space"
            status_code = 400

    if 'delay_type' not in doc:
        err = "'delay_type' param not found in request"
        status_code = 400
    if not err:
        # checking for fixed delays
        if doc['delay_type'] == 'fixed':
            if 'milliseconds' not in doc:
                err = "'milliseconds' param is required for 'fixed' delays"
                status_code = 409

        # checking for normalvariate delays
        elif doc['delay_type'] == 'normalvariate':
            if 'mean' not in doc or 'stddev' not in doc:
                err = "'mean' and 'stddev' params are required for " \
                      "'normalvariate' delays"
                status_code = 409

        # checking for weighted delays
        elif doc['delay_type'] == 'weighted':
            if 'delays' not in doc:
                err = "'delays' are required for 'weighted' delays"
                status_code = 409
            else:
                try:
                    Delay.parse_args(doc)
                except Exception, e:
                    err = 'Unable to parse weighted delay arguments: {0}'.format(str(e))
                    status_code = 409
        # delay_type not known, creating error
        else:
            err = 'Unknown delay type: {0}'.format(doc['delay_type'])
            status_code = 400
    # if errors are present - add key error
    if err:
        response['error'] = err
        response['status_code'] = status_code
        return response
    # no errors were detected - updating cache and returning results
    result = cache.set_delay_policy(doc['name'], doc)

    if result:
        updated = 'new'
        status_code = 201
    else:
        updated = 'updated'
        status_code = 200

    response['status_code'] = status_code
    response['data'] = {
        'message': 'Put Delay Policy Finished',
        'name': doc['name'],
        'delay_type': doc['delay_type'],
        'delayPolicyRef': '/stubo/api/v2/delay-policy/objects/%s' % doc['name'],
        'status': updated
    }
    return response


def get_delay_policy(handler, name, cache_loc):
    """
    Gets specified or all delays, returns dictionary

    :param handler: RequestHandler (or TrackRequest, BaseHandler, etc..)
    :param name: Delay name, if None is passed - gets all delays
    :param cache_loc: Cache location, usually just 'main'
    :return: dictionary of dictionaries with scenario information and reference URI and status_code for response
    """
    cache = Cache(get_hostname(handler.request))
    response = {
        'version': version
    }
    status_code = 200
    delays = cache.get_delay_policy(name, cache_loc)

    # if delay policy not found but name was specified, return error message
    if delays is None and name is not None:
        status_code = 404
        response['error'] = "Delay policy '%s' not found" % name
        return response, status_code

    # list for storing delay objects since cache.get_delay_policy(name, cache_loc) returns a dict
    delay_list = []
    # adding references
    if name is None:
        if delays is not None:
            # All stored delays should be returned
            for k, v in delays.items():
                v['delayPolicyRef'] = "/stubo/api/v2/delay-policy/objects/%s" % k
                delay_list.append(v)
        else:
            # Returning empty dict
            delays = {}
            delay_list.append(delays)
    else:
        delays['delayPolicyRef'] = "/stubo/api/v2/delay-policy/objects/%s" % name
        delay_list.append(delays)

    response['data'] = delay_list
    return response, status_code


def list_available_modules(hostname):
    """
    Gets all available modules (for given host) and returns a list with them.
    :param hostname:
    :return:
    """
    modules_list = []
    module = Module(hostname)
    # getting keys
    keys = get_keys('{0}:modules:*'.format(module.host()))

    names = [x.rpartition(':')[-1] for x in keys]

    for name in names:
        loaded_sys_versions = [x for x in sys.modules.keys() if '{0}_v'.format(name) in x]
        lastest_code_version = module.latest_version(name)
        source_code = Module(hostname).get_source(name)
        obj = {
            'name': name,
            'latest_code_version': lastest_code_version,
            'loaded_sys_versions': loaded_sys_versions,
            'source_raw': source_code,
            'href': '/api/v2/modules/objects/%s' % name
        }
        modules_list.append(obj)

    return {
        'version': version,
        'data': modules_list
    }


class MagicFiltering:
    def __init__(self, query, hostname):
        self.query = query
        self.hostname = hostname
        self.conditions = []
        # adding hostname regex
        self.conditions.append({'host': {'$regex': hostname}})

    def get_filter(self):
        """

        Main method, returns query for MongoDB with condition list
        :return:
        """
        if self.query:
            query_list = self.query.split(' ')
            map(self._assign_function, query_list)
            return {'$and': self.conditions}
        else:
            return {}

    def _find_api_scenario_conditions(self, keyword):
        """

        Searching for keywords in scenario or api call name ('function' in MongoDB document)
        :param keyword:
        """
        fl = {'$or': [
            {'scenario': {'$regex': keyword, '$options': 'i'}},
            {'function': {'$regex': keyword, '$options': 'i'}}
        ]
        }
        self.conditions.append(fl)

    def _assign_function(self, item):
        """

        Assigns function based on keyword
        :param item:
        """
        if 'sc:' in item and len(item) > 3:
            # looking for status codes in requests
            self._find_status_code_conditions(item)
        elif 'rt:' in item and len(item) > 3:
            # looking for response time conditions
            self._find_response_time_conditions(item)
        elif 'd:' in item and len(item) > 2:
            # looking for delays conditions
            self._find_delays_conditions(item)
        else:
            # looking for any keywords in scenarios or API calls
            self._find_api_scenario_conditions(item)

    def _find_delays_conditions(self, delay):
        """

        Filters based on delays
        :param delay:
        """
        try:
            _, d = delay.split(":")
            value = self._get_item_query_value(d)
            self.conditions.append({'delay': value})
        except Exception as ex:
            log.debug("Got error during delay code search: %s" % ex)

    def _find_status_code_conditions(self, status_code):
        """

       Looks for status code query inside string. Finds comparison operators and amends query to condition list
       :param status_code:
       """
        try:
            _, code = status_code.split(":")
            value = self._get_item_query_value(code)
            self.conditions.append({'return_code': value})
        except Exception as ex:
            log.debug("Got error during status code search: %s" % ex)

    def _find_response_time_conditions(self, response_time):
        """

        Looks for response time query inside string. Finds comparison operators and amends query to condition list
        :param response_time:
        """
        try:
            _, tm = response_time.split(":")
            # searching for <, <=, >, >= operators
            value = self._get_item_query_value(tm)
            self.conditions.append({'duration_ms': value})
        except Exception as ex:
            log.debug("Got error during status code search: %s" % ex)

    @staticmethod
    def _get_item_query_value(tm):
        """

        Searching for operators and creates queries for database based on them
        :param tm:
        :return:
        """
        # searching for <, <=, >, >= operators
        if '<=' in tm:
            value = {'$lte': int(tm[2:])}
        elif '<' in tm:
            value = {'$lt': int(tm[1:])}
        elif '>=' in tm:
            value = {'$gte': int(tm[2:])}
        elif '>' in tm:
            value = {'$gt': int(tm[1:])}
        else:
            value = int(tm)

        return value


def get_response_v2(handler, full_scenario_name, session_name):
    # main result dictionary that will be returned
    result_dict = {}

    request = handler.request
    stubo_request = StuboRequest(request)
    cache = Cache(get_hostname(request))

    scenario_name = full_scenario_name.partition(':')[-1]
    handler.track.scenario = scenario_name
    request_id = stubo_request.id()
    module_system_date = handler.get_argument('system_date', None)
    url_args = handler.track.request_params

    # trace_matcher = TrackTrace(handler.track, 'matcher')
    user_cache = handler.settings['ext_cache']
    # check cached requests
    cached_request = cache.get_request(scenario_name, session_name, request_id)
    if cached_request:
        response_ids, delay_policy_name, recorded, system_date, module_info, request_index_key = cached_request
    else:
        retry_count = 5 if handler.settings.get('is_cluster', False) else 1
        session, retries = cache.get_session_with_delay(scenario_name,
                                                        session_name,
                                                        retry_count=retry_count,
                                                        retry_interval=1)
        if retries > 0:
            log.warn("replication was slow for session: {0} {1}, it took {2} secs!".format(
                full_scenario_name, session_name, retries + 1))
        if session['status'] != 'playback':
            result_dict["error"] = 'cache status != playback. session={0}'.format(session)
            result_dict["statusCode"] = 412
            return result_dict

        system_date = session['system_date']
        if not system_date:
            result_dict["error"] = "subordinate session {0} not available for scenario {1}".format(
                session_name, full_scenario_name)
            result_dict["statusCode"] = 412
            return result_dict

        trace_matcher = TrackTrace(handler.track, 'matcher')
        session['ext_cache'] = user_cache
        result = match(stubo_request, session, trace_matcher,
                       as_date(system_date),
                       url_args=url_args,
                       hooks=handler.settings['hooks'],
                       module_system_date=module_system_date)
        # matching request not found
        if not result[0]:
            result_dict["error"] = "Not matching request found"
            result_dict["statusCode"] = 404
            return result_dict

        _, stub_number, stub = result
        response_ids = stub.response_ids()
        delay_policy_name = stub.delay_policy_name()
        recorded = stub.recorded()
        module_info = stub.module()
        request_index_key = add_request(session, request_id, stub, system_date,
                                        stub_number,
                                        handler.settings['request_cache_limit'])

        if not stub.response_body():
            _response = stub.get_response_from_cache(request_index_key)
            stub.set_response_body(_response['body'])

        if delay_policy_name:
            stub.load_delay_from_cache(delay_policy_name)

    if cached_request:
        stub = StubCache({}, full_scenario_name, session_name)
        stub.load_from_cache(response_ids, delay_policy_name, recorded,
                             system_date, module_info, request_index_key)
    trace_response = TrackTrace(handler.track, 'response')
    if module_info:
        trace_response.info('module used', str(module_info))
    response_text = stub.response_body()

    if not response_text:
        result_dict["error"] = 'Unable to find response in cache using session: {0}:{1}, '
        'response_ids: {2}'.format(full_scenario_name, session_name, response_ids)
        result_dict["statusCode"] = 400
        return result_dict

    # get latest delay policy
    delay_policy = stub.delay_policy()
    if delay_policy:
        delay = Delay.parse_args(delay_policy)
        if delay:
            delay = delay.calculate()
            msg = 'apply delay: {0} => {1}'.format(delay_policy, delay)
            log.debug(msg)
            handler.track['delay'] = delay
            trace_response.info(msg)

    trace_response.info('found response')
    module_system_date = as_date(module_system_date) if module_system_date \
        else module_system_date
    stub, _ = transform(stub,
                        stubo_request,
                        module_system_date=module_system_date,
                        system_date=as_date(system_date),
                        function='get/response',
                        cache=user_cache,
                        hooks=handler.settings['hooks'],
                        stage='response',
                        trace=trace_response,
                        url_args=url_args)
    transfomed_response_text = stub.response_body()[0]
    # Note transformed_response_text can be encoded in utf8
    if response_text[0] != transfomed_response_text:
        trace_response.diff('response:transformed',
                            dict(response=response_text[0]),
                            dict(response=transfomed_response_text))

    result_dict["body"] = transfomed_response_text
    result_dict["headers"] = stub.response_headers()
    result_dict["statusCode"] = stub.response_status()

    return result_dict
