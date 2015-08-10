"""  
    :copyright: (c) 2015 by OpenCredo.
    :license: GPLv3, see LICENSE for more details.
"""
import time
import logging
import os
import zipfile
import tarfile
import shutil
import codecs
import yaml
import json

from .db import Scenario, Tracker
from .stub import Stub, create
from .request import StuboRequest
from stubo.exceptions import exception_response
from tornado.util import ObjectDict


DummyModel = ObjectDict

log = logging.getLogger(__name__)

dummy_stub = create('dummy matcher', 'dummy response')

YAML_FORMAT_SUBDIR = 'yaml_format'

class Exporter(object):
    
    def __init__(self, static_dir):
        self.static_dir = static_dir
    
    def export(self, scenario, runnable=False, playback_session=None, 
               session_id=None, export_dir=None):
        
        host, scenario_name = scenario.split(':')
        # use session_id arg or epoch time
        session_id = session_id or int(time.time()) 
        session = u'{0}_{1}'.format(scenario_name, session_id)

        export_dir = (export_dir or scenario).replace(':', '_')

        # specifying sub directory to store yaml configuration

        export_dir += '/' + YAML_FORMAT_SUBDIR
        
        # write this at the top of the yaml
        comment = '# use the session_id url arg from exec/cmds if supplied otherwise the one set from the get/export'    
        session_template_var = "{{% set session = globals().get('session_id',[None])[0] or '{0}' %}}".format(session)
      
        files = [] 
        header = dict(scenario=scenario_name, 
                      session='{{session}}',
                      stubs=[])
        export_payload = dict(recording=header)
        scenario_db = Scenario()
        stubs = list(scenario_db.get_pre_stubs(scenario))
        if len(stubs) > 0: 
            for i in range(len(stubs)):
                entry = stubs[i]
                stub = Stub(entry['stub'], scenario)
                # remove scenario & session from stub args
                args = stub.args()
                args.pop('scenario', None)
                args.pop('session', None)
                stub.set_args(args)   
                stub_file = ('{0}_{1}.json'.format(session, i), 
                             json.dumps(stub.payload, indent=3))
                export_payload['recording']['stubs'].append(dict(file=stub_file[0]))
                files.append(stub_file)    
        else:
            files.append(('{0}_0.json'.format(session), json.dumps(dummy_stub, 
                                                                   indent=3))) 
        
        runnable_info = {}
        if runnable:
            playback_header = dict(scenario=scenario_name, 
                                   session='{{session}}',
                                   requests=[])
            export_payload['playback'] = playback_header
            runnable_info = self.export_playback(host, export_payload, files, 
                                                 session, playback_session)    
            runnable_info['playback_session'] = playback_session
             
        yaml_export = yaml.safe_dump(export_payload, encoding='utf-8', 
                                     allow_unicode=True, 
                                     default_flow_style=False) 
        yaml_lines = u"\n".join([comment, session_template_var, yaml_export]) 
        files.append(('{0}.yaml'.format(scenario_name), yaml_lines)) 
        export_dir_path = self.write_files(scenario_name, export_dir, files)  
        return (export_dir_path, files, runnable_info)  
    
    def export_playback(self, host, export_payload, files, session,
                        playback_session):
        playback_payload = export_payload['playback']
        scenario_name = playback_payload['scenario']
        scenario = u'{0}:{1}'.format(host, scenario_name)
        runnable_info = dict()   
        tracker = Tracker()    
        last_used = tracker.session_last_used(scenario, playback_session, 
                                              'playback')
        if not last_used:
            raise exception_response(400, 
                        title="Unable to find playback session")  
        runnable_info['last_used'] = dict(remote_ip=last_used['remote_ip'],
                                          start_time=str(last_used['start_time']))      
        playback = tracker.get_last_playback(scenario_name, playback_session,
                                             last_used['start_time']) 
        playback = list(playback)
        if not playback:
            raise exception_response(400, 
              title="Unable to find a playback for scenario='{0}', playback_session='{1}'".format(scenario_name, playback_session))
   
        number_of_requests = len(playback)
        runnable_info['number_of_playback_requests'] = number_of_requests
        for nrequest in range(number_of_requests):
            track = playback[nrequest]
            request_text = track.get('request_text')
            if not request_text:
                raise exception_response(400, title='Unable to obtain playback details, was full tracking enabled?')
            stubo_request = StuboRequest(DummyModel(headers=track.get('request_headers'),
                                                    body=request_text))
            vars = track.get('request_params')
            vars.pop('session', None)
            vars.pop('scenario', None)
            request_payload = dict(body=stubo_request.body,
                                   method=stubo_request.method,
                                   host=stubo_request.host,
                                   uri=stubo_request.uri,
                                   path=stubo_request.path,
                                   query=stubo_request.query,
                                   headers=stubo_request.headers)
                
            request_file_name = '{0}_{1}.request'.format(session, nrequest)
            files.append((request_file_name, json.dumps(request_payload, indent=3)))
            # export a response for comparison
            stubo_response_text = track['stubo_response']
            if not isinstance(stubo_response_text, basestring):
                stubo_response_text = unicode(stubo_response_text)
            response_payload = dict(status=track.get('return_code'),
                                    body=stubo_response_text,
                                    headers=track.get('response_headers'))
           
            stubo_response_file_name = '{0}_{1}.stubo_response'.format(session, 
                                                                       nrequest)
            playback_payload['requests'].append(dict(
                                file=request_file_name,
                                vars=vars,
                                response=stubo_response_file_name))
            files.append((stubo_response_file_name, json.dumps(response_payload, 
                                                               indent=3)))
        return runnable_info        
            
    def write_files(self, scenario_name, export_dir, files):
        export_dir_path = os.path.join(self.static_dir, 'exports', export_dir)
    
        if os.path.exists(export_dir_path):
            shutil.rmtree(export_dir_path)
        os.makedirs(export_dir_path)
    
        archive_name = os.path.join(export_dir_path, scenario_name)
        zout = zipfile.ZipFile(archive_name+'.zip', "w")
        tar = tarfile.open(archive_name+".tar.gz", "w:gz")
        for finfo in files:
            fname, contents = finfo
            file_path = os.path.join(export_dir_path, fname)
            with codecs.open(file_path, mode='wb', encoding='utf-8') as f:
                f.write(contents)
            f.close()
            tar.add(file_path, fname)
            zout.write(file_path, fname)
        tar.close()     
        zout.close() 
        shutil.copy(archive_name+'.zip', archive_name+'.jar')  
    
        files.extend([(scenario_name+'.zip',), (scenario_name+'.tar.gz',),
                      (scenario_name+'.jar',)])   
        return export_dir_path           