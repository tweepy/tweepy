import tweepy

""" Tutorial 4 -- Errors

Errors are going to happen sooner or later in your applications.
This tutorial will show you how to properly catch these errors in 
Tweepy and handle them gracefully in your application.
"""

""" TweepError

Tweepy uses a single exception: tweepy.TweepError.
When ever something goes wrong this exception will be raised.
Here is an example:
"""
try:
  tweepy.api.update_status('this will fail since we are not authenticated!')
except tweepy.TweepError, e:
  print 'Failed to update! %s' % e

"""
TweepError's can be casted to string format which will
give details as to what went wrong.
The main reasons an exception will be raised include:

  -HTTP request to twitter failed
  -Model failed validation
  -Trying to use an authenticated API endpoint w/o authenticating
  -Invalid parameters supplied to API methods
  -Authentication failures

Be sure to keep a look out for these exceptions and handle them properly.
"""

""" The End """

