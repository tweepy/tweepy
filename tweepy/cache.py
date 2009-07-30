# Tweepy
# Copyright 2009 Joshua Roesslein
# See LICENSE

import time
import threading

"""Cache interface"""
class Cache(object):

  def __init__(self, timeout=60):
    """Init the cache
        timeout: number of seconds to keep a cached entry
    """
    self.timeout = timeout

  def store(self, key, value):
    """Add new record to cache
        key: entry key
        value: data of entry
    """
    raise NotImplemented

  def get(self, key):
    """Get cached entry if exists and not expired
        key: which entry to get
    """
    raise NotImplemented

  def cleanup(self):
    """Delete any expired entries in cache."""
    raise NotImplemented

  def flush(self):
    """Delete all cached entries"""
    raise NotImplemented

"""In-memory cache"""
class MemoryCache(Cache):

  def __init__(self, timeout=60):
    Cache.__init__(self, timeout)
    self._entries = {}
    self.lock = threading.Lock()

  def _is_expired(self, entry):
    return (time.time() - entry[0]) >= self.timeout

  def store(self, key, value):
    with self.lock:
      self._entries[key] = (time.time(), value)

  def get(self, key):
    with self.lock:
      # check to see if we have this key
      entry = self._entries.get(key)
      if not entry:
        # no hit, return nothing
        return None

      # make sure entry is not expired
      if self._is_expired(entry):
        # entry expired, delete and return nothing
        del self._entries[key]
        return None

      # entry found and not expired, return it
      return entry[1]

  def cleanup(self):
    with self.lock:
      for k,v in self._entries.items():
        if self._is_expired(v):
          del self._entries[k]

  def flush(self):
    with self.lock:
      self._entries.clear()

