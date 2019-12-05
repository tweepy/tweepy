.. _api_reference:

.. include:: parameters.rst

API Reference
=============

This page contains some basic documentation for the Tweepy module.


:mod:`tweepy.api` --- Twitter API wrapper
=========================================

.. class:: API([auth_handler=None], [host='api.twitter.com'], \
               [search_host='search.twitter.com'], [cache=None], \
               [api_root='/1'], [search_root=''], [retry_count=0], \
               [retry_delay=0], [retry_errors=None], [timeout=60], \
               [parser=ModelParser], [compression=False], \
               [wait_on_rate_limit=False], [wait_on_rate_limit_notify=False], \
               [proxy=None])

   This class provides a wrapper for the API as provided by Twitter.
   The functions provided in this class are listed below.

   :param auth_handler: authentication handler to be used
   :param host: general API host
   :param search_host: search API host
   :param cache: cache backend to use
   :param api_root: general API path root
   :param search_root: search API path root
   :param retry_count: default number of retries to attempt when error occurs
   :param retry_delay: number of seconds to wait between retries
   :param retry_errors: which HTTP status codes to retry
   :param timeout: The maximum amount of time to wait for a response from
                   Twitter
   :param parser: The object to use for parsing the response from Twitter
   :param compression: Whether or not to use GZIP compression for requests
   :param wait_on_rate_limit: Whether or not to automatically wait for rate
                              limits to replenish
   :param wait_on_rate_limit_notify: Whether or not to print a notification
                                     when Tweepy is waiting for rate limits to
                                     replenish
   :param proxy: The full url to an HTTPS proxy to use for connecting to
                 Twitter.


Timeline methods
----------------

.. method:: API.home_timeline([since_id], [max_id], [count], [page])

   Returns the 20 most recent statuses, including retweets, posted by the
   authenticating user and that user's friends. This is the equivalent of
   /timeline/home on the Web.

   :param since_id: |since_id|
   :param max_id: |max_id|
   :param count: |count|
   :param page: |page|
   :rtype: list of :class:`Status` objects


.. method:: API.statuses_lookup(id_, [include_entities], [trim_user], [map_], \
                                [include_ext_alt_text], [include_card_uri])

   Returns full Tweet objects for up to 100 tweets per request, specified by
   the ``id_`` parameter.

   :param id\_: A list of Tweet IDs to lookup, up to 100
   :param include_entities: |include_entities|
   :param trim_user: |trim_user|
   :param map\_: A boolean indicating whether or not to include tweets that
                 cannot be shown. Defaults to False.
   :param include_ext_alt_text: |include_ext_alt_text|
   :param include_card_uri: |include_card_uri|
   :rtype: list of :class:`Status` objects


.. method:: API.user_timeline([id/user_id/screen_name], [since_id], [max_id], \
                              [count], [page])

   Returns the 20 most recent statuses posted from the authenticating user or
   the user specified. It's also possible to request another user's timeline
   via the id parameter.

   :param id: |uid|
   :param user_id: |user_id|
   :param screen_name: |screen_name|
   :param since_id: |since_id|
   :param max_id: |max_id|
   :param count: |count|
   :param page: |page|
   :rtype: list of :class:`Status` objects


.. method:: API.retweets_of_me([since_id], [max_id], [count], [page])

   Returns the 20 most recent tweets of the authenticated user that have been
   retweeted by others.

   :param since_id: |since_id|
   :param max_id: |max_id|
   :param count: |count|
   :param page: |page|
   :rtype: list of :class:`Status` objects


.. method:: API.mentions_timeline([since_id], [max_id], [count])

   Returns the 20 most recent mentions, including retweets.

   :param since_id: |since_id|
   :param max_id: |max_id|
   :param count: |count|
   :rtype: list of :class:`Status` objects


Status methods
--------------

