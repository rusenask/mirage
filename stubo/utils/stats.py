"""  
    :copyright: (c) 2015 by OpenCredo.
    :license: GPLv3, see LICENSE for more details.
"""
import logging

log = logging.getLogger(__name__)

class Stats(object):
        
    def send(self, settings, track):
        pass
    
class StatsdStats(Stats):
        
    def send(self, settings, track):
        """ track data
        function: get/response
        scenario: first
        start_time: 2013-07-08 10:36:38.455000+00:00
        return_code: 200
        server: my.server
        request_size: 32
        host: somehost:8001
        session: first_1
        response_size: 14
        duration_ms: 8
        stubo_response: Hello 2 World
        _id: 51da7a1631588e043a192c6d
        remote_ip: ::1
        """
        try:
            # e.g. <cluster>.<host>.stuboapi.<function>.latency
            statsd_client = settings['statsd_client']
            cluster = settings['cluster_name']
            host = track['host'].replace('.', '_')          
            remote_ip = track.get('remote_ip', 'unknown').replace(
                '.', '_').replace(':', '_')
            function = track['function'].replace('/', '_')
            latency = track['duration_ms']
            request_size = track['request_size']
            response_size = track.get('response_size')
            return_code = track['return_code']
            delay = track.get('delay')
            root = '{0}.{1}.stuboapi.{2}'.format(cluster, host, function) 
            log.debug('statsd namespace: {0}'.format(root))

            with statsd_client.pipeline() as pipe:
                if delay:
                    latency = latency - delay
                    pipe.timing('{0}.delay'.format(root), delay)
                pipe.timing('{0}.latency'.format(root), latency)
                pipe.gauge('{0}.sent'.format(root), request_size)
                if response_size:    
                    pipe.gauge('{0}.received'.format(root), response_size)
                if return_code < 400:
                    status = 'success'  
                else:
                    status = 'failure.{0}'.format(return_code)
                pipe.incr('{0}.{1}'.format(root, status))
                # track client call count with a separate counter
                pipe.incr('{0}.{1}.client.{2}'.format(cluster, host, remote_ip))

        except Exception:
            log.info('error sending to statsd, track={0}'.format(track),
                     exc_info=True)       