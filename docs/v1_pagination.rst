.. _v1_pagination_guide:

.. currentmodule:: tweepy

**********
Pagination
**********

.. autoclass:: Cursor
    :members:

.. rubric:: Example

::

    import tweepy

    auth = tweepy.OAuth2AppHandler("Consumer Key here", "Consumer Secret here")
    api = tweepy.API(auth)

    for status in tweepy.Cursor(api.search_tweets, "Tweepy",
                                count=100).items(250):
        print(status.id)

    for page in tweepy.Cursor(api.get_followers, screen_name="TwitterDev",
                                count=200).pages(5):
        print(len(page))