.. method:: API.get_status(id, [trim_user], [include_my_retweet], \
                           [include_entities], [include_ext_alt_text], \
                           [include_card_uri])

   Returns a single status specified by the ID parameter.

   :param id: |sid|
   :param trim_user: |trim_user|
   :param include_my_retweet: A boolean indicating if any Tweets returned that
      have been retweeted by the authenticating user should include an
      additional current_user_retweet node, containing the ID of the source
      status for the retweet.
   :param include_entities: |include_entities|
   :param include_ext_alt_text: |include_ext_alt_text|
   :param include_card_uri: |include_card_uri|
   :rtype: :class:`Status` object


.. method:: API.update_status(status, [in_reply_to_status_id], \
                              [auto_populate_reply_metadata], \
                              [exclude_reply_user_ids], [attachment_url], \
                              [media_ids], [possibly_sensitive], [lat], \
                              [long], [place_id], [display_coordinates], \
                              [trim_user], [enable_dmcommands], \
                              [fail_dmcommands], [card_uri])

   Updates the authenticating user's current status, also known as Tweeting.

   For each update attempt, the update text is compared with the authenticating
   user's recent Tweets. Any attempt that would result in duplication will be
   blocked, resulting in a 403 error. A user cannot submit the same status
   twice in a row.

   While not rate limited by the API, a user is limited in the number of Tweets
   they can create at a time. If the number of updates posted by the user
   reaches the current allowed limit this method will return an HTTP 403 error.

   :param status: The text of your status update.
   :param in_reply_to_status_id: The ID of an existing status that the update
      is in reply to. Note: This parameter will be ignored unless the author of
      the Tweet this parameter references is mentioned within the status text.
      Therefore, you must include @username, where username is the author of
      the referenced Tweet, within the update.
   :param auto_populate_reply_metadata: If set to true and used with
      in_reply_to_status_id, leading @mentions will be looked up from the
      original Tweet, and added to the new Tweet from there. This wil append
      @mentions into the metadata of an extended Tweet as a reply chain grows,
      until the limit on @mentions is reached. In cases where the original
      Tweet has been deleted, the reply will fail.
   :param exclude_reply_user_ids: When used with auto_populate_reply_metadata,
      a comma-separated list of user ids which will be removed from the
      server-generated @mentions prefix on an extended Tweet. Note that the
      leading @mention cannot be removed as it would break the
      in-reply-to-status-id semantics. Attempting to remove it will be
      silently ignored.
   :param attachment_url: In order for a URL to not be counted in the status
      body of an extended Tweet, provide a URL as a Tweet attachment. This URL
      must be a Tweet permalink, or Direct Message deep link. Arbitrary,
      non-Twitter URLs must remain in the status text. URLs passed to the
      attachment_url parameter not matching either a Tweet permalink or Direct
      Message deep link will fail at Tweet creation and cause an exception.
   :param media_ids: A list of media_ids to associate with the Tweet.
      You may include up to 4 photos or 1 animated GIF or 1 video in a Tweet.
   :param possibly_sensitive: If you upload Tweet media that might be
      considered sensitive content such as nudity, or medical procedures, you
      must set this value to true.
   :param lat: The latitude of the location this Tweet refers to. This
      parameter will be ignored unless it is inside the range -90.0 to +90.0
      (North is positive) inclusive. It will also be ignored if there is no
      corresponding long parameter.
   :param long: The longitude of the location this Tweet refers to. The valid
      ranges for longitude are -180.0 to +180.0 (East is positive) inclusive.
      This parameter will be ignored if outside that range, if it is not a
      number, if geo_enabled is disabled, or if there no corresponding lat
      parameter.
   :param place_id: A place in the world.
   :param display_coordinates: Whether or not to put a pin on the exact
      coordinates a Tweet has been sent from.
   :param trim_user: |trim_user|
   :param enable_dmcommands: When set to true, enables shortcode commands for
      sending Direct Messages as part of the status text to send a Direct
      Message to a user. When set to false, disables this behavior and includes
      any leading characters in the status text that is posted
   :param fail_dmcommands: When set to true, causes any status text that starts
      with shortcode commands to return an API error. When set to false, allows
      shortcode commands to be sent in the status text and acted on by the API.
   :param card_uri: Associate an ads card with the Tweet using the card_uri
      value from any ads card response.
   :rtype: :class:`Status` object


