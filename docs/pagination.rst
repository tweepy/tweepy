.. _pagination_guide:

.. currentmodule:: tweepy

**********
Pagination
**********

API v1.1
========

.. autoclass:: Cursor
    :members:

Example
-------

::

    import tweepy

    auth = tweepy.AppAuthHandler("Consumer Key here", "Consumer Secret here")
    api = tweepy.API(auth)

    for status in tweepy.Cursor(api.search_tweets, "Tweepy",
                                count=100).items(250):
        print(status.id)

    for page in tweepy.Cursor(api.get_followers, screen_name="TwitterDev",
                              count=200).pages(5):
        print(len(page))

API v2
======

.. autoclass:: Paginator
    :members:

Example
-------

::

    import tweepy

    client = tweepy.Client("Bearer Token here")

    for response in tweepy.Paginator(client.get_users_followers, 2244994945,
                                     max_results=1000, limit=5):
        print(response.meta)

    for tweet in tweepy.Paginator(client.search_recent_tweets, "Tweepy",
                                  max_results=100).flatten(limit=250):
        print(tweet.id)
