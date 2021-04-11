.. _api_reference:

.. currentmodule:: tweepy

.. include:: parameters.rst

*************
API Reference
*************

This page contains some basic documentation for the Tweepy module.


:mod:`tweepy.api` --- Twitter API wrapper
=========================================

.. autoclass:: API

Tweets
------

Get Tweet timelines
^^^^^^^^^^^^^^^^^^^

.. automethod:: API.home_timeline

.. automethod:: API.mentions_timeline

.. automethod:: API.user_timeline

Post, retrieve, and engage with Tweets
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
^^^^^^^^^^^^^

.. automethod:: API.search

Accounts and users
------------------

Create and manage lists
^^^^^^^^^^^^^^^^^^^^^^^

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
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
---------------

Sending and receiving events
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: API.destroy_direct_message

.. automethod:: API.list_direct_messages

.. automethod:: API.get_direct_message

.. automethod:: API.send_direct_message

Media
-----

Upload media
^^^^^^^^^^^^

.. automethod:: API.get_media_upload_status

.. automethod:: API.create_media_metadata

.. automethod:: API.media_upload

.. automethod:: API.simple_upload

.. automethod:: API.chunked_upload

.. automethod:: API.chunked_upload_append

.. automethod:: API.chunked_upload_finalize

.. automethod:: API.chunked_upload_init

Trends
------

Get locations with trending topics
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: API.trends_available

.. automethod:: API.trends_closest

Get trends near a location
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: API.trends_place

Geo
---

Get information about a place
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: API.geo_id


Account Methods
---------------

.. method:: API.rate_limit_status()

   Returns the current rate limits for methods belonging to the specified
   resource families. When using application-only auth, this method's response
   indicates the application-only auth rate limiting context.

   :param resources: A comma-separated list of resource families you want to
                     know the current rate limit disposition for.
   :rtype: :class:`JSON` object


Search Methods
--------------

.. method:: API.search_30_day(environment_name, query, [tag], [fromDate], \
                              [toDate], [maxResults], [next])

   Premium search that provides Tweets posted within the last 30 days.

   :param environment_name: The (case-sensitive) label associated with your
      search developer environment, as displayed at
      https://developer.twitter.com/en/account/environments.
   :param query: The equivalent of one premium rule/filter, with up to 1,024
      characters (256 with Sandbox dev environments).
      This parameter should include ALL portions of the rule/filter, including
      all operators, and portions of the rule should not be separated into
      other parameters of the query.
   :param tag: Tags can be used to segregate rules and their matching data into
      different logical groups. If a rule tag is provided, the rule tag is
      included in the 'matching_rules' attribute.
      It is recommended to assign rule-specific UUIDs to rule tags and maintain
      desired mappings on the client side.
   :param fromDate: The oldest UTC timestamp (from most recent 30 days) from
      which the Tweets will be provided. Timestamp is in minute granularity and
      is inclusive (i.e. 12:00 includes the 00 minute).
      Specified: Using only the fromDate with no toDate parameter will deliver
      results for the query going back in time from now( ) until the fromDate.
      Not Specified: If a fromDate is not specified, the API will deliver all
      of the results for 30 days prior to now( ) or the toDate (if specified).
      If neither the fromDate or toDate parameter is used, the API will deliver
      all results for the most recent 30 days, starting at the time of the
      request, going backwards.
   :param toDate: The latest, most recent UTC timestamp to which the Tweets
      will be provided. Timestamp is in minute granularity and is not inclusive
      (i.e. 11:59 does not include the 59th minute of the hour).
      Specified: Using only the toDate with no fromDate parameter will deliver
      the most recent 30 days of data prior to the toDate.
      Not Specified: If a toDate is not specified, the API will deliver all of
      the results from now( ) for the query going back in time to the fromDate.
      If neither the fromDate or toDate parameter is used, the API will deliver
      all results for the entire 30-day index, starting at the time of the
      request, going backwards.
   :param maxResults: The maximum number of search results to be returned by a
      request. A number between 10 and the system limit (currently 500, 100 for
      Sandbox environments). By default, a request response will return 100
      results.
   :param next: This parameter is used to get the next 'page' of results. The
      value used with the parameter is pulled directly from the response
      provided by the API, and should not be modified.


