"""  
    :copyright: (c) 2015 by OpenCredo.
    :license: GPLv3, see LICENSE for more details.
"""
import logging
import json
from urlparse import urlparse, urljoin, parse_qs
from urllib import urlencode
import requests
from StringIO import StringIO
import os.path
from tornado.template import Template
from stubo.exceptions import exception_response
from stubo.ext import roll_date, today_str, parse_xml
from stubo.utils import as_date
from stubo.model.stub import create

log = logging.getLogger(__name__)

verbs = frozenset(['get/response',
                   'begin/session',
                   'end/session',
                   'end/sessions',
                   'put/stub',
                   'delete/stubs',
                   'get/stubcount',
                   'get/stublist',
                   'get/export',
                   'get/delay_policy',
                   'put/delay_policy',
                   'delete/delay_policy',
                   'put/module',
                   'delete/module',
                   'get/modulelist',
                   'import/bookmarks',
                   'put/bookmark',
                   'jump/bookmark',
                   'get/stats',
                   'exec/cmds',
                   'put/setting',
                   'get/setting'
                 ])

form_input_cmds = frozenset(['delete/stubs',
                             'begin/session',
                             'put/delay_policy',
                             'end/session',
                             'get/export',
                             'put/delay_policy',
                             'delete/delay_policy',
                             'put/module',
                             'delete/module',
                             'delete/modules',
                             'get/setting',
                             'put/setting'])

api_base = 'stubo/api/'

def delist_arguments(args):
    """
    Takes a dictionary, 'args' and de-lists any single-item lists then
    returns the resulting dictionary.

    In other words, {'foo': ['bar']} would become {'foo': 'bar'}
    """
    for arg, value in args.items():
        if len(value) == 1:
            args[arg] = value[0]
    return args

class UriLocation(object):
    '''
    Return the URI if the path is fully formed or construct it based on the 
    input request.
    
    >>> from stubo.testing import DummyRequestHandler
    >>> handler = DummyRequestHandler()
    >>> loc = UriLocation(handler.request)
    >>> loc.get_base_url()
    'http://localhost:8001'
    >>> loc('/foo')
    ('http://localhost:8001/foo', 'foo')
    >>> loc('http://mongo.com:9000/foo')
    ('http://mongo.com:9000/foo', 'foo')
    '''
    
    def __init__(self, request):
        self.request = request
        
    def get_base_url(self):
        return "{0}://{1}".format(self.request.protocol, self.request.host)
                       
    def __call__(self, path):
        ''' path is either a local ref or full url'''
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
        response = requests.get(url, **kwargs)
        self.raise_on_error(response, url)
        if 'application/json' in response.headers["Content-Type"]:
            return response.json(), response.headers
        else:
            if not response.encoding:
                try:
                    return response.content.decode('utf-8'), response.headers
                except Exception:    
                    return response.content, response.headers
            else:          
                return response.text, response.headers
        
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
            

