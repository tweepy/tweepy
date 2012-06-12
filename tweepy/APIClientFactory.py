'''
Created on Jun 6, 2012

@author: rogelio
'''
import tweepy

class APIClientFactory(object):
    '''Given the access configuration information. You can create several API clients
    by calling get_api or get_streaming_api in an instance of this class'''
   
    def __init__(self, consumer_key, consumer_secret, secure, access_token_key, 
                 access_token_secret, cache = None):
        
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.secure = secure
        self.access_token_key = access_token_key
        self.access_token_secret = access_token_secret
        self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret, self.secure)
        self.auth.set_access_token(access_token_key, access_token_secret)
        self.cache = cache or tweepy.cache.MemoryCache()
    
    
    def get_api(self):
        '''Returns the normal api. With this you can get followers, tweets, friends and a whole bunch
        of other data from twitter'''
        return tweepy.ExtendedAPI(self.auth, cache = self.cache)
    
    
    def get_streaming_api(self, listener, **kwargs):
        '''Returns a tweepy streaming api. This can monitor a stream of tweets with some given options.
        The only non optional argument is a listener, which controls how the data is handled on certain events,
        most commonly on_data, on_status, on_error and on_timeout.
        To read more about how to implement your own listener see tweepy.streaming.StreamListener.
        https://github.com/aaronsw/tweepy/blob/master/tweepy/streaming.py'''
        kwargs['secure'] = True
        return tweepy.streaming.Stream(self.auth, listener, **kwargs)
    
    
    @staticmethod
    def factory_for_django(use_cache = True, cache_time = 3600 * 24 * 7 * 4):
        '''Helper function for django users. Create a client factory where the configuration
        is extracted from the settings.py file of a django project.
        
        Cache time is the number of seconds that the tweepy results will be stored in 
        the django cache
        
        Example configuration:
        
        '''
        # TODO: Use other kinds of cache
        # TODO: Create an example cache configuration
        
        try:
            from django.conf import settings
            from django.core.cache import cache
            
            return APIClientFactory(
                      settings.TWITTER.get('consumer_key'),
                      settings.TWITTER.get('consumer_secret'),
                      settings.TWITTER.get('secure'),
                      settings.TWITTER.get('access_token_key'),
                      settings.TWITTER.get('access_token_secret'),
                      cache = tweepy.RedisCache(client=cache._client, timeout = cache_time))

            
        except ImportError:
            print "Could not import django. Is it installed and in your path?"
