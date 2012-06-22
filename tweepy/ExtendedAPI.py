'''
Created on Jun 28, 2011

@author: rogelio
'''

from tweepy.api import API
from tweepy.binder import bind_api
from tweepy.cache import MemoryCache
from tweepy.utils import make_chunks, list_to_csv

from itertools import chain, izip

# NOTE: This is a test to see how a higher level API will behave
# Not the best way to do it, a major rewrite of API and Binder will make something similar 
# possible in a much cleaner way
class ExtendedAPI(API):
    
    LOOKUP_MAX_PER_REQUEST = 100
    
    def __init__(self, *args, **kwargs):
        super(ExtendedAPI, self).__init__(*args, **kwargs)
        # If no cache was set, use MemoryCache (python dict) as our cache
        self.cache = self.cache or MemoryCache()

    # This is exactly the same call with cache disabled.
    # Were going to provide higher level cache (by user instead of by call)
    """ users/lookup """
    __uncached_lookup_users = bind_api(
        path = '/users/lookup.json',
        payload_type = 'user', payload_list = True,
        allowed_param = ['user_id', 'screen_name'],
        require_auth = True,
        use_cache = False
    )
    
    def _lookup_users(self, user_ids=[], screen_names=[]):
        '''A wrapper around __uncached_lookup_users to store the returned Users
        in the cache'''
        
        assert (len(user_ids) + len(screen_names) > 0), "WAKA WAKA"
        
        users = self.__uncached_lookup_users(list_to_csv(user_ids), list_to_csv(screen_names))
        self.cache.store_users(*users)
        return users

    # This is exactly the same call with cache disabled.
    # Were going to provide higher level cache (by user instead of by call)    
    """ users/show """
    __uncached_get_user = bind_api(
        path = '/users/show.json',
        payload_type = 'user',
        allowed_param = ['id', 'user_id', 'screen_name'],
        use_cache = False
    )
    
    def _get_user(self, *args, **kwargs):
        user = self.__uncached_get_user(*args, **kwargs)
        self.cache.store_users(user)
        return user
        
    class Decorators(object):
        
        @classmethod
        def yield_users_from_cache(cls, wrapped):
            '''Removes the users that were in the cache and lets the decorated function just 
            look for the missing objects'''
            def wrapper(self, user_ids=[], screen_names=[]):                
                user_ids = set(user_ids)
                screen_names = set(screen_names)
                # Trivia question: What is faster union or chain? How about if you iterate over the result two times?
                users = user_ids.union(screen_names)
                
                cache_results = self.cache.get_multiple(*users)
                
                missing = set()
                # Iterate over the cache results, yielding the users in the cache
                # and adding to a missing set the users that weren't
                for user, cache_result in izip(users, cache_results):
                    if cache_result:
                        yield cache_result
                    else:
                        missing.add(user)
                        
                missing_user_ids = missing.intersection(user_ids)
                missing_screen_names = missing.intersection(screen_names)
                # Yield the missing users
                for user in wrapped(self, missing_user_ids, missing_screen_names):
                    yield user
            return wrapper
        
    def lookup_users(self, user_ids=[], screen_names=[]):
        '''An extension to lookup_users to work with authenticated and unauthenticated api instances.
        
        If the client is authenticated we use twitter's users/lookup call, which retrieves up to 100 
        users per request.
        If the client is unauthenticated we use users/show which is less efficient, since it retrieves
        one user per request'''
        
        # If the user is authenticated use users/lookup call
        if self.auth:
            return self.__authenticated_lookup_users(user_ids, screen_names)
        # If the api is not authenticated just use users/show call and return the results as they come
        else:
            return self.__unauthenticated_lookup_users(user_ids, screen_names)
        
    @Decorators.yield_users_from_cache      
    def __authenticated_lookup_users(self, user_ids=[], screen_names=[]):
        '''This function will only work for authenticated apis.
        
        First we separate the given users in chunks of 100 (otherwise it will fail with
        "Too many terms specified for this query") we then proceed to do the request
        and return the results as they come'''
        assert self.auth, "This API is not authenticated"
            
        user_ids_chunks = make_chunks(user_ids, self.LOOKUP_MAX_PER_REQUEST)
        screen_names_chunks = make_chunks(screen_names, self.LOOKUP_MAX_PER_REQUEST)
                
        for chunk in user_ids_chunks:
            for result in self._lookup_users(user_ids = chunk):
                yield result
        
        for chunk in screen_names_chunks:
            for result in self._lookup_users(screen_names = chunk):
                yield result
    
    @Decorators.yield_users_from_cache         
    def __unauthenticated_lookup_users(self, user_ids=[], screen_names=[]):
        '''This function is intended to work in a similar fashion to lookup_users for unauthenticated apis.
        Since users/lookup call won't work with unauth apis we use users/show instead and yield the results 
        as they come'''
        for user in chain(user_ids, screen_names):
            yield self._get_user(user)