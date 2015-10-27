"""  
    :copyright: (c) 2015 by OpenCredo.
    :license: GPLv3, see LICENSE for more details.
"""
from urlparse import urlparse, urljoin
from urllib import urlencode
import os.path
import logging
import json

import requests
import yaml

from stubo.exceptions import StuboException, exception_response
from stubo.ext import roll_date, today_str, parse_xml
from stubo.utils import as_date, run_template

log = logging.getLogger(__name__)


class UriLocation(object):
    """
    Return the URI if the path is fully formed or construct it based on the
    input request.

     from stubo.testing import DummyRequestHandler
     handler = DummyRequestHandler()
     loc = UriLocation(handler.request)
     loc.get_base_url()
    'http://localhost:8001'
     loc('/foo')
    ('http://localhost:8001/foo', 'foo')
     loc('http://mongo.com:9000/foo')
    ('http://mongo.com:9000/foo', 'foo')
    """

    def __init__(self, request):
        self.request = request

    def get_base_url(self):
        return "{0}://{1}".format(self.request.protocol, self.request.host)

    def __call__(self, path):
        """
        path is either a local ref or full url
        """
        uri = urlparse(path)
        url = uri.geturl()
        if not uri.netloc:
            url = urljoin(self.get_base_url(), url)
        return url, os.path.basename(path)


class UrlFetch(object):
    def raise_on_error(self, response, url):
        status = response.status_code
        if status != 200:
            if status == 404:
                msg = "File not found using url: {0}".format(url)
                raise exception_response(response.status_code,
                                         title=msg)
            else:
                json_response = None
                try:
                    json_response = response.json()
                except Exception:
                    pass
                if json_response and 'error' in json_response:
                    # its one of ours, reconstruct the error 
                    raise exception_response(response.status_code,
                                             title=json_response['error'].get('message'))
                if response.status_code > 399:
                    raise exception_response(response.status_code,
                                             title="Error executing request '{0}', reason={1}".format(
                                                 url, response.reason))

    def get(self, url, **kwargs):
        log.debug(u'fetch url: {0}, {kwargs}'.format(url, kwargs=kwargs))
        response = requests.get(url, verify=False, **kwargs)
        self.raise_on_error(response, url)
        if 'application/json' in response.headers["Content-Type"]:
            return response.json(), response.headers, response.status_code
        else:
            if not response.encoding:
                try:
                    return response.content.decode('utf-8'), response.headers, response.status_code
                except Exception:
                    return response.content, response.headers, response.status_code
            elif response.encoding == 'ISO-8859-1' and 'xml' in response.headers["Content-Type"]:
                # work around for https://github.com/kennethreitz/requests/issues/2086
                try:
                    return response.content.decode('utf-8'), response.headers, response.status_code
                except Exception:
                    return response.content, response.headers, response.status_code
            else:
                return response.text, response.headers, response.status_code

    def post(self, url, data, **kwargs):
        log.debug(u'post url: {0}'.format(url))
        response = requests.post(url, data=data, **kwargs)
        if 'get/response' in url and response.status_code == 400 and \
                        'E017' in response.content:
            # handle no response found case
            log.warn('no response found for request')
        else:
            self.raise_on_error(response, url)
        return response


class Importer(object):
    api_base = 'stubo/api/'

    def __init__(self, location, cmd_file_url=None):
        self.location = location
        self.cmd_file_url = cmd_file_url or ''
        self.parent_path = self.location(os.path.dirname(self.cmd_file_url))[0] + '/'

    def get_url(self, cmd, **args):
        cmd_path = cmd if not args else cmd + '?{0}'.format(urlencode(args))
        return self.location(urljoin(Importer.api_base, cmd_path))[0]

    def run(self):
        if not self.cmd_file_url:
            raise exception_response(500,
                                     title='run requires a cmd_file_url input to the ctor.')
        cmds, _, _ = UrlFetch().get(self.location(self.cmd_file_url)[0])
        cmds_expanded = run_template(cmds,
                                     # utility functions   
                                     roll_date=roll_date,
                                     today=today_str,
                                     as_date=as_date,
                                     parse_xml=parse_xml,
                                     **self.location.request.arguments)
        try:
            payload = self.parse(cmds_expanded)
        except Exception, e:
            raise exception_response(400, title="Unable to parse '{0}', error={1}".format(self.cmd_file_url, e))

        responses = self.run_all(payload)

        number_of_requests = number_of_errors = 0
        for k, v in responses.iteritems():
            number_of_requests += len(v)
            number_of_errors += len([x for x in v if x[1] > 399])

        return {
            'executed_commands': responses,
            'number_of_requests': number_of_requests,
            'number_of_errors': number_of_errors
        }


