import tweepy

print 'An example of using the Tweepy library...'

# Some twitter credentials.
# Fill these in with your own login credentials.
username = ''
password = ''

# Create an instance of the API object.
api = tweepy.API(username, password)

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
cached_api = tweepy.API(username, password, cache=tweepy.MemoryCache(timeout=60))

# First request here will not be cached
s = cached_api.get_status(id=123)

# Now this request will be cached and won't require a trip to twitter's server.
s_again = cached_api.get_status(id=123)

