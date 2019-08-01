# Tweepy
# Copyright 2009-2019 Joshua Roesslein
# See LICENSE for details.

import datetime
import hashlib
import logging
import threading
import time
import os

try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    import fcntl
except ImportError:
    # Probably on a windows system
    # TODO: use win32file
    pass

log = logging.getLogger(__name__)


class Cache(object):
    """Cache interface"""

    def __init__(self, timeout=60):
        """Initialize the cache
            timeout: number of seconds to keep a cached entry
        """
        self.timeout = timeout

    def store(self, key, value):
        """Add new record to cache
            key: entry key
            value: data of entry
        """
        raise NotImplementedError

    def get(self, key, timeout=None):
        """Get cached entry if exists and not expired
            key: which entry to get
            timeout: override timeout with this value [optional]
        """
        raise NotImplementedError

    def count(self):
        """Get count of entries currently stored in cache"""
        raise NotImplementedError

    def cleanup(self):
        """Delete any expired entries in cache."""
        raise NotImplementedError

    def flush(self):
        """Delete all cached entries"""
        raise NotImplementedError


class MemoryCache(Cache):
    """In-memory cache"""

    def __init__(self, timeout=60):
        Cache.__init__(self, timeout)
        self._entries = {}
        self.lock = threading.Lock()

    def __getstate__(self):
        # pickle
        return {'entries': self._entries, 'timeout': self.timeout}

    def __setstate__(self, state):
        # unpickle
        self.lock = threading.Lock()
        self._entries = state['entries']
        self.timeout = state['timeout']

    def _is_expired(self, entry, timeout):
        return timeout > 0 and (time.time() - entry[0]) >= timeout

    def store(self, key, value):
        self.lock.acquire()
        self._entries[key] = (time.time(), value)
        self.lock.release()

    def get(self, key, timeout=None):
        self.lock.acquire()
        try:
            # check to see if we have this key
            entry = self._entries.get(key)
            if not entry:
                # no hit, return nothing
                return None

            # use provided timeout in arguments if provided
            # otherwise use the one provided during init.
            if timeout is None:
                timeout = self.timeout

            # make sure entry is not expired
            if self._is_expired(entry, timeout):
                # entry expired, delete and return nothing
                del self._entries[key]
                return None

            # entry found and not expired, return it
            return entry[1]
        finally:
            self.lock.release()

    def count(self):
        return len(self._entries)

    def cleanup(self):
        self.lock.acquire()
        try:
            for k, v in dict(self._entries).items():
                if self._is_expired(v, self.timeout):
                    del self._entries[k]
        finally:
            self.lock.release()

    def flush(self):
        self.lock.acquire()
        self._entries.clear()
        self.lock.release()


class FileCache(Cache):
    """File-based cache"""

    # locks used to make cache thread-safe
    cache_locks = {}

    def __init__(self, cache_dir, timeout=60):
        Cache.__init__(self, timeout)
        if os.path.exists(cache_dir) is False:
            os.mkdir(cache_dir)
        self.cache_dir = cache_dir
        if cache_dir in FileCache.cache_locks:
            self.lock = FileCache.cache_locks[cache_dir]
        else:
            self.lock = threading.Lock()
            FileCache.cache_locks[cache_dir] = self.lock

        if os.name == 'posix':
            self._lock_file = self._lock_file_posix
            self._unlock_file = self._unlock_file_posix
        elif os.name == 'nt':
            self._lock_file = self._lock_file_win32
            self._unlock_file = self._unlock_file_win32
        else:
            log.warning('FileCache locking not supported on this system!')
            self._lock_file = self._lock_file_dummy
            self._unlock_file = self._unlock_file_dummy

    def _get_path(self, key):
        md5 = hashlib.md5()
        md5.update(key.encode('utf-8'))
        return os.path.join(self.cache_dir, md5.hexdigest())

    def _lock_file_dummy(self, path, exclusive=True):
        return None

    def _unlock_file_dummy(self, lock):
        return

    def _lock_file_posix(self, path, exclusive=True):
        lock_path = path + '.lock'
        if exclusive is True:
            f_lock = open(lock_path, 'w')
            fcntl.lockf(f_lock, fcntl.LOCK_EX)
        else:
            f_lock = open(lock_path, 'r')
            fcntl.lockf(f_lock, fcntl.LOCK_SH)
        if os.path.exists(lock_path) is False:
            f_lock.close()
            return None
        return f_lock

    def _unlock_file_posix(self, lock):
        lock.close()

    def _lock_file_win32(self, path, exclusive=True):
        # TODO: implement
        return None

    def _unlock_file_win32(self, lock):
        # TODO: implement
        return

    def _delete_file(self, path):
        os.remove(path)
        if os.path.exists(path + '.lock'):
            os.remove(path + '.lock')

    def store(self, key, value):
        path = self._get_path(key)
        self.lock.acquire()
        try:
            # acquire lock and open file
            f_lock = self._lock_file(path)
            datafile = open(path, 'wb')

            # write data
            pickle.dump((time.time(), value), datafile)

            # close and unlock file
            datafile.close()
            self._unlock_file(f_lock)
        finally:
            self.lock.release()

    def get(self, key, timeout=None):
        return self._get(self._get_path(key), timeout)

    def _get(self, path, timeout):
        if os.path.exists(path) is False:
            # no record
            return None
        self.lock.acquire()
        try:
            # acquire lock and open
            f_lock = self._lock_file(path, False)
            datafile = open(path, 'rb')

            # read pickled object
            created_time, value = pickle.load(datafile)
            datafile.close()

            # check if value is expired
            if timeout is None:
                timeout = self.timeout
            if timeout > 0:
                if (time.time() - created_time) >= timeout:
                    # expired! delete from cache
                    value = None
                    self._delete_file(path)

            # unlock and return result
            self._unlock_file(f_lock)
            return value
        finally:
            self.lock.release()

    def count(self):
        c = 0
        for entry in os.listdir(self.cache_dir):
            if entry.endswith('.lock'):
                continue
            c += 1
        return c

    def cleanup(self):
        for entry in os.listdir(self.cache_dir):
            if entry.endswith('.lock'):
                continue
            self._get(os.path.join(self.cache_dir, entry), None)

    def flush(self):
        for entry in os.listdir(self.cache_dir):
            if entry.endswith('.lock'):
                continue
            self._delete_file(os.path.join(self.cache_dir, entry))


