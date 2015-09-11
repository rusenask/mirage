from logging.config import fileConfig
import sys
from stubo.scripts import get_default_config
from argparse import ArgumentParser

def main():
    """

    Launches application
    """
    parser = ArgumentParser(
        description="Run Mirage app"
    )
    parser.add_argument('-c', '--config', dest='config',
                        help="Path to configuration file (defaults to $CWD/etc/dev.ini)")

    args = parser.parse_args()
    # looking for configuration path
    config_path = args.config
    if not config_path:
        # if path not provided - looking at default directory - project root
        config_path = get_default_config()
    try:
        fileConfig(config_path)
    except Exception, e:
        print "Unable to load config file: {0}, error={1}".format(config_path, e)
        sys.exit(-1)

    from stubo.service.run_stubo import TornadoManager
    tm = TornadoManager(config_path)
    tm.start_server()


if __name__ == "__main__":
    main()
