'''
Created on Jun 30, 2011

@author: rogelio
'''

import threading
import time
from tweepy.cache import Cache


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

    def store(self, key, value):
        self.lock.acquire()
        self._entries[key] = (time.time(), value)
        self.lock.release()
        
    def store_multiple(self, keys_values_dict, **kwargs):
        self.lock.acquire()
        for key, value in keys_values_dict.items():
            self._entries[key] = (time.time(), value)
        self.lock.release()
        
    def get_multiple(self, *keys, **kwargs):
        # Acquire the lock
        self.lock.acquire()
        # Get the timeout
        timeout = kwargs.get('timeout', self.timeout)
        # Get each key, if it does not exists or it is expired, append none to the result list
        # otherwise append the value were looking for
        try:
            results = []
            for key in keys:
                entry = self._entries.get(key, None)
                if not entry:
                    results.append(None)
                elif self._is_expired(entry, timeout):
                    del self._entries[key]
                    results.append(None)
                else: 
                    results.append(entry[1])
            return results
        finally:
            self.lock.release()

    def get(self, key, timeout=None):
        return self.get_multiple(key, timeout=timeout)[0]

    def count(self):
        return len(self._entries)

    def cleanup(self):
        self.lock.acquire()
        try:
            for k, v in self._entries.items():
                if self._is_expired(v, self.timeout):
                    del self._entries[k]
        finally:
            self.lock.release()

    def flush(self):
        self.lock.acquire()
        self._entries.clear()
        self.lock.release()