class MemCacheCache(Cache):
    """Cache interface"""

    def __init__(self, client, timeout=60):
        """Initialize the cache
            client: The memcache client
            timeout: number of seconds to keep a cached entry
        """
        self.client = client
        self.timeout = timeout

    def store(self, key, value):
        """Add new record to cache
            key: entry key
            value: data of entry
        """
        self.client.set(key, value, time=self.timeout)

    def get(self, key, timeout=None):
        """Get cached entry if exists and not expired
            key: which entry to get
            timeout: override timeout with this value [optional].
            DOES NOT WORK HERE
        """
        return self.client.get(key)

    def count(self):
        """Get count of entries currently stored in cache. RETURN 0"""
        raise NotImplementedError

    def cleanup(self):
        """Delete any expired entries in cache. NO-OP"""
        raise NotImplementedError

    def flush(self):
        """Delete all cached entries. NO-OP"""
        raise NotImplementedError


class RedisCache(Cache):
    """Redis server cache"""

    def __init__(
        self, client, timeout=60, keys_container='tweepy:keys', pre_identifier='tweepy:'
    ):
        Cache.__init__(self, timeout)
        self.client = client
        self.keys_container = keys_container
        self.pre_identifier = pre_identifier
        # Use milliseconds to support float values
        self.timeout = int(timeout * 1000)

    def store(self, key, value):
        # Prepend 'tweepy:' to our key,
        key = self.pre_identifier + key
        pipe = self.client.pipeline()
        pipe.set(key, pickle.dumps(value), px=self.timeout)
        # Add key to a set (container) to track cached keys
        pipe.sadd(self.keys_container, key)
        pipe.execute()

    def get(self, key, timeout=None):
        key = self.pre_identifier + key
        value = self.client.get(key)
        if not value:
            # Make sure expired key is not in container
            self.client.srem(self.keys_container, key)
        else:
            if timeout:
                self.client.pexpire(key, int(timeout * 1000))
            value = pickle.loads(value)
        return value

    def count(self):
        # Remove expired keys before count
        self.cleanup()
        return self.client.scard(self.keys_container)

    def delete_entry(self, key):
        pipe = self.client.pipeline()
        pipe.delete(key)
        pipe.srem(self.keys_container, key)
        pipe.execute()

    def cleanup(self):
        keys = self.client.smembers(self.keys_container)
        for key in keys:
            if not self.client.get(key):
                # Key expired, so remove ref from container
                self.client.srem(self.keys_container, key)

    def flush(self):
        keys = tuple(self.client.smembers(self.keys_container))
        self.client.delete(self.keys_container, *keys)


class MongodbCache(Cache):
    """A simple pickle-based MongoDB cache sytem."""

    def __init__(self, db, timeout=3600, collection='tweepy_cache'):
        """Should receive a "database" cursor from pymongo."""
        Cache.__init__(self, timeout)
        self.timeout = timeout
        self.col = db[collection]
        self.col.create_index('created', expireAfterSeconds=timeout)

    def store(self, key, value):
        from bson.binary import Binary

        now = datetime.datetime.utcnow()
        blob = Binary(pickle.dumps(value))

        self.col.insert({'created': now, '_id': key, 'value': blob})

    def get(self, key, timeout=None):
        if timeout:
            raise NotImplementedError
        obj = self.col.find_one({'_id': key})
        if obj:
            return pickle.loads(obj['value'])

    def count(self):
        return self.col.find({}).count()

    def delete_entry(self, key):
        return self.col.remove({'_id': key})

    def cleanup(self):
        """MongoDB will automatically clear expired keys."""
        pass

    def flush(self):
        self.col.drop()
        self.col.create_index('created', expireAfterSeconds=self.timeout)
