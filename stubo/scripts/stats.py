"""  
    :copyright: (c) 2015 by OpenCredo.
    :license: GPLv3, see LICENSE for more details.
"""
from argparse import ArgumentParser

from stubo.service.admin import get_stats
from stubo.testing import DummyRequestHandler
from stubo.exceptions import StuboException


def latency_pcent():
    parser = ArgumentParser(
        description="Get response latency % > limit"
    )
    parser.add_argument('-c', '--cluster', dest='cluster',
                        help="cluster name", default='aws_cluster1')
    parser.add_argument('-p', '--percent_above_value', dest='percent_above_value',
                        help="percent found above this value",
                        default='50')
    parser.add_argument('-f', '--from', dest='from_str',
                        help="from (relative or absolute time period to graph)",
                        default="-1hours")
    parser.add_argument('-t', '--to', dest='to_str',
                        help="to (relative or absolute time period to graph)",
                        default="now")

    args = parser.parse_args()
    cluster = args.cluster
    percent_above_value = args.percent_above_value
    args = {
        'cluster_name': args.cluster,
        'percent_above_value': args.percent_above_value,
        'from': [args.from_str],
        'to': [args.to_str]
    }
    handler = DummyRequestHandler(**args)
    try:
        response = get_stats(handler)
        print response
    except StuboException, e:
        print e
