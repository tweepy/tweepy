.. _extended_tweets:
.. _Twitter's Tweet updates documentation: https://developer.twitter.com/en/docs/tweets/tweet-updates

***************
Extended Tweets
***************

This supplements `Twitter's Tweet updates documentation`_.

Introduction
============

On May 24, 2016, Twitter
`announced <https://blog.twitter.com/express-even-more-in-140-characters>`_
changes to the way that replies and URLs are handled and
`published plans <https://blog.twitter.com/2016/doing-more-with-140-characters>`_
around support for these changes in the Twitter API and initial technical
documentation describing the updates to Tweet objects and API options.\ [#]_
On September 26, 2017, Twitter
`started testing <https://blog.twitter.com/official/en_us/topics/product/2017/Giving-you-more-characters-to-express-yourself.html>`_
280 characters for certain languages,\ [#]_ and on November 7, 2017,
`announced <https://blog.twitter.com/official/en_us/topics/product/2017/tweetingmadeeasier.html>`_
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

Streaming
=========

By default, the Status objects from streams may contain an ``extended_tweet``
attribute representing the equivalent field in the raw data/payload for the
Tweet. This attribute/field will only exist for extended Tweets, containing a
dictionary of sub-fields. The ``full_text`` sub-field/key of this dictionary
will contain the full, untruncated text of the Tweet, and the ``entities``
sub-field/key will contain the full set of entities. If there are extended
entities, the ``extended_entities`` sub-field/key will contain the full set of
those. Additionally, the ``display_text_range`` sub-field/key will contain an
array of two Unicode code point indices, identifying the inclusive start and
exclusive end of the displayable content of the Tweet.

Handling Retweets
=================

When using extended mode with a Retweet, the ``full_text`` attribute of the
Status object may be truncated with an ellipsis character instead of
containing the full text of the Retweet. However, since the
``retweeted_status`` attribute (of a Status object that is a Retweet) is
itself a Status object, the ``full_text`` attribute of the Retweeted Status
object can be used instead.

This also applies similarly to Status objects/payloads that are Retweets from
streams. The dictionary from the ``extended_tweet`` attribute/field contains a
``full_text`` sub-field/key that may be truncated with an ellipsis character.
Instead, the ``extended_tweet`` attribute/field of the Retweeted Status (from
the ``retweeted_status`` attribute/field) can be used.

Examples
========

Given an existing ``tweepy.API`` object and ``id`` for a Tweet, the following
can be used to print the full text of the Tweet, or if it's a Retweet, the
full text of the Retweeted Tweet::

   status = api.get_status(id, tweet_mode="extended")
   try:
       print(status.retweeted_status.full_text)
   except AttributeError:  # Not a Retweet
       print(status.full_text)

If ``status`` is a Retweet, ``status.full_text`` could be truncated.

This Status event handler for a ``StreamListener`` prints the full text of the
Tweet, or if it's a Retweet, the full text of the Retweeted Tweet::

   def on_status(self, status):
       if hasattr(status, "retweeted_status"):  # Check if Retweet
           try:
               print(status.retweeted_status.extended_tweet["full_text"])
           except AttributeError:
               print(status.retweeted_status.text)
       else:
           try:
               print(status.extended_tweet["full_text"])
           except AttributeError:
               print(status.text)

If ``status`` is a Retweet, it will not have an ``extended_tweet`` attribute,
and ``status.text`` could be truncated.

.. rubric:: Footnotes

.. [#] https://twittercommunity.com/t/upcoming-changes-to-simplify-replies-and-links-in-tweets/67497
.. [#] https://twittercommunity.com/t/testing-280-characters-for-certain-languages/94126
.. [#] https://twittercommunity.com/t/updating-the-character-limit-and-the-twitter-text-library/96425
