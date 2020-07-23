import os
import json
from stubo.cache.queue import redis_server

__author__ = 'karolisrusenas'


class CacheBackend(object):
    """
    The base Cache Backend class
    """

    def get(self, name, key):
        raise NotImplementedError

    def set(self, name, key, msg):
        raise NotImplementedError

    def set_raw(self, name, key, msg):
        raise NotImplementedError

    def incr(self, name, key, amount=1):
        raise NotImplementedError

    def get_raw(self, name, key):
        raise NotImplementedError

    def get_all_raw(self, name):
        raise NotImplementedError

    def get_all(self, name):
        raise NotImplementedError

    def keys(self, name):
        raise NotImplementedError

    def values(self, name):
        raise NotImplementedError

    def delete(self, name, *keys):
        raise NotImplementedError

    def remove(self, name):
        raise NotImplementedError

    def exists(self, name, key):
        raise NotImplementedError


class RedisCacheBackend(CacheBackend):
    def __init__(self, server=None):
        # trying to get server from environment variables
        redis_hostname = os.getenv("REDIS_ADDRESS", None)
        redis_port = os.getenv("REDIS_PORT", None)
        redis_password = os.getenv("REDIS_PASSWORD", None)

        if redis_hostname and redis_port:
            from stubo.utils import setup_redis
            self.server = setup_redis(host=redis_hostname, port=int(redis_port), password=redis_password)
        else:
            self.server = server or redis_server

    def get(self, name, key):
        try:
            return json.loads(self.get_raw(name, key))
        except TypeError:
            return None

    def set(self, name, key, msg):
        return self.set_raw(name, key, json.dumps(msg))

    def set_raw(self, name, key, msg):
        return self.server.hset(name, key, msg)

    def incr(self, name, key, amount=1):
        return self.server.hincrby(name, key, amount=amount)

    def get_raw(self, name, key):
        return self.server.hget(name, key)

    def get_all_raw(self, name):
        return self.server.hgetall(name)

    def get_all(self, name):
        return dict((k, json.loads(v)) for k, v in self.server.hgetall(
            name).iteritems())

    def keys(self, name):
        return self.server.hkeys(name)

    def values(self, name):
        return [json.loads(x) for x in self.server.hvals(name)]

    def delete(self, name, *keys):
        """
        Removes the specified fields from the hash stored at key.
        Specified fields that do not exist within this hash are ignored.
        If key does not exist, it is treated as an empty hash and this command returns 0.
        """
        return self.server.hdel(name, *keys)

    def remove(self, name):
        """
        Time complexity: O(N) where N is the number of keys that will be removed.
        When a key to remove holds a value other than a string, the individual complexity for this key is O(M)
        where M is the number of elements in the list, set, sorted set or hash.
        Removing a single key that holds a string value is O(1).
        """
        return self.server.delete(name)

    def exists(self, name, key):
        return self.server.hexists(name, key)


redis_main_server = None


def get_redis_main():
    return redis_main_server