.. method:: API.update_with_media(filename, [status], \
                                  [in_reply_to_status_id], \
                                  [auto_populate_reply_metadata], [lat], \
                                  [long], [source], [place_id], [file])

   *Deprecated*: Use :func:`API.media_upload` instead. Update the authenticated
   user's status. Statuses that are duplicates or too long will be silently
   ignored.

   :param filename: The filename of the image to upload. This will
                    automatically be opened unless `file` is specified
   :param status: The text of your status update.
   :param in_reply_to_status_id: The ID of an existing status that the update
                                 is in reply to.
   :param auto_populate_reply_metadata: Whether to automatically include the
                                        @mentions in the status metadata.
   :param lat: The location's latitude that this tweet refers to.
   :param long: The location's longitude that this tweet refers to.
   :param source: Source of the update. Only supported by Identi.ca. Twitter
                  ignores this parameter.
   :param place_id: Twitter ID of location which is listed in the Tweet if
                    geolocation is enabled for the user.
   :param file: A file object, which will be used instead of opening
                `filename`. `filename` is still required, for MIME type
                detection and to use as a form field in the POST data
   :rtype: :class:`Status` object


.. method:: API.destroy_status(id)

   Destroy the status specified by the id parameter. The authenticated user
   must be the author of the status to destroy.

   :param id: |sid|
   :rtype: :class:`Status` object


.. method:: API.retweet(id)

   Retweets a tweet. Requires the id of the tweet you are retweeting.

   :param id: |sid|
   :rtype: :class:`Status` object


.. method:: API.retweeters(id, [cursor], [stringify_ids])

   Returns up to 100 user IDs belonging to users who have retweeted the Tweet
   specified by the id parameter.

   :param id: |sid|
   :param cursor: |cursor|
   :param stringify_ids: Have ids returned as strings instead.
   :rtype: list of Integers


.. method:: API.retweets(id, [count])

   Returns up to 100 of the first retweets of the given tweet.

   :param id: |sid|
   :param count: Specifies the number of retweets to retrieve.
   :rtype: list of :class:`Status` objects


.. method:: API.unretweet(id)

   Untweets a retweeted status. Requires the id of the retweet to unretweet.

   :param id: |sid|
   :rtype: :class:`Status` object


User methods
------------

.. method:: API.get_user(id/user_id/screen_name)

   Returns information about the specified user.

   :param id: |uid|
   :param user_id: |user_id|
   :param screen_name: |screen_name|
   :rtype: :class:`User` object


.. method:: API.me()

   Returns the authenticated user's information.

   :rtype: :class:`User` object


.. method:: API.friends([id/user_id/screen_name], [cursor], [skip_status], \
                        [include_user_entities])

   Returns an user's friends ordered in which they were added 100 at a time.
   If no user is specified it defaults to the authenticated user.

   :param id: |uid|
   :param user_id: |user_id|
   :param screen_name: |screen_name|
   :param cursor: |cursor|
   :param count: |count|
   :param skip_status: |skip_status|
   :param include_user_entities: |include_user_entities|
   :rtype: list of :class:`User` objects


.. method:: API.followers([id/screen_name/user_id], [cursor])

   Returns a user's followers ordered in which they were added. If no user is
   specified by id/screen name, it defaults to the authenticated user.

   :param id: |uid|
   :param user_id: |user_id|
   :param screen_name: |screen_name|
   :param cursor: |cursor|
   :param count: |count|
   :param skip_status: |skip_status|
   :param include_user_entities: |include_user_entities|
   :rtype: list of :class:`User` objects


