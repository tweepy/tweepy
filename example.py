import tweepy

print 'An example of using the Tweepy library...'

# We need an authentication handler to tell twitter who we are.
# First let's make one using basic auth.
basic_auth = tweepy.BasicAuthHandler('tweebly', 'omega1987twitter')

# Now a handler for oauth.
oauth_auth = tweepy.OAuthHandler('consumer_key', 'consumer_secrete')

# Create an instance of the API object and use the basic auth handler.
api = tweepy.API(basic_auth)

# Let's get a list of the statuses on the public timeline
# and print the texts to the console.
public_timeline = api.public_timeline()
for status in public_timeline:
  print '%s:  %s\n   from %s posted at %s' % (
      status.user.screen_name, status.text, status.source, status.created_at)

# Now we will update our twitter status
# and print the text to the console.
update = api.update_status(status='hello!')
print 'Update: %s' % update.text

# Get the timeline for the 'twitter' user.
twitter_timeline = api.user_timeline(screen_name='twitter')

# You can also setup up a cache.
# Here we will use an in-memory cache with a timeout of 60 seconds.
cached_api = tweepy.API(basic_auth, cache=tweepy.MemoryCache(timeout=60))

# First request here will not be cached
s = cached_api.get_status(id=123)

# Now this request will be cached and won't require a trip to twitter's server.
s_again = cached_api.get_status(id=123)