class YAMLImporter(Importer):
    def parse(self, data):
        return yaml.load(data)

    def run_all(self, data):
        response = {}
        commands = data.get('commands')
        if commands:
            response['commands'] = self.run_cmds(commands)
        recording = data.get('recording')
        if recording:
            response['recording'] = self.run_recording(recording)
        playback = data.get('playback')
        if playback:
            response['playback'] = self.run_playback(playback)
        return response

    def run_cmds(self, commands):
        """ [
              {'put/module':
                 {'vars':
                     {'name': 'https://github.com/somerepo/myexit.py'}
                 }
               },
              {'put/delay_policy':
                  {'vars':
                     {'delay_type': 'fixed', 'name': 'slow', 'milliseconds': 1000}
                  }
              }
            ]
        """
        log.debug('cmds={0}'.format(commands))
        responses = []
        for cmd in commands:
            # there is only 1 key
            cmd, args = cmd.items()[0]
            try:
                status_code = self.run_command(cmd, **args.get('vars'))
            except StuboException, stubo_error:
                status_code = stubo_error.code
            except Exception, e:
                status_code = 500
            responses.append((cmd, status_code))
        return responses

    def run_command(self, cmd, **args):
        url = self.get_url(cmd, **args)
        log.debug(u'run_command: {0}'.format(url))
        _, _, status_code = UrlFetch().get(url)
        return status_code

    def run_recording(self, recording):
        scenario_args = dict(scenario=recording['scenario'],
                             session=recording['session'])
        recordings = []
        recordings.append(('delete/stubs', self.run_command('delete/stubs',
                                                            **scenario_args)))
        recordings.append(('begin/session', self.run_command('begin/session',
                                                             mode='record', **scenario_args)))
        for stub in recording['stubs']:
            try:
                if 'file' in stub:
                    stub_data_url = urljoin(self.parent_path, stub['file'])
                    stub_payload, _, _ = UrlFetch().get(stub_data_url)
                elif 'json' in stub:
                    stub_payload = stub['json']
                else:
                    raise exception_response(400, title="A stub definition must "
                                                        "contain either a 'file' location key or a 'json' key that "
                                                        "defines an inplace payload.")
                vars = stub.get('vars', {})
                vars.update(scenario_args)
                url = self.get_url('put/stub', **vars)
                log.debug(u'run_command: {0}'.format(url))
                if not isinstance(stub_payload, dict):
                    stub_payload = json.loads(stub_payload)
                response = UrlFetch().post(url, data=None, json=stub_payload)
                recordings.append(('put/stub', response.status_code))
            except Exception, e:
                recordings.append(('put/stub', str(e)))
        recordings.append(('end/session', self.run_command('end/session',
                                                           mode='record', **scenario_args)))
        return recordings

    def run_playback(self, playback):
        scenario_args = dict(scenario=playback['scenario'],
                             session=playback['session'])
        plays = []
        plays.append(('begin/session', self.run_command('begin/session',
                                                        mode='playback', **scenario_args)))
        for request in playback['requests']:
            """
             {"method": "GET",
               "body": '{"body": {"cmd": {"a": "b"}}',
               "headers" : {
                  "Content-Type" : "application/json",
                  "X-Custom-Header" : "1234"
               }}
            """
            try:
                if 'file' in request:
                    request_data_url = urljoin(self.parent_path, request['file'])
                    payload, _, _ = UrlFetch().get(request_data_url)
                elif 'json' in request:
                    payload = request['json']
                else:
                    raise exception_response(400, title="A request definition "
                                                        "must contain either a 'file' location key or a 'json' "
                                                        "key that defines an inplace payload.")
                if isinstance(payload, basestring):
                    payload = json.loads(payload)
                vars = request.get('vars', {})
                vars.update(scenario_args)
                url = self.get_url('get/response', **vars)
                log.debug(u'run_command: {0}'.format(url))
                body = payload['body']
                if isinstance(body, dict):
                    # payload is json
                    encoded_data = json.dumps(body)
                else:
                    encoded_data = body.encode('utf-8')

                headers = {
                    'Stubo-Request-URI': payload.get('uri'),
                    'Stubo-Request-Method': payload.get('method', 'POST'),
                    'Stubo-Request-Headers': payload.get('headers', ''),
                    'Stubo-Request-Host': payload.get('host'),
                    'Stubo-Request-Path': payload.get('path'),
                    'Stubo-Request-Query': payload.get('query', '')
                }

                response = UrlFetch().post(url, data=encoded_data, headers=headers)
                plays.append(('get/response', response.status_code))
            except Exception, e:
                plays.append(('get/response', 500, str(e)))
        plays.append(('end/session', self.run_command('end/session',
                                                      mode='playback', **scenario_args)))
        return plays
