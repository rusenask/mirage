"""  
    :copyright: (c) 2015 by OpenCredo.
    :license: GPLv3, see LICENSE for more details.
"""
from logging.config import fileConfig
import sys
from argparse import ArgumentParser
from . import get_default_config
from stubo.service.run_stubo import TornadoManager


def run_stubo_app():
    parser = ArgumentParser(
        description="Run stubo app"
    )
    parser.add_argument('-c', '--config', dest='config',
                        help="Path to configuration file (defaults to $CWD/etc/dev.ini)")

    args = parser.parse_args()
    config = args.config
    if not config:
        config = get_default_config()
    try:
        fileConfig(config)
    except Exception, e:
        print "Unable to load config file: {0}, error={1}".format(config, e)
        sys.exit(-1)

    tm = TornadoManager(config)
    tm.start_server()
