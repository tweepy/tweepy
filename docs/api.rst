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


Direct Message Methods
----------------------

.. method:: API.get_direct_message([id], [full_text])

   Returns a specific direct message.

   :param id: The id of the Direct Message event that should be returned.
   :param full_text: |full_text|
   :rtype: :class:`DirectMessage` object


.. method:: API.list_direct_messages([count], [cursor])

   Returns all Direct Message events (both sent and received) within the last
   30 days. Sorted in reverse-chronological order.

   :param count: |count|
   :param cursor: |cursor|
   :rtype: list of :class:`DirectMessage` objects


.. method:: API.send_direct_message(recipient_id, text, [quick_reply_type], \
                                    [attachment_type], [attachment_media_id])

   Sends a new direct message to the specified user from the authenticating
   user.

   :param recipient_id: The ID of the user who should receive the direct
                        message.
   :param text: The text of your Direct Message. Max length of 10,000
                characters.
   :param quick_reply_type: The Quick Reply type to present to the user:

                            * options - Array of Options objects (20 max).
                            * text_input - Text Input object.
                            * location - Location object.
   :param attachment_type: The attachment type. Can be media or location.
   :param attachment_media_id: A media id to associate with the message.
                               A Direct Message may only reference a single
                               media_id.
   :rtype: :class:`DirectMessage` object


.. method:: API.destroy_direct_message(id)

   Deletes the direct message specified in the required ID parameter. The
   authenticating user must be the recipient of the specified direct message.
   Direct Messages are only removed from the interface of the user context
   provided. Other members of the conversation can still access the Direct
   Messages.

   :param id: The id of the Direct Message that should be deleted.
   :rtype: None


Account Methods
---------------

.. method:: API.rate_limit_status()

   Returns the current rate limits for methods belonging to the specified
   resource families. When using application-only auth, this method's response
   indicates the application-only auth rate limiting context.

   :param resources: A comma-separated list of resource families you want to
                     know the current rate limit disposition for.
   :rtype: :class:`JSON` object


.. method:: API.update_profile_image(filename)

   Update the authenticating user's profile image. Valid formats: GIF, JPG, or
   PNG

   :param filename: local path to image file to upload. Not a remote URL!
   :rtype: :class:`User` object


.. method:: API.update_profile([name], [url], [location], [description])

   Sets values that users are able to set under the "Account" tab of their
   settings page.

   :param name: Maximum of 20 characters
   :param url: Maximum of 100 characters.
               Will be prepended with "http://" if not present
   :param location: Maximum of 30 characters
   :param description: Maximum of 160 characters
   :rtype: :class:`User` object


Block Methods
-------------

.. method:: API.create_block(id/screen_name/user_id)

   Blocks the user specified in the ID parameter as the authenticating user.
   Destroys a friendship to the blocked user if it exists.

   :param id: |uid|
   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :rtype: :class:`User` object


.. method:: API.destroy_block(id/screen_name/user_id)

   Un-blocks the user specified in the ID parameter for the authenticating
   user.

   :param id: |uid|
   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :rtype: :class:`User` object


.. method:: API.blocks([page])

   Returns an array of user objects that the authenticating user is blocking.

   :param page: |page|
   :rtype: list of :class:`User` objects


.. method:: API.blocks_ids([cursor])

   Returns an array of numeric user ids the authenticating user is blocking.

   :param cursor: |cursor|
   :rtype: list of Integers


Mute Methods
------------

.. method:: API.create_mute(id/screen_name/user_id)

   Mutes the user specified in the ID parameter for the authenticating user.

   :param id: |uid|
   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :rtype: :class:`User` object


.. method:: API.destroy_mute(id/screen_name/user_id)

   Un-mutes the user specified in the ID parameter for the authenticating user.

   :param id: |uid|
   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :rtype: :class:`User` object


.. method:: API.mutes([cursor], [include_entities], [skip_status])

   Returns an array of user objects the authenticating user has muted.

   :param cursor: |cursor|
   :param include_entities: |include_entities|
   :param skip_status: |skip_status|
   :rtype: list of :class:`User` objects


.. method:: API.mutes_ids([cursor])

   Returns an array of numeric user ids the authenticating user has muted.

   :param cursor: |cursor|
   :rtype: list of Integers


Spam Reporting Methods
----------------------

.. method:: API.report_spam(id/screen_name/user_id, [perform_block])

   The user specified in the id is blocked by the authenticated user and
   reported as a spammer.

   :param id: |uid|
   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :param perform_block: A boolean indicating if the reported account should be
                         blocked. Defaults to True.
   :rtype: :class:`User` object


Saved Searches Methods
----------------------

.. method:: API.saved_searches()

   Returns the authenticated user's saved search queries.

   :rtype: list of :class:`SavedSearch` objects


.. method:: API.get_saved_search(id)

   Retrieve the data for a saved search owned by the authenticating user
   specified by the given id.

   :param id: The id of the saved search to be retrieved.
   :rtype: :class:`SavedSearch` object


.. method:: API.create_saved_search(query)

   Creates a saved search for the authenticated user.

   :param query: The query of the search the user would like to save.
   :rtype: :class:`SavedSearch` object


.. method:: API.destroy_saved_search(id)

   Destroys a saved search for the authenticated user. The search specified by
   id must be owned by the authenticating user.

   :param id: The id of the saved search to be deleted.
   :rtype: :class:`SavedSearch` object


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


Trends Methods
--------------

.. method:: API.trends_available()

   Returns the locations that Twitter has trending topic information for.
   The response is an array of "locations" that encode the location's WOEID
   (a Yahoo! Where On Earth ID) and some other human-readable information such
   as a canonical name and country the location belongs in.

   :rtype: :class:`JSON` object


