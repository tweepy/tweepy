'''
Created on Jun 30, 2011

@author: rogelio
'''

import time

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
    
    def store_multiple(self, keys_values_dict, **kwargs):
        '''Store several key, values as given in a mapping(dict)'''
        raise NotImplementedError    

    def get(self, key, timeout=None):
        """Get cached entry if exists and not expired
            key: which entry to get
            timeout: override timeout with this value [optional]
        """
        raise NotImplementedError
    
    
    def get_multiple(self, *keys, **kwargs):
        '''Same as get but works for multiple keys'''
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

    def _is_expired(self, entry, timeout):
        # Returns true if the entry has expired
        return timeout > 0 and (time.time() - entry[0]) >= timeout
    
    def store_users(self, *tweepy_users):
        '''Given some users stores it in the cache using the twitter id as the key'''
        # Create a mapping twitter_id, user
        mapping = {}
        for user in tweepy_users:
            mapping[user.id] = user
        return self.store_multiple(mapping)