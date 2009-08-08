import tweepy
from t1 import oauth_auth

""" Tutorial 2 -- API

This tutorial will focus on creating and using the API class.
The API class is the primary interface between your application
and Twitter's API. It implements most of the endpoint documented here:
    http://apiwiki.twitter.com/Twitter-API-Documentation
"""

"""
The API class can be used in either authenticated or non-authenticated modes.
First let's demonstrate using the API class without authentication...
"""
no_auth_api = tweepy.API()

"""
Let's query the public timeline and print it to the console...
"""
public_timeline = no_auth_api.public_timeline()
print 'Public timeline...'
for status in public_timeline:
  print status.text
  print 'from: %s' % status.user.screen_name

"""
Tweepy provides a non-authenticated instance of the API for you already
so you don't normally need to create one your self.
"""
tweepy.api  # non-auth instance of API

"""
Any endpoint that does not require authentication can be accessed 
with this non-authenticated API instance. If you try to access an
API endpoint that does require authentication, a TweepError exception
will be raised.
"""

"""
Now we will create an authenticated instance of the API class
using the auth handler we created in tutorial 1.
"""
auth_api = tweepy.API(oauth_auth)

"""
Let's query the authenticated user's friends timeline
and print it to the console...
"""
friends_timeline = auth_api.friends_timeline()
for status in friends_timeline:
  print status.text
  print 'from: %s' % status.user.screen_name

""" The End

So that wraps up this tutorial. You now know how to create both
non-authenticated and authenticated instances of the API class.

Onto the next tutorial!
"""

