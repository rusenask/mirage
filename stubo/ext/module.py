"""  
    :copyright: (c) 2015 by OpenCredo.
    :license: GPLv3, see LICENSE for more details.
"""
import imp
import sys
import logging

from stubo.cache import Cache, get_redis_server
from stubo.cache.queue import Queue
from stubo.exceptions import exception_response, UserExitModuleNotFound

log = logging.getLogger(__name__)


class Module(object):
    def __init__(self, host):
        self.cache = Cache(host)

    def host(self):
        return self.cache.host

    def add_sys_module(self, name, src):
        log.info('adding {0} to sys.modules'.format(name))
        _module = imp.new_module(name)
        code = compile(src, '<string>', 'exec')
        exec code in _module.__dict__
        sys.modules[name] = _module
        names = [x for x in sys.modules.keys() if x.startswith(name[:-4])]
        log.debug('sys.modules: {0}'.format(names))
        return code, _module

    def remove_sys_module(self, name):
        log.debug('remove_sys_module: {0}'.format(name))
        del sys.modules[name]

    def key(self, module_name):
        return '{0}:modules:{1}'.format(self.cache.host, module_name)

    def sys_module_name(self, name, version):
        return '{0}_{1}_v{2}'.format(self.cache.host, name, version)

    def get_sys_module(self, name, version):
        # lazy load if not in already in sys.modules
        module_name = self.sys_module_name(name, version)
        if module_name not in sys.modules:
            # load from source
            code = self.get_source(name, version)
            if not code:
                raise exception_response(500, title="module '{0}' source not "
                                                    "found.".format(module_name))
            self.add_sys_module(module_name, code)
        return sys.modules[module_name]

    def latest_version(self, module_name):
        q = Queue(self.key(module_name))
        return len(q)

    def get(self, module_name, version=None):
        # get module version from redis, load if not in sys.modules
        _mod_version = version or self.latest_version(module_name)
        if not _mod_version:
            raise UserExitModuleNotFound(code=400, title="module '{0}' not found, "
                                                         "you must add the module "
                                                         "first, see put/module.".format(module_name))
        return self.get_sys_module(module_name, _mod_version)

    def add(self, module_name, code):
        key = self.key(module_name)
        log.debug('add {0} module to cache'.format(key))
        q = Queue(key, server=get_redis_server(local=False))
        q.put(code)

    def get_source(self, module_name, version=None):
        key = self.key(module_name)
        q = Queue(key)
        version = version or len(q)
        return q.get_item(version - 1)

    def remove(self, module_name):
        key = self.key(module_name)
        log.debug('remove {0} module from cache'.format(key))
        return Queue(key, server=get_redis_server(local=False)).delete()
