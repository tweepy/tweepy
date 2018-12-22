.. _streaming_how_to:
.. _Twitter Streaming API Documentation: https://developer.twitter.com/en/docs/tweets/filter-realtime/overview
.. _Twitter Streaming API Connecting Documentation: https://developer.twitter.com/en/docs/tutorials/consuming-streaming-data
.. _Twitter Response Codes Documentation: https://dev.twitter.com/overview/api/response-codes

*********************
Streaming With Tweepy
*********************
Tweepy makes it easier to use the twitter streaming api by handling authentication, 
connection, creating and destroying the session, reading incoming messages, 
and partially routing messages. 

This page aims to help you get started using Twitter streams with Tweepy 
by offering a first walk through.  Some features of Tweepy streaming are
not covered here. See streaming.py in the Tweepy source code. 

API authorization is required to access Twitter streams. 
Follow the :ref:`auth_tutorial` if you need help with authentication. 

Summary
=======
The Twitter streaming API is used to download twitter messages in real 
time.  It is useful for obtaining a high volume of tweets, or for 
creating a live feed using a site stream or user stream. 
See the `Twitter Streaming API Documentation`_.

The streaming api is quite different from the REST api because the
REST api is used to *pull* data from twitter but the streaming api
*pushes* messages to a persistent session. This allows the streaming 
api to download more data in real time than could be done using the
REST API. 

In Tweepy, an instance of **tweepy.Stream** establishes a streaming 
session and routes messages to **StreamListener** instance.  The
**on_data** method of a stream listener receives all messages and
calls functions according to the message type. The default 
**StreamListener** can classify most common twitter messages and 
routes them to appropriately named methods, but these methods are 
only stubs. 

Therefore using the streaming api has three steps. 

1. Create a class inheriting from **StreamListener**

2. Using that class create a **Stream** object 

3. Connect to the Twitter API using the **Stream**.


Step 1: Creating a **StreamListener**
=====================================
This simple stream listener prints status text.
The **on_data** method of Tweepy's **StreamListener** conveniently passes 
data from statuses to the **on_status** method.
Create class **MyStreamListener** inheriting from  **StreamListener** 
and overriding **on_status**.::
  import tweepy
  #override tweepy.StreamListener to add logic to on_status
  class MyStreamListener(tweepy.StreamListener):
  
      def on_status(self, status):
          print(status.text)

Step 2: Creating a **Stream**
=============================
We need an api to stream. See :ref:`auth_tutorial` to learn how to get an api object. 
Once we have an api and a status listener we can create our stream object.::

  myStreamListener = MyStreamListener()
  myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)

Step 3: Starting a Stream
=========================
A number of twitter streams are available through Tweepy. Most cases 
will use filter, the user_stream, or the sitestream. 
For more information on the capabilities and limitations of the different
streams see `Twitter Streaming API Documentation`_.

In this example we will use **filter** to stream all tweets containing
the word *python*. The **track** parameter is an array of search terms to stream. ::
  
  myStream.filter(track=['python'])

This example shows how to use **filter** to stream tweets by a specific user. The **follow** parameter is an array of IDs. ::

  myStream.filter(follow=["2211149702"])

An easy way to find a single ID is to use one of the many conversion websites: search for 'what is my twitter ID'.

A Few More Pointers
===================

Async Streaming
---------------
Streams do not terminate unless the connection is closed, blocking the thread. 
Tweepy offers a convenient **is_async** parameter on **filter** so the stream will run on a new
thread. For example ::

  myStream.filter(track=['python'], is_async=True)

Handling Errors
---------------
When using Twitter's streaming API one must be careful of the dangers of 
rate limiting. If clients exceed a limited number of attempts to connect to the streaming API 
in a window of time, they will receive error 420.  The amount of time a client has to wait after receiving error 420
will increase exponentially each time they make a failed attempt. 

Tweepy's **Stream Listener** passes error codes to an **on_error** stub. The
default implementation returns **False** for all codes, but we can override it
to allow Tweepy to reconnect for some or all codes, using the backoff
strategies recommended in the `Twitter Streaming API Connecting
Documentation`_. ::

  class MyStreamListener(tweepy.StreamListener):
  
      def on_error(self, status_code):
          if status_code == 420:
              #returning False in on_error disconnects the stream
              return False

          # returning non-False reconnects the stream, with backoff.

For more information on error codes from the Twitter API see `Twitter Response Codes Documentation`_.

