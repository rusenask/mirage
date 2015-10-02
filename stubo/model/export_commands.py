"""  
    :copyright: (c) 2015 by OpenCredo.
    :license: GPLv3, see LICENSE for more details.
"""
import os
import zipfile
import tarfile
import shutil
import logging
import time
import json
from urllib import urlencode

import codecs

from stubo.model.db import Scenario, Tracker

from stubo.model.stub import Stub
from stubo.exceptions import exception_response
from stubo import version
from stubo.cache import Cache

from stubo.utils import asbool, get_export_links, get_hostname

log = logging.getLogger(__name__)


def export_stubs_to_commands_format(handler, scenario_name_key, scenario_name, session_id,
                                    runnable, playback_session, static_dir, export_dir):
    """

    :param handler:
    :param scenario_name_key:
    :param scenario_name:
    :param session_id:
    :param runnable:
    :param playback_session:
    :param static_dir:
    :param export_dir:
    :return: :raise exception_response:
    """
    # cache = Cache(get_hostname(handler.request))
    # scenario_name_key = cache.scenario_key_name(scenario_name)

    # use user arg or epoch time

    if not session_id:
        session_id = int(time.time())
    # session_id = handler.get_argument('session_id', int(time.time()))
    session = u'{0}_{1}'.format(scenario_name, session_id)
    cmds = [
        'delete/stubs?scenario={0}'.format(scenario_name),
        'begin/session?scenario={0}&session={1}&mode=record'.format(
            scenario_name, session)
    ]
    files = []
    scenario = Scenario()
    # get scenario pre stubs for specified scenario
    stubs = list(scenario.get_pre_stubs(scenario_name_key))
    if stubs:
        for i in range(len(stubs)):
            entry = stubs[i]
            stub = Stub(entry['stub'], scenario_name_key)
            # if stub is rest - matcher may be None, checking that
            if stub.contains_matchers() is None:
                cmds.append('# Stub skipped since no matchers were found. Consider using .yaml format for additional '
                            'capabilities')
                # skipping to next stub, this stub is not compatible with .commands format
                continue
            matchers = [('{0}_{1}_{2}.textMatcher'.format(session, i, x), stub.contains_matchers()[x])
                        for x in range(len(stub.contains_matchers()))]
            matchers_str = ",".join(x[0] for x in matchers)
            url_args = stub.args()
            url_args['session'] = session
            module_info = stub.module()
            if module_info:
                # Note: not including put/module in the export, modules are shared
                # by multiple scenarios.
                url_args['ext_module'] = module_info['name']
                url_args['stub_created_date'] = stub.recorded()
                url_args['stubbedSystemDate'] = module_info.get('recorded_system_date')
                url_args['system_date'] = module_info.get('system_date')
            url_args =  urlencode(url_args)
            responses = stub.response_body()
            assert(len(responses) == 1)
            response = responses[0]
            response = ('{0}_{1}.response'.format(session, i), response)
            cmds.append('put/stub?{0},{1},{2}'.format(url_args, matchers_str,
                                                      response[0]))
            files.append(response)
            files.extend(matchers)
    else:
        cmds.append('put/stub?session={0},text=a_dummy_matcher,text=a_dummy_response'.format(session))
    cmds.append('end/session?session={0}'.format(session))

    runnable_info = dict()

    # if this scenario is runnable
    if runnable:
        # playback_session = handler.get_argument('playback_session', None)
        if not playback_session:
            raise exception_response(400,
                                     title="'playback_session' argument required with 'runnable")
        runnable_info['playback_session'] = playback_session

        tracker = Tracker()
        last_used = tracker.session_last_used(scenario_name_key,
                                              playback_session, 'playback')
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

        cmds.append('begin/session?scenario={0}&session={1}&mode=playback'.format(
            scenario_name, session))
        number_of_requests = len(playback)
        runnable_info['number_of_playback_requests'] = number_of_requests
        for nrequest in range(number_of_requests):
            track = playback[nrequest]
            request_text = track.get('request_text')
            if not request_text:
                raise exception_response(400, title='Unable to obtain playback details, was full tracking enabled?')

            request_file_name = '{0}_{1}.request'.format(session, nrequest)
            files.append((request_file_name, request_text))
            stubo_response_text = track['stubo_response']
            if not isinstance(stubo_response_text, basestring):
                stubo_response_text = unicode(stubo_response_text)
            stubo_response_file_name = '{0}_{1}.stubo_response'.format(session, nrequest)
            files.append((stubo_response_file_name, stubo_response_text))
            url_args = track['request_params']
            url_args['session'] = session
            url_args =  urlencode(url_args)
            cmds.append(u'get/response?{0},{1}'.format(url_args,
                                                       request_file_name))
        cmds.append('end/session?session={0}'.format(session))

    files.append(('{0}.commands'.format(scenario_name),
                  b"\r\n".join(cmds)))

    # checking whether export dir parameter is provided
    if not export_dir:
        export_dir = scenario_name_key.replace(':', '_')
    export_dir_path = os.path.join(static_dir, 'exports', export_dir)

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
    # getting links
    links = get_export_links(handler, scenario_name_key, files)

    return links
