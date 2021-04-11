.. _api_reference:

.. currentmodule:: tweepy

.. include:: parameters.rst

***********************************
:mod:`tweepy.api` --- API Reference
***********************************

This page contains some basic documentation for the Tweepy module.

.. autoclass:: API

Premium Search APIs
===================

.. automethod:: API.search_30_day

.. automethod:: API.search_full_archive

Tweets
======

Get Tweet timelines
-------------------

.. automethod:: API.home_timeline

.. automethod:: API.mentions_timeline

.. automethod:: API.user_timeline

Post, retrieve, and engage with Tweets
--------------------------------------

.. automethod:: API.favorites

.. automethod:: API.statuses_lookup

.. automethod:: API.get_oembed

.. automethod:: API.retweeters

.. automethod:: API.retweets

.. automethod:: API.retweets_of_me

.. automethod:: API.get_status

.. automethod:: API.create_favorite

.. automethod:: API.destroy_favorite

.. automethod:: API.destroy_status

.. automethod:: API.retweet

.. automethod:: API.unretweet

.. automethod:: API.update_status

.. automethod:: API.update_with_media

Search Tweets
-------------

.. automethod:: API.search

Accounts and users
==================

Create and manage lists
-----------------------

.. automethod:: API.lists_all

.. automethod:: API.list_members

.. automethod:: API.show_list_member

.. automethod:: API.lists_memberships

.. automethod:: API.lists_ownerships

.. automethod:: API.get_list

.. automethod:: API.list_timeline

.. automethod:: API.list_subscribers

.. automethod:: API.show_list_subscriber

.. automethod:: API.lists_subscriptions

.. automethod:: API.create_list

.. automethod:: API.destroy_list

.. automethod:: API.add_list_member

.. automethod:: API.add_list_members

.. automethod:: API.remove_list_member

.. automethod:: API.remove_list_members

.. automethod:: API.subscribe_list

.. automethod:: API.unsubscribe_list

.. automethod:: API.update_list

Follow, search, and get users
-----------------------------

.. automethod:: API.followers_ids

.. automethod:: API.followers

.. automethod:: API.friends_ids

.. automethod:: API.friends

.. automethod:: API.friendships_incoming

.. automethod:: API.lookup_friendships

.. automethod:: API.no_retweets_friendships

.. automethod:: API.friendships_outgoing

.. automethod:: API.show_friendship

.. automethod:: API.lookup_users

.. automethod:: API.search_users

.. automethod:: API.get_user

.. automethod:: API.create_friendship

.. automethod:: API.destroy_friendship

.. automethod:: API.update_friendship

Manage account settings and profile
-----------------------------------

.. automethod:: API.get_settings

.. automethod:: API.verify_credentials

.. automethod:: API.saved_searches

.. automethod:: API.get_saved_search

.. automethod:: API.get_profile_banner

.. automethod:: API.remove_profile_banner

.. automethod:: API.set_settings

.. automethod:: API.update_profile

.. automethod:: API.update_profile_banner

.. automethod:: API.update_profile_image

.. automethod:: API.create_saved_search

.. automethod:: API.destroy_saved_search

Mute, block, and report users
-----------------------------

.. automethod:: API.blocks_ids

.. automethod:: API.blocks

.. automethod:: API.mutes_ids

.. automethod:: API.mutes

.. automethod:: API.create_block

.. automethod:: API.destroy_block

.. automethod:: API.create_mute

.. automethod:: API.destroy_mute

.. automethod:: API.report_spam

Direct Messages
===============

Sending and receiving events
----------------------------

.. automethod:: API.destroy_direct_message

.. automethod:: API.list_direct_messages

.. automethod:: API.get_direct_message

.. automethod:: API.send_direct_message

Media
=====

Upload media
------------

.. automethod:: API.get_media_upload_status

.. automethod:: API.create_media_metadata

.. automethod:: API.media_upload

.. automethod:: API.simple_upload

.. automethod:: API.chunked_upload

.. automethod:: API.chunked_upload_append

.. automethod:: API.chunked_upload_finalize

.. automethod:: API.chunked_upload_init

Trends
======

Get locations with trending topics
----------------------------------

.. automethod:: API.trends_available

.. automethod:: API.trends_closest

Get trends near a location
--------------------------

.. automethod:: API.trends_place

Geo
===

Get information about a place
-----------------------------

.. automethod:: API.geo_id

Get places near a location
--------------------------

.. automethod:: API.reverse_geocode

.. automethod:: API.geo_search

Developer utilities
===================

Get Twitter configuration details
---------------------------------

.. automethod:: API.configuration

Get Twitter supported languages
-------------------------------

.. automethod:: API.supported_languages

Get app rate limit status
-------------------------

.. automethod:: API.rate_limit_status


.. rubric:: Footnotes

.. [#] https://web.archive.org/web/20170829051949/https://dev.twitter.com/rest/reference/get/search/tweets
.. [#] https://twittercommunity.com/t/favorited-reports-as-false-even-if-status-is-already-favorited-by-the-user/11145
