"""  
    :copyright: (c) 2015 by OpenCredo.
    :license: GPLv3, see LICENSE for more details.
"""
import logging
import datetime
from stubo.model.db import Tracker
from stubo.utils import (
    get_hostname, get_graphite_datapoints, get_graphite_stats
)
from stubo.exceptions import exception_response
from stubo import version

log = logging.getLogger(__name__)

# TODO: remove this function when handlers_mt.tracker_request is removed
def get_tracks(handler, scenario_filter, session_filter, show_only_errors, skip,
               limit, start_time, latency, all_hosts, function):
    tracker = Tracker()
    tracker_filter = {}
    if start_time:
        try:
            start = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            tracker_filter['start_time'] = {"$lt": start}
        except ValueError, e:
            raise exception_response(400,
                                     title='start_time format error: {0}'.format(e))
    if scenario_filter:
        tracker_filter['scenario'] = {'$regex': scenario_filter}
    if session_filter:
        tracker_filter['request_params.session'] = {'$regex': session_filter}
    if show_only_errors:
        tracker_filter['return_code'] = {'$ne': 200}
    if latency:
        tracker_filter['duration_ms'] = {'$gt': latency}
    if not all_hosts:
        host = get_hostname(handler.request)
        tracker_filter['host'] = host
    if function != 'all':
        tracker_filter['function'] = function
    return tracker.find_tracker_data(tracker_filter, skip, limit)


def get_track(request, tracker_id):
    tracker = Tracker()
    return tracker.find_tracker_data_full(tracker_id)


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
