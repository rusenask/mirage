"""  
    :copyright: (c) 2015 by OpenCredo.
    :license: GPLv3, see LICENSE for more details.
"""
import logging
import socket
import datetime
import tornado
from collections import OrderedDict
import json

from tornado.web import RequestHandler
from tornado.util import ObjectDict
from stubo.model.db import Tracker
from stubo.utils import tsecs_to_date, pretty_format
from stubo.cache import Cache

log = logging.getLogger(__name__)

class TrackTrace(object):
    """ Instrument processing in tracking for an area such as matching """
    
    def __init__(self, track, attr):
        self.full_tracking = 1 if track.tracking_level == 'full' else 0
        if self.full_tracking:
            if not hasattr(track, 'trace'):
                track.trace = OrderedDict()       
            self.trace = track.trace[attr] = []
        
    def info(self, summary, details=None):
        self.append(('ok', summary, details))
        
    def error(self, summary, details=None):
        self.append(('error', summary, details))
                              
    def warn(self, summary, details=None):
        self.append(('warn', summary, details))
    
    def diff(self, summary, source, transformed):
        # trace data is stored in mongo so serialize complex types (json)
        if self.full_tracking:
            info = ('ok', summary, json.dumps(source), json.dumps(transformed))
            self.trace.append((str(datetime.datetime.utcnow()), info))  
                    
    def append(self, info):
        if self.full_tracking: 
            level, summary, details = info
            if details:
                # details is a msg payload, pretty print to HTML
                if not isinstance(details, basestring):
                    details = str(details)
                info = (level, summary, pretty_format(details)) 
            self.trace.append((str(datetime.datetime.utcnow()), info))  


class BaseHandler(RequestHandler):

    def load_json(self):
        """Load JSON from the request body and store them in
        self.request.arguments, like Tornado does by default for POSTed form
        parameters.
        If JSON cannot be decoded, raises an HTTPError with status 400.
        """
        try:
            self.request.arguments = json.loads(self.request.body)
        except ValueError:
            msg = "Could not decode JSON: %s" % self.request.body
            log.debug(msg)
            raise tornado.web.HTTPError(400, msg)

    def get_json_argument(self, name, default=None):
        """Find and return the argument with key 'name' from JSON request data.
        Similar to Tornado's get_argument() method.
        """
        if default is None:
            default = self._ARG_DEFAULT
        if not self.request.arguments:
            self.load_json()
        if name not in self.request.arguments:
            if default is self._ARG_DEFAULT:
                msg = "Missing argument '%s'" % name
                log.debug(msg)
                raise tornado.web.HTTPError(400, msg)
            log.debug("Returning default argument %s, as we couldn't find "
                         "'%s' in %s" % (default, name, self.request.arguments))
            return default
        arg = self.request.arguments[name]
        log.debug("Found '%s': %s in JSON arguments" % (name, arg))
        return arg

        
class TrackRequest(BaseHandler):
    """Subclass this class to track requests.
    A track member is available to store additional state to the mongo tracker
    collection if required. This class can be initialized with a different Stats
    interface to send metrics somewhere else. The default StatsdStats sends
    to statsd/graphite.
    """   
    max_response_size = 120   
    
    def skip_dotted_names(self, d):
        # and multiple values
        return dict(
            (key, value[0] if len(value) == 1 else value) for key, value in \
                    d.iteritems() if '.' not in key) 

    def prepare(self):
        function = self.request.path
        if function.startswith('/stubo/api/'):
            function = function.partition('/stubo/api/')[-1]
        elif function == '/stubo/default/execCmds':
            # LEGACY
            function = 'exec/cmds'    

        args = self.skip_dotted_names(self.request.arguments) 
        headers = self.skip_dotted_names(self.request.headers)
        self.track = ObjectDict(request_params=args, 
                                request_headers=headers,
                                request_method=self.request.method)
        host_parts = self.request.host.partition(':')       
        host = host_parts[0].lower()
        port = host_parts[-1] 
        cache = Cache(host)
        track_setting = cache.get_stubo_setting('tracking_level')
        if not track_setting:
            track_setting = cache.get_stubo_setting('tracking_level', 
                                                    all_hosts=True)
        if not track_setting:
            track_setting = 'normal'   
        self.track.tracking_level = args.get('tracking_level', track_setting)
                    
        request_size = len(self.request.body)
        # always track put/stub recordings
        if self.track.tracking_level == 'full' or function == 'put/stub':
            self.track.request_text = self.request.body
            if function == 'get/response' and request_size <= 0:
                self.track.error = 'NoTextInBody' 
        
        self.track.update(dict(function=function,                    
                               start_time=tsecs_to_date(self.request._start_time),
                               host=host,
                               port=port,
                               remote_ip=self.request.remote_ip,
                               server=socket.getfqdn(),
                               request_size=request_size))
        log.debug('tracking: {0}:{1}'.format(self.request.host, function))


    def send_stats(self):
        stats = self.settings.get('stats')
        if stats:
            stats.send(self.settings, self.track)
           
    def on_finish(self):
        elapsed_ms = int(1000.0 * self.request.request_time())
        tracker = Tracker() 
        # handle fail early cases that don't have a response
        if not hasattr(self.track, 'stubo_response'):
            self.track.stubo_response = ''  
        return_code = self.get_status()      
        record = dict(duration_ms=elapsed_ms,
                      return_code=return_code)
        if self._headers_written:
            record['response_headers'] = self._headers
        record['response_size'] = int(self._headers.get('Content-Length',
                                len(self.track.stubo_response)))    
        self.track.update(record)

        if self.track.function == 'get/response' \
          and return_code > 399:
            self.track.request_text = self.request.body
        
        if self.track.tracking_level != 'full' and \
            self.track.response_size > self.max_response_size:
            try:
                # response will typically be json dict so convert to str to chop
                self.track.stubo_response = str(self.track.stubo_response
                                                )[:self.max_response_size]
            except Exception, e:
                log.error("unable to trim tracked stubo response: {0}".format(e))                                    
                
        if self.track.function == 'get/stublist':
            # don't want to store stub listing in the track
            self.track.stubo_response = 'stubs listed ...'
        elif self.track.function == 'exec/cmds':
            self.track.stubo_response = 'commands executed ...' 
        try:
            write_concern =  1 if self.track.function == 'put/stub' else 0
            tracker.insert(self.track, write_concern)
        except Exception, e:
            log.warn(u"error inserting track: {0}".format(e))
        self.send_stats()      
