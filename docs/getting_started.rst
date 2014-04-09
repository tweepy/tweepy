.. _getting_started:


***************
Getting started
***************

Introduction
============

If you are new to Tweepy, this is the place to begin. The goal of this
tutorial is to get you set-up and rolling with Tweepy. We won't go
into too much detail here, just some important basics.

Hello Tweepy
============

.. code-block :: python

   import tweepy

   auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
   auth.set_access_token(access_token, access_token_secret)

   api = tweepy.API(auth)
   
   public_tweets = api.home_timeline()
   for tweet in public_tweets:
       print tweet.text

This example will download your home timeline tweets and print each
one of their texts to the console. Twitter requires all requests to
use OAuth for authentication.
The :ref:`auth_tutorial` goes into more details about authentication.

API
===

The API class provides access to the entire twitter RESTful API
methods. Each method can accept various parameters and return
responses. For more information about these methods please refer to
:ref:`API Reference <api_reference>`.

Models
======

When we invoke an API method most of the time returned back to us will
be a Tweepy model class instance. This will contain the data returned
from Twitter which we can then use inside our application. For example
the following code returns to us an User model::

   # Get the User object for twitter...
   user = tweepy.api.get_user('twitter')

Models container the data and some helper methods which we can then
use::

   print user.screen_name
   print user.followers_count
   for friend in user.friends():
      print friend.screen_name

For more information about models please see ModelsReference.