.. method:: API.trends_place(id, [exclude])

   Returns the top 50 trending topics for a specific WOEID,
   if trending information is available for it.

   The response is an array of “trend” objects that encode the name of the
   trending topic, the query parameter that can be used to search for the topic
   on Twitter Search, and the Twitter Search URL.

   This information is cached for 5 minutes. Requesting more frequently than
   that will not return any more data, and will count against your rate limit
   usage.

   The tweet_volume for the last 24 hours is also returned for many trends if
   this is available.

   :param id: The Yahoo! Where On Earth ID of the location to return trending
              information for. Global information is available by using 1 as
              the WOEID.
   :param exclude: Setting this equal to hashtags will remove all hashtags
                   from the trends list.
   :rtype: :class:`JSON` object


.. method:: API.trends_closest(lat, long)

   Returns the locations that Twitter has trending topic information for,
   closest to a specified location.

   The response is an array of “locations” that encode the location’s WOEID and
   some other human-readable information such as a canonical name and country
   the location belongs in.

   A WOEID is a Yahoo! Where On Earth ID.

   :param lat: If provided with a long parameter the available trend locations
               will be sorted by distance, nearest to furthest, to the
               co-ordinate pair. The valid ranges for longitude is -180.0 to
               +180.0 (West is negative, East is positive) inclusive.
   :param long: If provided with a lat parameter the available trend locations
                will be sorted by distance, nearest to furthest, to the
                co-ordinate pair. The valid ranges for longitude is -180.0 to
                +180.0 (West is negative, East is positive) inclusive.
   :rtype: :class:`JSON` object


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


.. method:: API.geo_id(id)

   Given *id* of a place, provide more details about that place.

   :param id: Valid Twitter ID of a location.


Utility methods
---------------

.. method:: API.configuration()

   Returns the current configuration used by Twitter including twitter.com
   slugs which are not usernames, maximum photo resolutions, and t.co
   shortened URL length. It is recommended applications request this endpoint
   when they are loaded, but no more than once a day.


Media methods
-------------

.. method:: API.media_upload(filename, [file], [chunked], [media_category], \
                             [additional_owners])

   Use this to upload media to Twitter.
   This calls either :func:`API.simple_upload` or :func:`API.chunked_upload`.
   Chunked media upload is automatically used for videos.
   If ``chunked`` is set or the media is a video, ``wait_for_async_finalize``
   can be specified as a keyword argument to be passed to
   :func:`API.chunked_upload`.

   :param filename: |filename|
   :param file: |file|
   :param chunked: Whether or not to use chunked media upload. Videos use
                   chunked upload regardless of this parameter. Defaults to
                   False.
   :param media_category: |media_category|
   :param additional_owners: |additional_owners|

   :rtype: :class:`Media` object


.. method:: API.simple_upload(filename, [file], [media_category], \
                              [additional_owners])

   Use this endpoint to upload media to Twitter.
   This does not use the chunked upload endpoints.

   :param filename: |filename|
   :param file: |file|
   :param media_category: |media_category|
   :param additional_owners: |additional_owners|

   :rtype: :class:`Media` object


.. method:: API.chunked_upload(filename, [file], [file_type], \
                               [wait_for_async_finalize], [media_category], \
                               [additional_owners])

   Use this to upload media to Twitter.
   This uses the chunked upload endpoints and calls
   :func:`API.chunked_upload_init`, :func:`API.chunked_upload_append`, and
   :func:`API.chunked_upload_finalize`.
   If ``wait_for_async_finalize`` is set, this calls
   :func:`API.get_media_upload_status` as well.

   :param filename: |filename|
   :param file: |file|
   :param file_type: The MIME type of the media being uploaded.
   :param wait_for_async_finalize: Whether to wait for Twitter's API to finish
                                   processing the media. Defaults to ``True``.
   :param media_category: |media_category|
   :param additional_owners: |additional_owners|

   :rtype: :class:`Media` object


.. method:: API.chunked_upload_init(total_bytes, media_type, \
                                    [media_category], [additional_owners])

   Use this endpoint to initiate a chunked file upload session.

   :param total_bytes: The size of the media being uploaded in bytes.
   :param media_type: The MIME type of the media being uploaded.
   :param media_category: |media_category|
   :param additional_owners: |additional_owners|

   :rtype: :class:`Media` object


.. method:: API.chunked_upload_append(media_id, media, segment_index)

   Use this endpoint to upload a chunk (consecutive byte range) of the media
   file.

   :param media_id: The ``media_id`` returned from the initialization.
   :param media: The raw binary file content being uploaded. It must be <= 5
                 MB.
   :param segment_index: An ordered index of file chunk. It must be between
                         0-999 inclusive. The first segment has index 0, second
                         segment has index 1, and so on.


.. method:: API.chunked_upload_finalize(media_id)

   Use this endpoint after the entire media file is uploaded via appending.
   If (and only if) the response contains a ``processing_info field``, it may
   also be necessary to check its status and wait for it to return success
   before proceeding to Tweet creation.

   :param media_id: The ``media_id`` returned from the initialization.

   :rtype: :class:`Media` object


.. method:: API.create_media_metadata(media_id, alt_text)

   This endpoint can be used to provide additional information about the
   uploaded media_id. This feature is currently only supported for images and
   GIFs. Call this endpoint to attach additional metadata such as image alt
   text.

   :param media_id: The ID of the media to add alt text to.
   :param alt_text: The alt text to add to the image.


.. method:: API.get_media_upload_status(media_id)

   This endpoints sends a STATUS command that will check on the progress of
   a chunked media upload. If the upload has succeeded, it's safe to create
   a tweet with this ``media_id``\ .

   :param media_id: The ID of the media to check.


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
