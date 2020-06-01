.. _acc_activity_tutorial:


***********************
Account Activity Tutorial
***********************

Introduction
============

Twitter removed the Streaming APIs and replaced it with the 
AccountActivity API which uses a webhook. This Tutorial covers the
Subscription, enabling and structure of the Webhook required by
Twitter.

This Tutorial depends upon the AccountActivity Tweety API but the
details would be much the same in any implementation.

Before attempting the implementation the Developer must have setup
the Twitter application, the Development Environment name and the
URL for the Webhook.

The following imports will be needed.

  import tweepy
  from tweepy.binder import bind_api
  from tweepy.error import TweepError
  from tweepy.parsers import JSONParser, Parser
  from tweepy.activityAPI import ActivityAPI

Setting up the Webhook with Twitter
===================================

If you have not implemented your Authentication code then you will
need to have that ready.

The setup is much the same as registering the client application using
OAuth 1a.

   auth = tweepy.OAuthHandler(CONSUMER_TOKEN, CONSUMER_SECRET)
   auth.set_access_token(key, secret)
        
   api = ActivityAPI(auth)
   activityResponse = api.enable_activity(url = WEBHOOK, env = ENV)
   
When Twitter receives the enable_activity request it makes a GET request
to the Webhook URL. The Webhook must be able to calculate the validation
hash and return the JSON data at receiving the GET. This is the CRC check
This happens every day once the Webhook is registered and if the request
fails Twitter will suspend the Webhook until it is verified again.

Webhook CRC Check
=================

The Webhook must be structured as receiving both a GET and a POST at the
same URL. The GET is for the CRC check and the POST is the data for the
Webhook to handle.

To return the CRC check perform the following and return it as JSON data.

   parameters = web.input()
   logger.info('twwebhook:CRC check')
   # create a HMAC SHA-256 hash from the incoming token and your consumer secret, base64 the result and return as JSON
   sha256_hash_digest = hmac.new(CONSUMER_SECRET.encode(), parameters.crc_token.encode(), digestmod=hashlib.sha256).digest()
   hashresponse = {'response_token': 'sha256=' + base64.b64encode(sha256_hash_digest).decode('utf-8')}
   web.header('Content-Type','application/json')
   return json.dumps(hashresponse)
   
The above presumes that the web.py framework is being used but adopt it
to the framework being used.

Subscribing a User's Account
============================

Once the Webhook is registered and validated it can be subscribed to a
user's Twitter Account. This is using the authorise Application process.
The logged in user on the browser is the account that will be subscribed.

Essentially this means it will be a call to your Web Application that makes
the subscription. You cannot do it directly from a web page as that would
expose your Application keys.

The Tweepy call looks like this.

   auth = tweepy.OAuthHandler(CONSUMER_TOKEN, CONSUMER_SECRET)
   auth.set_access_token(key, secret)

   api = ActivityAPI(auth)          
   activityResponse = api.subscribe_activity(env=ENV)
   
So long as the response from subscribe_activity is 200 (OK) the account is
subscribed and events will be sent to your Webhook for the account.

Receiving Events
================

The GET handler of the Webhook receives all the events as JSON. Refer to the
Twitter Developer documentation for the current schemas as they are subject to
change. The rate at which events are sent to the Webhook cannot be determined
the best strategy is to hand off every event, perhaps by writing to a queue,
and return quickly.