.. method:: API.lookup_users([user_ids], [screen_names], [include_entities], \
                             [tweet_mode])

   Returns fully-hydrated user objects for up to 100 users per request.

   There are a few things to note when using this method.

   * You must be following a protected user to be able to see their most recent
     status update. If you don't follow a protected user their status will be
     removed.
   * The order of user IDs or screen names may not match the order of users in
     the returned array.
   * If a requested user is unknown, suspended, or deleted, then that user will
     not be returned in the results list.
   * If none of your lookup criteria can be satisfied by returning a user
     object, a HTTP 404 will be thrown.

   :param user_ids: A list of user IDs, up to 100 are allowed in a single
                    request.
   :param screen_names: A list of screen names, up to 100 are allowed in a
                        single request.
   :param include_entities: |include_entities|
   :param tweet_mode: Valid request values are compat and extended, which give
                      compatibility mode and extended mode, respectively for
                      Tweets that contain over 140 characters.
   :rtype: list of :class:`User` objects


.. method:: API.search_users(q, [count], [page])

   Run a search for users similar to Find People button on Twitter.com; the
   same results returned by people search on Twitter.com will be returned by
   using this API (about being listed in the People Search). It is only
   possible to retrieve the first 1000 matches from this API.

   :param q: The query to run against people search.
   :param count: Specifies the number of statuses to retrieve.
                 May not be greater than 20.
   :param page: |page|
   :rtype: list of :class:`User` objects


Direct Message Methods
----------------------

.. method:: API.get_direct_message([id], [full_text])

   Returns a specific direct message.

   :param id: |id|
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


Friendship Methods
------------------

.. method:: API.create_friendship(id/screen_name/user_id, [follow])

   Create a new friendship with the specified user (aka follow).

   :param id: |uid|
   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :param follow: Enable notifications for the target user in addition to
                  becoming friends.
   :rtype: :class:`User` object


.. method:: API.destroy_friendship(id/screen_name/user_id)

   Destroy a friendship with the specified user (aka unfollow).

   :param id: |uid|
   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :rtype: :class:`User` object


.. method:: API.show_friendship(source_id/source_screen_name, \
                                target_id/target_screen_name)

   Returns detailed information about the relationship between two users.

   :param source_id: The user_id of the subject user.
   :param source_screen_name: The screen_name of the subject user.
   :param target_id: The user_id of the target user.
   :param target_screen_name: The screen_name of the target user.
   :rtype: :class:`Friendship` object


.. method:: API.friends_ids(id/screen_name/user_id, [cursor])

   Returns an array containing the IDs of users being followed by the specified
   user.

   :param id: |uid|
   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :param cursor: |cursor|
   :rtype: list of Integers


.. method:: API.followers_ids(id/screen_name/user_id)

   Returns an array containing the IDs of users following the specified user.

   :param id: |uid|
   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :param cursor: |cursor|
   :rtype: list of Integers


Account Methods
---------------

.. method:: API.verify_credentials([include_entities], [skip_status], \
                                   [include_email])

   Verify the supplied user credentials are valid.

   :param include_entities: |include_entities|
   :param skip_status: |skip_status|
   :param include_email: When set to true email will be returned in the user
                         objects as a string.
   :rtype: :class:`User` object if credentials are valid, otherwise False


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


.. method:: API.update_profile_background_image(filename)

   Update authenticating user's background image. Valid formats: GIF, JPG, or
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


Favorite Methods
----------------

.. method:: API.favorites([id], [page])

   Returns the favorite statuses for the authenticating user or user specified
   by the ID parameter.

   :param id: The ID or screen name of the user to request favorites
   :param page: |page|
   :rtype: list of :class:`Status` objects


.. method:: API.create_favorite(id)

   Favorites the status specified in the ID parameter as the authenticating
   user.

   :param id: |sid|
   :rtype: :class:`Status` object


