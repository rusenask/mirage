"""  
    :copyright: (c) 2015 by OpenCredo.
    :license: GPLv3, see LICENSE for more details.
"""
import logging
import json
from urlparse import urlparse, urljoin, parse_qs
from urllib import urlencode
from StringIO import StringIO
import os.path
from stubo.exceptions import StuboException, exception_response
from stubo.model.stub import create
from .importer import Importer, UrlFetch

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


class TextCommandsImporter(Importer):
    def run_all(self, data):
        return self.run_cmds(data)

    def parse(self, commands):
        sio = StringIO(commands)
        lines = [line.strip() for line in sio if not line.startswith('#') and line.strip()]
        return lines

    def run_cmds(self, cmds):
        log.debug('cmds={0}'.format(cmds))
        urls = [urlparse(cmd) for cmd in cmds]
        priority = 0
        responses = []
        for url in urls:
            response = [url.geturl()]
            if 'put/stub' in url.path:
                priority += 1
            try:
                # TODO: return (status_code, error) if error  
                response.append(self.run_command(url, priority))
            except StuboException, stubo_error:
                response.extend((stubo_error.code, str(stubo_error)))
            except Exception, e:
                response.extend((500, str(e)))
            responses.append(tuple(response))
        return {'commands': responses}

    def run_command(self, url, priority):
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
            response, _, status_code = UrlFetch().get(import_cmd_url)
            return status_code

        elif url.path == 'put/stub':
            # Note: delay policy is an optional param, the text matchers & 
            # response start after the first ","
            query, _, matchers_response = url.query.partition(',')
            query_params = parse_qs(query)
            delist_arguments(query_params)
            if 'session' not in query_params:
                raise exception_response(400, title="Missing 'session' param in"
                                                    " query: {0}".format(url.query))
            if 'priority' not in query_params:
                query_params['priority'] = priority
            matchers_response = u''.join(matchers_response.split()).strip()
            matchers_response = matchers_response.split(',')
            response_fname = matchers_response[-1].strip()
            matchers = matchers_response[:-1]
            request_matchers = []
            for matcher in matchers:
                if matcher[:4] == 'url=':
                    matcher_data_url = matcher[4:]
                    matcher_text, _, _ = UrlFetch().get(matcher_data_url)
                elif matcher[:5] == 'text=':
                    matcher_text = matcher[5:]
                else:
                    matcher_data_url = urljoin(parent_path, matcher)
                    matcher_text, _, _ = UrlFetch().get(matcher_data_url)
                request_matchers.append(matcher_text)

            if response_fname[:4] == 'url=':
                response_data_url = response_fname[4:]
                response_text, _, _ = UrlFetch().get(response_data_url)
            elif response_fname[:5] == 'text=':
                response_text = response_fname[5:]
            else:
                response_data_url = urljoin(parent_path, response_fname)
                response_text, hdrs, _ = UrlFetch().get(response_data_url)
                if 'application/json' in hdrs["Content-Type"]:
                    try:
                        response_text = json.dumps(response_text)
                    except Exception:
                        pass

            if not response_text:
                raise exception_response(400,
                                         title="put/stub response text can not be empty.")

            stub_payload = create(request_matchers, response_text)
            cmd_path = url.path + '?{0}'.format(urlencode(query_params))
            url = self.get_url(cmd_path)
            log.debug(u'run_command: {0}'.format(url))
            response = UrlFetch().post(url, data=None, json=stub_payload)
            return response.status_code

        elif url.path == 'get/response':
            # get/response?session=foo_1, my.request
            query, _, request_fname = url.query.partition(',')
            query_params = parse_qs(query)
            if 'session' not in query_params:
                raise exception_response(400, title="Missing 'session' param in"
                                                    " query: {0}".format(url.query))
            request_fname, _, header_args = request_fname.partition(',')
            request_fname = request_fname.strip()

            if request_fname[:4] == 'url=':
                request_data_url = request_fname[4:]
                request_text, _, _ = UrlFetch().get(request_data_url)
            elif request_fname[:5] == 'text=':
                request_text = request_fname[5:]
            else:
                request_data_url = urljoin(parent_path, request_fname)
                request_text, _, _ = UrlFetch().get(request_data_url)
            data = request_text
            cmd_path = url.path + '?{0}'.format(query)
            url = self.get_url(cmd_path)
            log.debug(u'run_command: {0}'.format(url))
            if isinstance(data, dict):
                # payload is json
                encoded_data = json.dumps(data)
            else:
                encoded_data = data.encode('utf-8')
            headers = {'Stubo-Request-Method': 'POST'}
            if header_args:
                headers.update(dict(x.split('=') for x in header_args.split(',')))
            response = UrlFetch().post(url, data=encoded_data, headers=headers)
            return response.status_code

        elif url.path == 'put/delay_policy':
            url = self.get_url(cmd_path)
            log.debug('run_command: {0}, data={1}'.format(url, data))
            _, _, status_code = UrlFetch().get(url)
            return status_code

        url = self.get_url(cmd_path)
        log.debug(u'run_command: {0}'.format(url))
        encoded_data = data.encode('utf-8')
        response = UrlFetch().post(url, data=encoded_data)
        return response.status_code
