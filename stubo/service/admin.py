"""  
    :copyright: (c) 2015 by OpenCredo.
    :license: GPLv3, see LICENSE for more details.
"""
import logging
from stubo.utils import get_graphite_datapoints, get_graphite_stats
from stubo.exceptions import exception_response
from stubo import version

log = logging.getLogger(__name__)


def get_stats(handler):
    # cluster.host
    # "cluster1.ahost or cluster1.*",
    response = {
        'version': version
    }
    cluster = handler.get_argument('cluster', handler.settings['cluster_name'])
    host = handler.get_argument('host', '*')
    cluster_host_server = '{0}.{1}'.format(cluster, host)
    metric = handler.get_argument('metric', 'latency')
    if metric == 'latency':
        target = 'averageSeries(stats.timers.stubo.{0}.stuboapi.get_response.latency.mean_90)'.format(
            cluster_host_server)
        percent_above_value = int(handler.get_argument('percent_above_value', 50))
    else:
        raise exception_response(400,
                                 title="metric '{0}' parameter not supported.".format(metric))

    server = handler.settings.get('graphite.host')
    auth = (handler.settings.get('graphite.user'),
            handler.settings.get('graphite.passwd'))
    from_str = handler.get_argument('from', '-1hours')
    to_str = handler.get_argument('to', 'now')
    json_response, hdrs, status_code = get_graphite_stats(server, auth,
                                                          target=target, from_str=from_str, to_str=to_str)
    if status_code != 200 or (hdrs['content-type'] != 'application/json'):
        raise exception_response(500,
                                 title='unexpected response from graphite => {0}: {1}'.format(
                                     hdrs, json_response))

    ts = get_graphite_datapoints(json_response, target)
    slow = [x for x in ts if x[0] > percent_above_value]
    pcent = len(slow) / float(len(ts)) * 100
    response['data'] = {
        'target': target,
        'metric': metric,
        'pcent': pcent,
        'percent_above_value': percent_above_value,
        'from': from_str,
        'to': to_str
    }
    return response
