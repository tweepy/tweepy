import tweepy

""" Tutorial 5 -- Cache

Tweepy provides a caching layer for frequently
requested data. This can help cut down on Twitter API
requests helping to make your application faster.
By default caching is disabled in API instances.
"""

"""
Let's create a new API instance with caching enabled.
Currently Tweepy just comes with an in-memory cache which
we will use for this demo.
"""
cached_api = tweepy.API(cache=tweepy.MemoryCache(timeout=120))

"""
Now we can use this API instance and any request that uses
'GET' will be cached for 120 seconds. If no timeout is specified
the default is 60 seconds.
Here is a demo using our new cached API instance...
"""
non_cached_result = cached_api.public_timeline()
cached_result = cached_api.public_timeline()

"""
The first request (non_cached_result) will require a trip
to the Twitter server. The second request (cached_result)
will be retrieved from the cache saving a trip to Twitter.
"""

""" Your own cache implementation

If you wish to use your own cache implementation just
extend the Cache interface class (tweepy/cache.py).
Then when you create your API instance pass it in.
"""
my_api = tweepy.API(cache=MyCache())

""" The End """