.. method:: API.destroy_favorite(id)

   Un-favorites the status specified in the ID parameter as the authenticating
   user.

   :param id: |sid|
   :rtype: :class:`Status` object


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

.. method:: API.search(q, [geocode], [lang], [locale], [result_type], \
                       [count], [until], [since_id], [max_id], \
                       [include_entities])

   Returns a collection of relevant Tweets matching a specified query.

   Please note that Twitter's search service and, by extension, the Search API
   is not meant to be an exhaustive source of Tweets. Not all Tweets will be
   indexed or made available via the search interface.

   In API v1.1, the response format of the Search API has been improved to
   return Tweet objects more similar to the objects you’ll find across the REST
   API and platform. However, perspectival attributes (fields that pertain to
   the perspective of the authenticating user) are not currently supported on
   this endpoint.\ [#]_\ [#]_

   :param q: the search query string of 500 characters maximum, including
      operators. Queries may additionally be limited by complexity.
   :param geocode: Returns tweets by users located within a given radius of the
      given latitude/longitude.  The location is preferentially taking from the
      Geotagging API, but will fall back to their Twitter profile. The
      parameter value is specified by "latitide,longitude,radius", where radius
      units must be specified as either "mi" (miles) or "km" (kilometers). Note
      that you cannot use the near operator via the API to geocode arbitrary
      locations; however you can use this geocode parameter to search near
      geocodes directly. A maximum of 1,000 distinct "sub-regions" will be
      considered when using the radius modifier.
   :param lang: Restricts tweets to the given language, given by an ISO 639-1
      code. Language detection is best-effort.
   :param locale: Specify the language of the query you are sending (only ja is
      currently effective). This is intended for language-specific consumers
      and the default should work in the majority of cases.
   :param result_type: Specifies what type of search results you would prefer
      to receive. The current default is "mixed." Valid values include:

      * mixed : include both popular and real time results in the response
      * recent : return only the most recent results in the response
      * popular : return only the most popular results in the response
   :param count: |count|
   :param until: Returns tweets created before the given date. Date should be
      formatted as YYYY-MM-DD. Keep in mind that the search index has a 7-day
      limit. In other words, no tweets will be found for a date older than one
      week.
   :param since_id: |since_id| There are limits to the number of Tweets which
      can be accessed through the API. If the limit of Tweets has occurred
      since the since_id, the since_id will be forced to the oldest ID
      available.
   :param max_id: |max_id|
   :param include_entities: |include_entities|
   :rtype: :class:`SearchResults` object


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


List Methods
------------

.. method:: API.create_list(name, [mode], [description])

   Creates a new list for the authenticated user.
   Note that you can create up to 1000 lists per account.

   :param name: The name of the new list.
   :param mode: |list_mode|
   :param description: The description of the list you are creating.
   :rtype: :class:`List` object


.. method:: API.destroy_list([owner_screen_name/owner_id], list_id/slug)

   Deletes the specified list.
   The authenticated user must own the list to be able to destroy it.

   :param owner_screen_name: |owner_screen_name|
   :param owner_id: |owner_id|
   :param list_id: |list_id|
   :param slug: |slug|
   :rtype: :class:`List` object


.. method:: API.update_list(list_id/slug, [name], [mode], [description], \
                            [owner_screen_name/owner_id])

   Updates the specified list.
   The authenticated user must own the list to be able to update it.

   :param list_id: |list_id|
   :param slug: |slug|
   :param name: The name for the list.
   :param mode: |list_mode|
   :param description: The description to give the list.
   :param owner_screen_name: |owner_screen_name|
   :param owner_id: |owner_id|
   :rtype: :class:`List` object


.. method:: API.lists_all([screen_name], [user_id], [reverse])

   Returns all lists the authenticating or specified user subscribes to,
   including their own. The user is specified using the ``user_id`` or
   ``screen_name`` parameters. If no user is given, the authenticating user is
   used.

   A maximum of 100 results will be returned by this call. Subscribed lists are
   returned first, followed by owned lists. This means that if a user
   subscribes to 90 lists and owns 20 lists, this method returns 90
   subscriptions and 10 owned lists. The ``reverse`` method returns owned lists
   first, so with ``reverse=true``, 20 owned lists and 80 subscriptions would
   be returned.

   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :param reverse: A boolean indicating if you would like owned lists to be
                   returned first. See description above for information on how
                   this parameter works.
   :rtype: list of :class:`List` objects


.. method:: API.lists_memberships([screen_name], [user_id], \
                                  [filter_to_owned_lists], [cursor], [count])

   Returns the lists the specified user has been added to. If ``user_id`` or
   ``screen_name`` are not provided, the memberships for the authenticating
   user are returned.

   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :param filter_to_owned_lists: A boolean indicating whether to return just
      lists the authenticating user owns, and the user represented by
      ``user_id`` or ``screen_name`` is a member of.
   :param cursor: |cursor|
   :param count: |count|
   :rtype: list of :class:`List` objects


.. method:: API.lists_subscriptions([screen_name], [user_id], [cursor], \
                                    [count])

   Obtain a collection of the lists the specified user is subscribed to, 20
   lists per page by default. Does not include the user's own lists.

   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :param cursor: |cursor|
   :param count: |count|
   :rtype: list of :class:`List` objects


.. method:: API.list_timeline(list_id/slug, [owner_id/owner_screen_name], \
                              [since_id], [max_id], [count], \
                              [include_entities], [include_rts])

   Returns a timeline of tweets authored by members of the specified list.
   Retweets are included by default. Use the ``include_rts=false`` parameter to
   omit retweets.

   :param list_id: |list_id|
   :param slug: |slug|
   :param owner_id: |owner_id|
   :param owner_screen_name: |owner_screen_name|
   :param since_id: |since_id|
   :param max_id: |max_id|
   :param count: |count|
   :param include_entities: |include_entities|
   :param include_rts: A boolean indicating whether the list timeline will
      contain native retweets (if they exist) in addition to the standard
      stream of tweets. The output format of retweeted tweets is identical to
      the representation you see in home_timeline.
   :rtype: list of :class:`Status` objects


.. method:: API.get_list(list_id/slug, [owner_id/owner_screen_name])

   Returns the specified list. Private lists will only be shown if the
   authenticated user owns the specified list.

   :param list_id: |list_id|
   :param slug: |slug|
   :param owner_id: |owner_id|
   :param owner_screen_name: |owner_screen_name|
   :rtype: :class:`List` object


.. method:: API.add_list_member(list_id/slug, screen_name/user_id, \
                                [owner_id/owner_screen_name])

   Add a member to a list. The authenticated user must own the list to be able
   to add members to it. Lists are limited to 5,000 members.

   :param list_id: |list_id|
   :param slug: |slug|
   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :param owner_id: |owner_id|
   :param owner_screen_name: |owner_screen_name|
   :rtype: :class:`List` object


.. method:: API.add_list_members(list_id/slug, screen_name/user_id, \
                                 [owner_id/owner_screen_name])

   Add up to 100 members to a list. The authenticated user must own the list to
   be able to add members to it. Lists are limited to 5,000 members.

   :param list_id: |list_id|
   :param slug: |slug|
   :param screen_name: A comma separated list of screen names, up to 100 are
                       allowed in a single request
   :param user_id: A comma separated list of user IDs, up to 100 are allowed in
                   a single request
   :param owner_id: |owner_id|
   :param owner_screen_name: |owner_screen_name|
   :rtype: :class:`List` object


.. method:: API.remove_list_member(list_id/slug, screen_name/user_id, \
                                   [owner_id/owner_screen_name])

   Removes the specified member from the list. The authenticated user must be
   the list's owner to remove members from the list.

   :param list_id: |list_id|
   :param slug: |slug|
   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :param owner_id: |owner_id|
   :param owner_screen_name: |owner_screen_name|
   :rtype: :class:`List` object


.. method:: API.remove_list_members(list_id/slug, screen_name/user_id, \
                                    [owner_id/owner_screen_name])

   Remove up to 100 members from a list. The authenticated user must own the
   list to be able to remove members from it. Lists are limited to 5,000
   members.

   :param list_id: |list_id|
   :param slug: |slug|
   :param screen_name: A comma separated list of screen names, up to 100 are
                       allowed in a single request
   :param user_id: A comma separated list of user IDs, up to 100 are allowed in
                   a single request
   :param owner_id: |owner_id|
   :param owner_screen_name: |owner_screen_name|
   :rtype: :class:`List` object


.. method:: API.list_members(list_id/slug, [owner_id/owner_screen_name], \
                             [cursor])

   Returns the members of the specified list.

   :param list_id: |list_id|
   :param slug: |slug|
   :param owner_id: |owner_id|
   :param owner_screen_name: |owner_screen_name|
   :param cursor: |cursor|
   :rtype: list of :class:`User` objects


.. method:: API.show_list_member(list_id/slug, screen_name/user_id, \
                                 [owner_id/owner_screen_name])

   Check if the specified user is a member of the specified list.

   :param list_id: |list_id|
   :param slug: |slug|
   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :param owner_id: |owner_id|
   :param owner_screen_name: |owner_screen_name|
   :rtype: :class:`User` object if user is a member of list


.. method:: API.subscribe_list(list_id/slug, [owner_id/owner_screen_name])

   Subscribes the authenticated user to the specified list.

   :param list_id: |list_id|
   :param slug: |slug|
   :param owner_id: |owner_id|
   :param owner_screen_name: |owner_screen_name|
   :rtype: :class:`List` object


.. method:: API.unsubscribe_list(list_id/slug, [owner_id/owner_screen_name])

   Unsubscribes the authenticated user from the specified list.

   :param list_id: |list_id|
   :param slug: |slug|
   :param owner_id: |owner_id|
   :param owner_screen_name: |owner_screen_name|
   :rtype: :class:`List` object


.. method:: API.list_subscribers(list_id/slug, [owner_id/owner_screen_name], \
                                 [cursor], [count], [include_entities], \
                                 [skip_status])

   Returns the subscribers of the specified list. Private list subscribers will
   only be shown if the authenticated user owns the specified list.

   :param list_id: |list_id|
   :param slug: |slug|
   :param owner_id: |owner_id|
   :param owner_screen_name: |owner_screen_name|
   :param cursor: |cursor|
   :param count: |count|
   :param include_entities: |include_entities|
   :param skip_status: |skip_status|
   :rtype: list of :class:`User` objects


.. method:: API.show_list_subscriber(list_id/slug, screen_name/user_id, \
                                     [owner_id/owner_screen_name])

   Check if the specified user is a subscriber of the specified list.

   :param list_id: |list_id|
   :param slug: |slug|
   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :param owner_id: |owner_id|
   :param owner_screen_name: |owner_screen_name|
   :rtype: :class:`User` object if user is subscribed to list


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
   :param granularity: Assumed to be `neighborhood' by default; can also be
                       `city'.
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

.. method:: API.media_upload(filename, [file])

   Use this endpoint to upload images to Twitter.

   :param filename: The filename of the image to upload. This will
                    automatically be opened unless ``file`` is specified.
   :param file: A file object, which will be used instead of opening
                ``filename``. ``filename`` is still required, for MIME type
                detection and to use as a form field in the POST data.
   :rtype: :class:`Media` object


.. method:: API.create_media_metadata(media_id, alt_text)

   This endpoint can be used to provide additional information about the
   uploaded media_id. This feature is currently only supported for images and
   GIFs. Call this endpoint to attach additional metadata such as image alt
   text.

   :param media_id: The ID of the media to add alt text to.
   :param alt_text: The alt text to add to the image.


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
