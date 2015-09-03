"""
    stubo.scripts
    ~~~~~~~~~~~~~
    
    Bin scripts
     
    :copyright: (c) 2015 by OpenCredo.
    :license: GPLv3, see LICENSE for more details.
"""
import os
import sys


def get_default_config():
    """Get the default configuration file name.

    This should be called by a console script. We assume that the
    console script lives in the 'bin' dir of a sandbox or buildout, and
    that the dev.ini file lives in the 'etc' directory of the sandbox.
    """
    me = sys.argv[0]
    me = os.path.abspath(me)
    sandbox = os.path.dirname(os.path.dirname(me))
    config = os.path.join(sandbox, 'etc', 'dev.ini')
    return os.path.abspath(os.path.normpath(config))
