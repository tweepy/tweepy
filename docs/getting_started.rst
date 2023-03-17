.. _getting_started:

.. currentmodule:: tweepy

***************
Getting Started
***************

Tweepy supports both Twitter API v1.1 and Twitter API v2.

Tweepy's interface for making requests to Twitter API v1.1 endpoints is
:class:`API`.

Tweepy's interface for making requests to Twitter API v2 endpoints is
:class:`Client`.

Models
======

:class:`API` and :class:`Client` methods generally return instances of classes
that are models of Twitter API objects. Each model instance / object contains
the data provided by Twitter's API that represent that object.

For example, the following code retrieves a User object and assigns it to the
variable, ``user``::

    # Get the User object that represents the user, @Twitter
    user = api.get_user(screen_name="Twitter")

The data for each object can be accessed through its attributes/fields, and
some models have helper methods that can be used::

    print(user.screen_name)
    print(user.followers_count)
    for friend in user.friends():
       print(friend.screen_name)

:ref:`Twitter API v1.1 models <v1_models_reference>` and
:ref:`Twitter API v2 models <v2_models_reference>` are documented separately.

Example
=======

::

    import tweepy

    auth = tweepy.OAuth1UserHandler(
        consumer_key, consumer_secret, access_token, access_token_secret
    )

    api = tweepy.API(auth)

    public_tweets = api.home_timeline()
    for tweet in public_tweets:
        print(tweet.text)

This example uses Twitter API v1.1, by using :class:`API`, to retrieve the
Tweets in your home timeline and print the text of each one to the console.

The consumer key, consumer secret, access token, and access token secret being
passed are required to authenticate as a user, using OAuth 1.0a User Context.
The :ref:`authentication` page goes into more detail.

More examples can be found on the :ref:`examples` page.

Streaming
=========

Streams utilize Streaming HTTP protocol to deliver data through
an open, streaming API connection. Rather than delivering data in batches
through repeated requests by your client app, as might be expected from a REST
API, a single connection is opened between your app and the API, with new
results being sent through that connection whenever new matches occur. This
results in a low-latency delivery mechanism that can support very high
throughput. For further information, see
https://developer.twitter.com/en/docs/tutorials/consuming-streaming-data

The Twitter API v1.1 streaming endpoints, `statuses/filter`_ and
`statuses/sample`_, have been deprecated and retired.

.. note::

    ``Stream`` and ``AsyncStream`` were deprecated in v4.13 and removed with
    v4.14.

:class:`StreamingClient` allows `filtering <v2 filtering_>`_ and
`sampling <v2 sampling_>`_ of realtime Tweets using Twitter API v2.

.. _statuses/filter: https://twittercommunity.com/t/announcing-the-deprecation-of-v1-1-statuses-filter-endpoint/182960
.. _statuses/sample: https://twittercommunity.com/t/deprecation-announcement-removing-compliance-messages-from-statuses-filter-and-retiring-statuses-sample-from-the-twitter-api-v1-1/170500
.. _v2 filtering: https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/introduction
.. _v2 sampling: https://developer.twitter.com/en/docs/twitter-api/tweets/volume-streams/introduction

The :ref:`streaming_guide` page goes into more detail.

