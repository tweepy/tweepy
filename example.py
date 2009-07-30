import tweepy

print 'An example of using the Tweepy library...'

# Some twitter credentials.
# Fill these in with your own login credentials.
username = 'jitterapp'
password = 'omega123'

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

