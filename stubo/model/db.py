"""  
    :copyright: (c) 2015 by OpenCredo.
    :license: GPLv3, see LICENSE for more details.
"""
from pymongo import MongoClient, DESCENDING, ASCENDING
import logging
from bson.objectid import ObjectId
from stubo.utils import asbool
from stubo.model.stub import Stub
import hashlib
import time
import motor

default_env = {
    'port': 27017,
    'max_pool_size': 20,
    'tz_aware': True,
    'db': 'stubodb'
}


def coerce_mongo_param(k, v):
    if k in ('port', 'max_pool_size'):
        return int(v)
    elif k in ('tz_aware',):
        return asbool(v)
    return v


log = logging.getLogger(__name__)

mongo_client = None

def motor_driver(settings):
    # getting motor client
    client = motor.MotorClient(settings['mongo.host'], int(settings['mongo.port']))
    return client[settings['mongo.db']]

def get_mongo_client():
    return mongo_client


def get_connection(env=None):
    env = env or default_env
    _env = env.copy()
    dbname = _env.pop('db', None)
    client = MongoClient(**_env)
    if dbname:
        log.debug('using db={0}'.format(dbname))
        client = getattr(client, dbname)
    return client


class Scenario(object):
    def __init__(self, db=None):
        self.db = db or mongo_client
        assert self.db

    def get_stubs(self, name=None):
        if name:
            filter = {'scenario': name}
            return self.db.scenario_stub.find(filter)
        else:
            return self.db.scenario_stub.find()

    def get_pre_stubs(self, name=None):
        if name:
            filter = {'scenario': name}
            return self.db.pre_scenario_stub.find(filter)
        else:
            return self.db.scenario_pre_stub.find()

    def stub_count(self, name):
        return self.get_stubs(name).count()

    def get(self, name):
        return self.db.scenario.find_one({'name': name})

    def get_all(self, name=None):
        if name:
            cursor = self.db.scenario.find({'name': name})
        else:
            cursor = self.db.scenario.find()
        return cursor

    def insert(self, **kwargs):
        return self.db.scenario.insert(kwargs)

    def change_name(self, name, new_name):
        """
        Rename scenario and all stubs
        :param name: current scenario name
        :param new_name: new scenario name
        :return: statistics, how many stubs were changed
        """
        # updating scenario stub collection. You have to specify all parameters as booleans up to the one that you
        # actually want, in our case - the fourth parameter "multi" = True
        # update(spec, document[, upsert=False[,
        #                        manipulate=False[, safe=None[, multi=False[, check_keys=True[, **kwargs]]]]]])
        response = {
            'Old name': name,
            "New name": new_name
        }
        try:
            result = self.db.scenario_stub.update(
                {'scenario': name}, {'$set': {'scenario': new_name}}, False, False, None, True)
            try:
                response['Stubs changed'] = result['nModified']
            except KeyError:
                # older versions of mongodb returns 'n' instead of 'nModified'
                response['Stubs changed'] = result['n']
            except Exception as ex1:
                # this is probably KeyError, leaving Exception for debugging purposes
                log.debug("Could not get STUB nModified key, result returned: %s. Error: %s" % (result, ex1))
        except Exception as ex:
            log.debug("Could not update scenario stub, got error: %s " % ex)
            response['Stubs changed'] = 0

        # updating pre stubs
        try:
            result = self.db.scenario_pre_stub.update(
                {'scenario': name}, {'$set': {'scenario': new_name}}, False, False, None, True)
            try:
                response['Pre stubs changed'] = result['nModified']
            except KeyError:
                # older versions of mongodb returns 'n' instead of 'nModified'
                response['Pre stubs changed'] = result['n']
            except Exception as ex1:
                log.debug("Could not get PRE STUB nModified key, result returned: %s. Error: %s" % (result, ex1))
        except Exception as ex:
            log.debug("Could not update scenario pre stub, got error: %s" % ex)
            response['Pre stubs changed'] = 0

        try:
            # updating scenario itself
            result = self.db.scenario.update({'name': name}, {'name': new_name})
            try:
                response['Scenarios changed'] = result['nModified']
            except KeyError:
                # older versions of mongodb returns 'n' instead of 'nModified'
                response['Scenarios changed'] = result['n']
            except Exception as ex1:
                log.debug("Could not get SCENARIO nModified key, result returned: %s. Error: %s" % (result, ex1))
        except Exception as ex:
            log.debug("Could not update scenario, got error: %s" % ex)
            response['Scenarios changed'] = 0

        return response

    def recorded(self, name=None):
        """
        Calculates scenario recorded date. If name is not supplied - returns a dictionary with scenario name and
        recorded date:
        { 'scenario_1': '2015-05-07',
          'scenario_2': '2015-05-07'}
        If a name is supplied - returns recorded date string (since MongoDB does not support DateTimeField).
        :param name: optional parameter to get recorded date for specific scenario
        :return: <dict> - if name is not supplied, <string> with date - if scenario name supplied.
        """
        start_time = time.time()
        pipeline = [
            {'$group': {
                '_id': '$scenario',
                'recorded': {'$max': '$recorded'}}}]
        # use the pipe to calculate latest date
        try:
            result = self.db.command('aggregate', 'scenario_stub', pipeline=pipeline)['result']
        except KeyError as ex:
            log.error(ex)
            return None
        except Exception as ex:
            log.error("Got error when trying to use aggregation framework: %s" % ex)
            return None
        # using dict comprehension to form a new dict for fast access to elements
        result_dict = {x['_id']: x['recorded'] for x in result}

        # finish time
        finish_time = time.time()
        log.info("Recorded calculated in %s ms" % int((finish_time-start_time)*1000))
        # if name is provided - return only single recorded date for specific scenario.
        if name:
            scenario_recorded = None
            try:
                scenario_recorded = result_dict[name]
            except KeyError:
                log.debug("Wrong scenario name supplied (%s)" % name)
            except Exception as ex:
                log.warn("Failed to get scenario recorded date for: %s, error: %s" % (name, ex))
            return scenario_recorded
        else:
            # returning full list (scenarios and sizes)
            return result_dict

    def size(self, name=None):
        """
        Calculates scenario sizes. If name is not supplied - returns a dictionary with scenario name and size
        (in bytes):
        { 'scenario_1': 5646145,
          'scenario_2': 12312312}
        If a name is supplied - returns a size Integer in bytes.
        :param name: optional parameter to get size of specific scenario
        :return: <dict> - if name is not supplied, <int> - if scenario name supplied.
        """
        start_time = time.time()
        pipeline = [{'$group': {
            '_id': '$scenario',
            'size': {'$sum': {'$divide': ['$space_used', 1024]}}
                                }
                    }]

        # use the pipe to calculate scenario sizes
        try:
            result = self.db.command('aggregate', 'scenario_stub', pipeline=pipeline)['result']
        except KeyError as ex:
            log.error(ex)
            return None
        except Exception as ex:
            log.error("Got error when trying to use aggregation framework: %s" % ex)
            return None
        # using dict comprehension to form a new dict for fast access to elements
        result_dict = {x['_id']: x['size'] for x in result}

        # finish time
        finish_time = time.time()
        log.info("Sizes calculated in %s ms" % int((finish_time-start_time)*1000))
        # if name is provided - return only single size for specific scenario.
        if name:
            scenario_size = None
            try:
                scenario_size = result_dict[name]
            except KeyError:
                log.debug("Wrong scenario name supplied (%s)" % name)
            except Exception as ex:
                log.warn("Failed to get scenario size for: %s, error: %s" % (name, ex))
            return scenario_size
        else:
            # returning full list (scenarios and sizes)
            return result_dict

    def stub_counts(self):
        """
        Calculates stub counts:
        { 'scenario_1': 100,
          'scenario_2': 20}

        Remember, that if the scenario doesn't have any stubs - it will not be in this list since it is not accessing
        scenario collection to add scenarios with 0 stubs.
        :return: <dict>
        """
        start_time = time.time()
        pipeline = [{'$group': {
            '_id': '$scenario',
            'count': {'$sum': 1}
        }
        }]

        # use the pipe to calculate scenario stub counts
        try:
            result = self.db.command('aggregate', 'scenario_stub', pipeline=pipeline)['result']
        except KeyError as ex:
            log.error(ex)
            return None
        except Exception as ex:
            log.error("Got error when trying to use aggregation framework: %s" % ex)
            return None
        # using dict comprehension to form a new dict for fast access to elements
        result_dict = {x['_id']: x['count'] for x in result}

        # finish time
        finish_time = time.time()
        log.info("Stub counts calculated in %s ms" % int((finish_time-start_time)*1000))

        return result_dict

    @staticmethod
    def _create_hash(matchers):
        """
        Creates a hash out of matchers list.
        :param matchers: <list> matchers
        :return: matchers md5 hash
        """
        if matchers is not None:
            return hashlib.md5(u"".join(unicode(matchers))).hexdigest()
        elif matchers is None:
            return None

    def get_matched_stub(self, name, matchers_hash):
        """
        Gets matched stub for specific scenario. Relies on indexed "matchers" key in scenario_stub object
        :param name: <string> scenario name
        :param matchers: <list> containing matchers
        :return: matched stub document or None if stub not found
        """
        if name:
            pattern = {'scenario': name,
                       'matchers_hash': matchers_hash}
            return self.db.scenario_stub.find_one(pattern)

    def insert_stub(self, doc, stateful):
        """
        Insert stub into DB. Performs a check whether this stub already exists in database or not.  If it exists
        and stateful is True - new response is appended to the response list, else - reports that duplicate stub
        found and it will not be inserted.

        :param doc: Stub class with Stub that will be inserted
        :param stateful: <boolean> specify whether stub insertion should be stateful or not
        :return: <string> message with insertion status:
           ignored - if not stateful and stub was already present
           updated - if stateful and stub was already present
           created - if stub was not present in database
        """
        # getting initial values - stub matchers, scenario name
        matchers = doc['stub'].contains_matchers()
        scenario = doc['scenario']

        matchers_hash = self._create_hash(matchers)
        # check if we have matchers - should be None for REST calls
        if matchers is not None:
            # additional helper value for indexing
            doc['matchers_hash'] = matchers_hash
            matched_stub = self.get_matched_stub(name=scenario, matchers_hash=matchers_hash)

            # checking if stub already exists
            if matched_stub:
                # creating stub object from found document
                the_stub = Stub(matched_stub['stub'], scenario)
                if not stateful and doc['stub'].response_body() == the_stub.response_body():
                    msg = 'duplicate stub found, not inserting.'
                    log.warn(msg)
                    result = {'status': 'ignored',
                              'msg': msg,
                              'key': str(matched_stub['_id'])}
                    return result
                # since stateful is true - updating stub body by extending the list
                log.debug('In scenario: {0} found exact match for matchers:'
                          ' {1}. Perform stateful update of stub.'.format(scenario, matchers))
                response = the_stub.response_body()
                response.extend(doc['stub'].response_body())
                the_stub.set_response_body(response)
                # updating Stub body and size, writing to database
                self.db.scenario_stub.update(
                    {'_id': matched_stub['_id']},
                    {'$set': {'stub': the_stub.payload,
                              'space_used': len(unicode(the_stub.payload))}})
                result = {'status': 'updated',
                          'msg': 'Updated with stateful response',
                          'key': str(matched_stub['_id'])}
                return result

        # Stub doesn't exist in DB - preparing new object
        doc['stub'] = doc['stub'].payload

        # additional helper for aggregation framework
        try:
            doc['recorded'] = doc['stub']['recorded']
        except KeyError:
            # during tests "recorded" value is not supplied
            pass
        # calculating stub size
        doc['space_used'] = len(unicode(doc['stub']))

        # inserting stub into DB
        status = self.db.scenario_stub.insert(doc)

        # create indexes
        if matchers_hash:
            self._create_index(key="matchers_hash")
        # creating index for scenario and priority
        self._create_index(key="scenario")
        if 'priority' in doc['stub']:
            # creating index for priority
            self._create_index("stub.priority")

        result = {'status': 'created',
                  'msg': 'Inserted scenario_stub',
                  'key': str(status)}
        return result

    def _create_index(self, key=None, direction=ASCENDING):
        """
        Creates index for specific key, fails silently if index creation was unsuccessful. Key examples:
        "matchers_hash" , "stub.priority", "scenario"
        :param key: <string>
        :param direction: ASCENDING or DESCENDING (from pymongo)
        """
        if key:
            try:
                self.db.scenario_stub.create_index(key, direction)
            except Exception as ex:
                log.debug("Could not create index for key %s, got error: %s" % (key, ex))

    def insert_pre_stub(self, scenario, stub):
        status = self.db.pre_scenario_stub.insert(dict(scenario=scenario,
                                                       stub=stub.payload))
        return 'inserted pre_scenario_stub: {0}'.format(status)

    def remove_all(self, name):
        self.db.scenario.remove({'name': name})
        self.db.scenario_stub.remove({'scenario': name})
        self.db.pre_scenario_stub.remove({'scenario': name})

    def remove_all_older_than(self, name, recorded):
        # recorded = yyyy-mm-dd
        self.db.scenario_stub.remove({
            'scenario': name,
            'recorded': {"$lt": recorded}
        })
        self.db.pre_scenario_stub.remove({
            'scenario': name,
            'recorded': {"$lt": recorded}
        })
        if not self.stub_count(name):
            self.db.scenario.remove({'name': name})