class StuboCommandFile(object):
    
    def __init__(self, request, cmd_file_url=None):   
        self.location = UriLocation(request)
        self.cmd_file_url = cmd_file_url or ''
        
    def run(self):
        if not self.cmd_file_url:
            raise exception_response(500,
                title='run requires a cmd_file_url input to the ctor.')
        response, _ = UrlFetch().get(self.location(self.cmd_file_url)[0])
        t = Template(response)
        cmds_templated = t.generate(today=today_str,
                                    as_date=as_date,
                                    roll_date=roll_date,
                                    parse_xml=parse_xml,
                                    **self.location.request.arguments)
        cmds = self.parse_commands(cmds_templated)
        self.run_cmds(cmds)
        return cmds
    
    def run_cmds(self, cmds):
        log.debug('cmds={0}'.format(cmds))
        urls = [urlparse(cmd) for cmd in cmds]
        for url in urls:  
            self.run_command(url)
    
    def run_command(self, url):
        data = ''
        log.debug('url.path={0}'.format(url.path))
        cmd_path = url.geturl()
        parent_path = self.location(os.path.dirname(self.cmd_file_url))[0] + '/'
        if url.path == 'import/bookmarks':
            loc = parse_qs(url.query).get('location')
            if loc:
                loc = loc[0]
            else:
                raise exception_response(400,
                    title="missing 'location' param executing import/bookmarks")
            target_url = self.location(urljoin(parent_path, loc))[0]
            log.debug('run_command: {0}'.format(target_url))
            import_cmd_url = self.location(
              'stubo/api/import/bookmarks?location={0}'.format(target_url))[0]
            response, _ = UrlFetch().get(import_cmd_url)
            return
        
        elif url.path == 'put/stub': 
            # Note: delay policy is an optional param, the text matchers & 
            # response start after the first ","
            query, _, matchers_response = url.query.partition(',') 
            query_params = parse_qs(query)
            delist_arguments(query_params)
            if 'session' not in query_params:
                raise exception_response(400, title="Missing 'session' param in"
                  " query: {0}".format(url.query))
            matchers_response = u''.join(matchers_response.split()).strip() 
            matchers_response = matchers_response.split(',')  
            response_fname = matchers_response[-1].strip()
            matchers = matchers_response[:-1]
            request_matchers = []
            for matcher in matchers:
                if matcher[:4] == 'url=':
                    matcher_data_url = matcher[4:]
                    matcher_text, _ = UrlFetch().get(matcher_data_url)
                elif matcher[:5] == 'text=':
                    matcher_text = matcher[5:]
                else:
                    matcher_data_url = urljoin(parent_path, matcher)
                    matcher_text, _ = UrlFetch().get(matcher_data_url)
                request_matchers.append(matcher_text)

            if response_fname[:4] == 'url=':
                response_data_url = response_fname[4:]
                response_text, _ = UrlFetch().get(response_data_url)
            elif response_fname[:5] == 'text=':
                response_text = response_fname[5:]
            else:
                response_data_url = urljoin(parent_path, response_fname)
                response_text, _ = UrlFetch().get(response_data_url)
            
            if not response_text:
                raise exception_response(400, 
                    title="put/stub response text can not be empty.") 
            
            stub_payload = create(request_matchers, response_text)
            cmd_path = url.path + '?{0}'.format(urlencode(query_params))
            url = self.location(urljoin(api_base, cmd_path))[0]
            log.debug(u'run_command: {0}'.format(url))
            UrlFetch().post(url, data=None, json=stub_payload)
            return
        
        elif url.path == 'get/response':    
            # get/response?session=foo_1, my.request
            query, _, request_fname = url.query.partition(',') 
            query_params = parse_qs(query)
            if 'session' not in query_params:
                raise exception_response(400, title="Missing 'session' param in"
                  " query: {0}".format(url.query))         
            request_fname = request_fname.strip()
            
            if request_fname[:4] == 'url=':
                request_data_url = request_fname[4:]
                request_text, _ = UrlFetch().get(request_data_url)
            elif request_fname[:5] == 'text=':
                request_text = request_fname[5:]
            else:
                request_data_url = urljoin(parent_path, request_fname)
                request_text, _ = UrlFetch().get(request_data_url)
            data = request_text
            cmd_path = url.path + '?{0}'.format(query)

        elif url.path == 'put/delay_policy':
            url = self.location(urljoin(api_base, cmd_path))[0]
            log.debug('run_command: {0}, data={1}'.format(url, data))
            response, _ = UrlFetch().get(url)
            return

        url = self.location(urljoin(api_base, cmd_path))[0]
        log.debug(u'run_command: {0}'.format(url))
        encoded_data = data.encode('utf-8')
        UrlFetch().post(url, data=encoded_data)

    def parse_commands(self, commands):
        sio = StringIO(commands)
        lines = [line.strip() for line in sio if not line.startswith('#') \
                 and line.strip()]
        return lines
