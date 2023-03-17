.. _extended_tweets:

.. currentmodule:: tweepy

***************
Extended Tweets
***************

This supplements Twitter's `Tweet updates documentation`_ and `repository`_.

.. _Tweet updates documentation: https://web.archive.org/web/20200705045150/https://developer.twitter.com/en/docs/tweets/tweet-updates
.. _repository: https://twitterdev.github.io/tweet-updates/upcoming.html

Introduction
============

On May 24, 2016, Twitter
`announced <https://blog.twitter.com/express-even-more-in-140-characters>`__
changes to the way that replies and URLs are handled and
`published plans <https://blog.twitter.com/2016/doing-more-with-140-characters>`__
around support for these changes in the Twitter API and initial technical
documentation describing the updates to Tweet objects and API options.\ [#]_
On September 26, 2017, Twitter
`started testing <https://blog.twitter.com/official/en_us/topics/product/2017/Giving-you-more-characters-to-express-yourself.html>`__
280 characters for certain languages,\ [#]_ and on November 7, 2017,
`announced <https://blog.twitter.com/official/en_us/topics/product/2017/tweetingmadeeasier.html>`__
that the character limit was being expanded for Tweets in languages where
cramming was an issue.\ [#]_

Standard API methods
====================

Any ``tweepy.API`` method that returns a Status object accepts a new
``tweet_mode`` parameter. Valid values for this parameter are ``compat`` and
``extended``, which give compatibility mode and extended mode, respectively.
The default mode (if no parameter is provided) is compatibility mode.

Compatibility mode
------------------

By default, using compatibility mode, the ``text`` attribute of Status objects
returned by ``tweepy.API`` methods is truncated to 140 characters, as needed.
When this truncation occurs, the ``truncated`` attribute of the Status object
will be ``True``, and only entities that are fully contained within the
available 140 characters range will be included in the ``entities`` attribute.
It will also be discernible that the ``text`` attribute of the Status object
is truncated as it will be suffixed with an ellipsis character, a space, and a
shortened self-permalink URL to the Tweet.

Extended mode
-------------

When using extended mode, the ``text`` attribute of Status objects returned by
``tweepy.API`` methods is replaced by a ``full_text`` attribute, which
contains the entire untruncated text of the Tweet. The ``truncated`` attribute
of the Status object will be ``False``, and the ``entities`` attribute will
contain all entities. Additionally, the Status object will have a
``display_text_range`` attribute, an array of two Unicode code point indices,
identifying the inclusive start and exclusive end of the displayable content
of the Tweet.

Handling Retweets
=================

When using extended mode with a Retweet, the ``full_text`` attribute of the
Status object may be truncated with an ellipsis character instead of
containing the full text of the Retweet. However, since the
``retweeted_status`` attribute (of a Status object that is a Retweet) is
itself a Status object, the ``full_text`` attribute of the Retweeted Status
object can be used instead.

Example
=======

Given an existing :class:`API` object and ``id`` for a Tweet, the following
can be used to print the full text of the Tweet, or if it's a Retweet, the
full text of the Retweeted Tweet::

   status = api.get_status(id, tweet_mode="extended")
   try:
       print(status.retweeted_status.full_text)
   except AttributeError:  # Not a Retweet
       print(status.full_text)

If ``status`` is a Retweet, ``status.full_text`` could be truncated.

.. rubric:: Footnotes

.. [#] https://twittercommunity.com/t/upcoming-changes-to-simplify-replies-and-links-in-tweets/67497
.. [#] https://twittercommunity.com/t/testing-280-characters-for-certain-languages/94126
.. [#] https://twittercommunity.com/t/updating-the-character-limit-and-the-twitter-text-library/96425