.. method:: API.search_full_archive(environment_name, query, [tag], \
                                    [fromDate], [toDate], [maxResults], [next])

   Premium search that provides Tweets from as early as 2006, starting with the
   first Tweet posted in March 2006.

   :param environment_name: The (case-sensitive) label associated with your
      search developer environment, as displayed at
      https://developer.twitter.com/en/account/environments.
   :param query: The equivalent of one premium rule/filter, with up to 1,024
      characters (256 with Sandbox dev environments).
      This parameter should include ALL portions of the rule/filter, including
      all operators, and portions of the rule should not be separated into
      other parameters of the query.
   :param tag: Tags can be used to segregate rules and their matching data into
      different logical groups. If a rule tag is provided, the rule tag is
      included in the 'matching_rules' attribute.
      It is recommended to assign rule-specific UUIDs to rule tags and maintain
      desired mappings on the client side.
   :param fromDate: The oldest UTC timestamp (from most recent 30 days) from
      which the Tweets will be provided. Timestamp is in minute granularity and
      is inclusive (i.e. 12:00 includes the 00 minute).
      Specified: Using only the fromDate with no toDate parameter will deliver
      results for the query going back in time from now( ) until the fromDate.
      Not Specified: If a fromDate is not specified, the API will deliver all
      of the results for 30 days prior to now( ) or the toDate (if specified).
      If neither the fromDate or toDate parameter is used, the API will deliver
      all results for the most recent 30 days, starting at the time of the
      request, going backwards.
   :param toDate: The latest, most recent UTC timestamp to which the Tweets
      will be provided. Timestamp is in minute granularity and is not inclusive
      (i.e. 11:59 does not include the 59th minute of the hour).
      Specified: Using only the toDate with no fromDate parameter will deliver
      the most recent 30 days of data prior to the toDate.
      Not Specified: If a toDate is not specified, the API will deliver all of
      the results from now( ) for the query going back in time to the fromDate.
      If neither the fromDate or toDate parameter is used, the API will deliver
      all results for the entire 30-day index, starting at the time of the
      request, going backwards.
   :param maxResults: The maximum number of search results to be returned by a
      request. A number between 10 and the system limit (currently 500, 100 for
      Sandbox environments). By default, a request response will return 100
      results.
   :param next: This parameter is used to get the next 'page' of results. The
      value used with the parameter is pulled directly from the response
      provided by the API, and should not be modified.


Geo Methods
-----------

.. method:: API.reverse_geocode([lat], [long], [accuracy], [granularity], \
                                [max_results])

   Given a latitude and longitude, looks for places (cities and neighbourhoods)
   whose IDs can be specified in a call to :func:`update_status` to appear as
   the name of the location. This call provides a detailed response about the
   location in question; the :func:`nearby_places` function should be preferred
   for getting a list of places nearby without great detail.

   :param lat: The location's latitude.
   :param long: The location's longitude.
   :param accuracy: Specify the "region" in which to search, such as a number
                    (then this is a radius in meters, but it can also take a
                    string that is suffixed with ft to specify feet).
                    If this is not passed in, then it is assumed to be 0m
   :param granularity: Assumed to be ``neighborhood`` by default; can also be
                       ``city``.
   :param max_results: A hint as to the maximum number of results to return.
                       This is only a guideline, which may not be adhered to.


Utility methods
---------------

.. method:: API.configuration()

   Returns the current configuration used by Twitter including twitter.com
   slugs which are not usernames, maximum photo resolutions, and t.co
   shortened URL length. It is recommended applications request this endpoint
   when they are loaded, but no more than once a day.


:mod:`tweepy.error` --- Exceptions
==================================

The exceptions are available in the ``tweepy`` module directly, which means
``tweepy.error`` itself does not need to be imported. For example,
``tweepy.error.TweepError`` is available as ``tweepy.TweepError``.


.. exception:: TweepError

   The main exception Tweepy uses. Is raised for a number of things.

   When a ``TweepError`` is raised due to an error Twitter responded with,
   the error code (`as described in the API documentation
   <https://developer.twitter.com/en/docs/basics/response-codes>`_) can be
   accessed at ``TweepError.response.text``. Note, however, that
   ``TweepError``\ s also may be raised with other things as message
   (for example plain error reason strings).


.. exception:: RateLimitError

   Is raised when an API method fails due to hitting Twitter's rate limit.
   Makes for easy handling of the rate limit specifically.

   Inherits from :exc:`TweepError`, so ``except TweepError`` will catch a
   ``RateLimitError`` too.


.. rubric:: Footnotes

.. [#] https://web.archive.org/web/20170829051949/https://dev.twitter.com/rest/reference/get/search/tweets
.. [#] https://twittercommunity.com/t/favorited-reports-as-false-even-if-status-is-already-favorited-by-the-user/11145
