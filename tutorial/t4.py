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

"""
If Twitter returns an error response you may wish to retry the request
again. To help make this easier Tweepy allows you to configure it to do
this for you automatically when such error codes are returned.

Here is an example of performing a request and retrying if it fails.
We will tell Tweepy to only attempt up to 5 retries and wait 5 seconds
between each attempt.
"""
try:
    tweepy.api.friends_timeline(retry_count=5, retry_delay=5)
except tweepy.TweepError, e:
    # If all 5 attempts fail a TweepError will be thrown
    print 'Failed to get timeline: %s' % e

"""
By default Tweepy will retry on any non-200 status code returned by twitter.
The default retry_delay is zero, so if no delay is provided Tweepy will retry right away.

Let's say we want to retry on status code responses of 400 only.
Here is how we do that...
"""
try:
    tweepy.api.user_timeline('twitter', retry_count=3, retry_delay=5, retry_errors=[400])
except tweepy.TweepError, e:
    print 'Failed to get timeline: %s' % e

""" The End """

