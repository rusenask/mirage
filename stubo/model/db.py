"""  
    :copyright: (c) 2015 by OpenCredo.
    :license: GPLv3, see LICENSE for more details.
"""
from pymongo import MongoClient, DESCENDING, ASCENDING
import logging
from bson.objectid import ObjectId
from stubo.utils import asbool

default_env = {
    'port' : 27017,
    'max_pool_size' : 20,
    'tz_aware' : True,
    'db' : 'stubodb'
}  

def coerce_mongo_param(k, v):
    if k in ('port', 'max_pool_size'):
        return int(v)
    elif k in ('tz_aware',):
        return asbool(v)
    return v 

log = logging.getLogger(__name__)

mongo_client = None

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
        fiter = {}
        if name:
            filter = {'scenario' : name}
        return self.db.scenario_stub.find(filter).sort("stub.priority", 
                                                       ASCENDING)
    
    def stub_count(self, name):
        return self.get_stubs(name).count()

    def get(self, name):
        return self.db.scenario.find_one({'name' : name})
    
    def get_all(self, name=None):
        if name:
            cursor = self.db.scenario.find({'name' : name})
        else:
            cursor = self.db.scenario.find()
        return cursor   
    
    def insert(self, **kwargs):
        return self.db.scenario.insert(kwargs)
    
    def insert_stub(self, doc, stateful):
        from stubo.model.stub import Stub
        matchers = doc['stub'].contains_matchers()
        scenario = doc['scenario']
        stubs_cursor = self.get_stubs(scenario)
        if stubs_cursor.count():
            for stub in stubs_cursor:
                the_stub = Stub(stub['stub'], scenario)
                if matchers == the_stub.contains_matchers():
                    if not stateful and \
                        doc['stub'].response_body() == the_stub.response_body():
                        msg = 'duplicate stub found, not inserting.'
                        log.warn(msg)
                        return msg
                    log.debug('In scenario: {0} found exact match for matchers:'
                      ' {1}. Perform stateful update of stub.'.format(scenario,
                                                                      matchers))
                    response = the_stub.response_body()
                    response.extend(doc['stub'].response_body())
                    the_stub.set_response_body(response)   
                    self.db.scenario_stub.update(
                        {'_id': ObjectId(stub['_id'])},
                        {'$set' : {'stub' : the_stub.payload}})
                    return 'updated with stateful response'
        doc['stub'] = doc['stub'].payload       
        status = self.db.scenario_stub.insert(doc)
        return 'put {0} stub'.format(status)
    
    def remove_all(self, name):
        self.db.scenario.remove({'name' : name})
        self.db.scenario_stub.remove({'scenario' : name})
        
    def remove_all_older_than(self, name, recorded):
        # recorded = yyyy-mm-dd
        self.db.scenario_stub.remove({
            'scenario' : name,
            'recorded' :  {"$lt": recorded}
            })
        if not self.stub_count(name):
            self.db.scenario.remove({'name' : name})    
                
class Tracker(object):
    
    def __init__(self, db=None):
        self.db = db or mongo_client
        
    def insert(self, track):
        forced_log_id = track.get('forced_log_id')
        if forced_log_id:
            track['_id'] = int(forced_log_id)
        # w=0 disables write ack    
        return self.db.tracker.insert(track, w=0)
    
    def find_tracker_data(self, tracker_filter, skip, limit):
        project = {'start_time':1, 'function':1, 'return_code':1, 'scenario':1,
             'stubo_response':1, 'duration_ms':1, 'request_params.session': 1,
             'delay' : 1}
        if skip < 0:
            skip = 0
        # sorted on start_time descending    
        return self.db.tracker.find(tracker_filter, project).sort('start_time',
                                    -1).limit(limit).skip(skip)

    def find_tracker_data_full(self, _id):
        return self.db.tracker.find_one({'_id': ObjectId(_id)})
    
    def session_last_used(self, scenario, session, mode):
        ''' Return the date this session was last used using the 
            last get/response time.
        '''
        if  mode == 'record':
            function = 'put/stub'
        else:
            function = 'get/response'    
        host, scenario_name = scenario.split(':')
        return self.db.tracker.find_one({
            'host' : host, 
            'scenario' : scenario_name, 
            'request_params.session' : session, 
            'function' : function }, sort=[("start_time", DESCENDING)])
    
    def get_last_session(self, scenario, session, remote_ip, start_time,
                         mode):
        if mode == 'record':
            function = 'put/stub'
        else:
            function = 'get/response'
                
        start = self.db.tracker.find_one({
            'scenario' : scenario, 
            'request_params.session' : session,
            'request_params.mode' : mode,
            'remote_ip': remote_ip, 
            'function' : 'begin/session',
            'start_time' :  {"$lt": start_time} 
            }, {'start_time':1}, sort=[("start_time", DESCENDING)])
        end = self.db.tracker.find_one({
            'scenario' : scenario, 
            'request_params.session' : session, 
            'remote_ip': remote_ip,
            'function' : 'end/session',
            'start_time' :  {"$gt": start_time} 
            }, {'start_time':1}, sort=[("start_time", DESCENDING)])
        if not (start or end):
            return []
        
        project = {'start_time':1, 'return_code':1, 'stubo_response':1, 
                    'response_headers':1, 'request_headers':1, 'duration_ms':1, 
                    'request_params': 1, 'request_text':1, 'delay' : 1}
        query = {
            'scenario' : scenario, 
            'request_params.session' : session, 
            'function' : function,
            'remote_ip': remote_ip,
            'start_time' :  {"$gt": start['start_time'], 
                             "$lt" : end['start_time']} 
            }
        return self.db.tracker.find(query, project).sort("start_time", 
                                                         ASCENDING)
        
    def get_last_playback(self, scenario, session, remote_ip, start_time):
        return self.get_last_session(scenario, session, remote_ip, start_time,
                                     'playback')
      
    def get_last_recording(self, scenario, session, remote_ip, start_time):
        return self.get_last_session(scenario, session, remote_ip, start_time,
                                    'record')  
          
        
def session_last_used(scenario, session_name, mode):
    tracker = Tracker()
    return tracker.session_last_used(scenario, session_name, mode)        
           
           
            
        
            