class Tracker(object):
    def __init__(self, db=None):
        self.db = db or mongo_client

    def insert(self, track, write_concern=0):
        # w=0 disables write ack 
        """
        Insert tracker doc into MongoDB and creates indexes for faster search.
        :param track: tracker object
        :param write_concern: 1 or 0, check mongo docs for more info
        :return:
        """
        forced_log_id = track.get('forced_log_id')
        if forced_log_id:
            track['_id'] = int(forced_log_id)

        return self.db.tracker.insert(track, w=write_concern)

    def _create_index(self, key=None, direction=DESCENDING):
        """
        Creates index for specific key, fails silently if index creation was unsuccessful. Key examples:
        "host" , "scenario", "scenario", "request_params.session"
        :param key: <string>
        :param direction: ASCENDING or DESCENDING (from pymongo)
        """
        if key:
            try:
                self.db.tracker.create_index(key, direction)
            except Exception as ex:
                log.debug("Could not create index (tracker collection) for key %s, got error: %s" % (key, ex))

    def find_tracker_data(self, tracker_filter, skip, limit):
        project = {'start_time': 1, 'function': 1, 'return_code': 1, 'scenario': 1,
                   'stubo_response': 1, 'duration_ms': 1, 'request_params.session': 1,
                   'delay': 1}
        if skip < 0:
            skip = 0
        # sorted on start_time descending    
        return self.db.tracker.find(tracker_filter, project).sort('start_time',
                                                                  -1).limit(limit).skip(skip)

    def find_tracker_data_full(self, _id):
        return self.db.tracker.find_one({'_id': ObjectId(_id)})

    def session_last_used(self, scenario, session, mode):
        """
        Return the date this session was last used using the
            last put/stub time (for record) or last get/response time otherwise.
        """
        if mode == 'record':
            function = 'put/stub'
        else:
            function = 'get/response'
        host, scenario_name = scenario.split(':')
        return self.db.tracker.find_one({
            'host': host,
            'scenario': scenario_name,
            'request_params.session': session,
            'function': function}, sort=[("start_time", DESCENDING)])

    def get_last_playback(self, scenario, session, start_time):
        start = self.db.tracker.find_one({
            'scenario': scenario,
            'request_params.session': session,
            'request_params.mode': 'playback',
            'function': 'begin/session',
            'start_time': {"$lt": start_time}
        }, {'start_time': 1}, sort=[("start_time", DESCENDING)])
        end = self.db.tracker.find_one({
            'scenario': scenario,
            'request_params.session': session,
            'function': 'end/session',
            'start_time': {"$gt": start_time}
        }, {'start_time': 1}, sort=[("start_time", DESCENDING)])
        if not (start or end):
            return []

        project = {'start_time': 1, 'return_code': 1, 'stubo_response': 1,
                   'response_headers': 1, 'request_headers': 1, 'duration_ms': 1,
                   'request_params': 1, 'request_text': 1, 'delay': 1}
        query = {
            'scenario': scenario,
            'request_params.session': session,
            'function': 'get/response',
            'start_time': {"$gt": start['start_time'],
                           "$lt": end['start_time']}
        }
        return self.db.tracker.find(query, project).sort("start_time",
                                                         ASCENDING)

    def get_last_recording(self, scenario, session, end):
        # find the last begin/session?mode=record from the last put/stub time 
        start = self.db.tracker.find_one({
            'scenario': scenario,
            'request_params.session': session,
            'request_params.mode': 'record',
            'function': 'begin/session',
            'start_time': {"$lt": end}
        }, {'start_time': 1}, sort=[("start_time", DESCENDING)])
        if not start:
            return []

        project = {'start_time': 1, 'return_code': 1, 'stubo_response': 1,
                   'response_headers': 1, 'request_headers': 1, 'duration_ms': 1,
                   'request_params': 1, 'request_text': 1, 'delay': 1}
        # get all the put/stubs > last begin/session?mode=record and <= last put/stub   
        query = {
            'scenario': scenario,
            'request_params.session': session,
            'function': 'put/stub',
            'start_time': {"$gt": start['start_time'],
                           "$lte": end}
        }
        log.debug('tracker.find: {0}'.format(query))
        return self.db.tracker.find(query, project).sort("start_time",
                                                         ASCENDING)


def session_last_used(scenario, session_name, mode):
    tracker = Tracker()
    return tracker.session_last_used(scenario, session_name, mode)
