'''
Created on Jun 30, 2011

@author: rogelio
'''
    
from tweepy.cache import Cache
import time  
try:
    import cPickle as pickle
except ImportError:
    import pickle
    
    
try:
    import redis
except:
    pass
    
    
class RedisCache(Cache):
    '''Cache running in a redis server.
    
    Elements are stored as a normal record in redis. We also have a Set containing all the keys
    in the cache which defaults to tweepy:keys and can be configured to be in whatever keys_container is.
    
    We follow the implementation in a similar way to MemoryCache, but also use extra features as the
    redis_expire function to expire keys instead of waiting for clean_up to be called. This can cause
    the key_set to indicate we have more keys than what we have, if an exact number is necessary, call
    cleanup before count.
    '''

    def __init__(self, client=None, timeout=60, keys_container = 'tweepy:keys', prefix = 'tweepy:'):
        super(RedisCache, self).__init__(timeout)
        self.keys_container = keys_container
        self.prefix = prefix
        try:            
            self.client = client or redis.Redis() # Attempt creating a client to localhost if no client
        except:
            raise TypeError, "You must provide a redis client instance"
        
                
    def store_multiple(self, keys_values_dict, **kwargs):
        '''Store the key, value pair in our redis server'''
        
        # Get a pipe (to execute several redis commands in one step)
        pipe = self.client.pipeline()
        timeout = kwargs.get('timeout', self.timeout)
        
        for key, value in keys_values_dict.items():
            # Prepend tweepy to our key, this makes it easier to identify tweepy keys in our redis server
            key = self.add_prefix(key)            
            # Set our values in a redis hash (similar to python dict)
            pipe.set(key, pickle.dumps((time.time(), value)))
            # Set the expiration
            pipe.expire(key, timeout)
            # Add the key to a set containing all the keys
            pipe.sadd(self.keys_container, key)
        
        # Execute the instructions in the redis server
        return pipe.execute()
        
    def store(self, key, value):
        '''Reuse logic in store_multiple'''
        return self.store_multiple(dict([(key, value)]))
    
    def add_prefix(self, key):
        '''Add the prefix to the key if it does not have it yet'''
        key = unicode(key)
        return key if key.startswith(self.prefix) else self.prefix + key
    
    def get_multiple(self, *keys, **kwargs):
        '''Given an iterable of keys, returns the corresponding elements in the cache'''
        
        timeout = kwargs.get('timeout', self.timeout)
        
        # Get the values in one go
        pipe = self.client.pipeline()
        for key in keys:
            key = self.add_prefix(key)
            pipe.get(key)
        unpickled_values = pipe.execute()        
        
        # Iterate over the keys, if we find expired keys
        results = []
        expired_keys = []
        
        for key, u_value in zip(keys, unpickled_values):
            # If we receive none, it wasn't on the cache
            if not u_value:
                results.append(None)
            else:  
                value = pickle.loads(u_value)              
                if self._is_expired(value, timeout):
                    expired_keys.append(key)
                    results.append(None)
                else:
                    # 0 is timeout, 1 is object
                    results.append(value[1])
                    
        self.delete_entries(expired_keys)
        return results

    def get(self, key):
        return self.get_multiple(key)[0]

    def count(self):
        '''If we didn't have the set here we wouldn't be able to retrieve this as a number and would have to
        get all keys and then count.'''
        return self.client.scard(self.keys_container)

    def delete_entries(self, *keys):
        '''Delete an object from the redis table'''
        pipe = self.client.pipeline()
        for key in keys:
            pipe.srem(self.keys_container, key)
            pipe.delete(key)
        return pipe.execute()
        
    # An alias for the single version
    delete_entry = delete_entries

    def cleanup(self):
        '''Cleanup all the expired keys'''
        
        # Get the keys from the key container
        keys = self.client.smembers(self.keys_container)
        # Use a pipe to get all the values from the keys in one go
        values_pipe = self.client.pipeline()
        for key in keys: values_pipe.get(key)
        values = values_pipe.execute()
        
        dead_keys = []
        
        # If the key did not exist or the key is expired, clean from the cache
        for key, value in zip(keys, values):
            
            if not value: 
                dead_keys.append(key)
            else:
                value = pickle.loads(value)
                if  self._is_expired(value, self.timeout):
                    dead_keys.append(key)

        return self.delete_entries(*dead_keys)
                    
    def flush(self):
        '''Delete all entries from the cache'''
        keys = self.client.smembers(self.keys_container)
        return self.delete_entries(*keys)