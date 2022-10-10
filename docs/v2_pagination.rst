.. _v2_pagination_guide:

.. currentmodule:: tweepy

**********
Pagination
**********

.. autoclass:: Paginator
    :members:

.. rubric:: Example

::

    import tweepy

    client = tweepy.Client("Bearer Token here")

    for response in tweepy.Paginator(client.get_users_followers, 2244994945,
                                        max_results=1000, limit=5):
        print(response.meta)

    for tweet in tweepy.Paginator(client.search_recent_tweets, "Tweepy",
                                    max_results=100).flatten(limit=250):
        print(tweet.id)

.. autoclass:: tweepy.asynchronous.AsyncPaginator
    :members:
