.. _api_reference:

.. include:: parameters.rst

API Reference
=============

This page contains some basic documentation for the Tweepy module.


:mod:`tweepy.api` --- Twitter API wrapper
=========================================

.. class:: API([auth_handler=None], [host='api.twitter.com'], [search_host='search.twitter.com'], [cache=None], [api_root='/1'], [search_root=''], [retry_count=0], [retry_delay=0], [retry_errors=None], [timeout=60], [parser=ModelParser], [compression=False], [wait_on_rate_limit=False], [wait_on_rate_limit_notify=False], [proxy=None])

   This class provides a wrapper for the API as provided by
   Twitter. The functions provided in this class are listed below.

   :param auth_handler: authentication handler to be used
   :param host: general API host
   :param search_host: search API host
   :param cache: cache backend to use
   :param api_root: general API path root
   :param search_root: search API path root
   :param retry_count: default number of retries to attempt when error occurs
   :param retry_delay: number of seconds to wait between retries
   :param retry_errors: which HTTP status codes to retry
   :param timeout: The maximum amount of time to wait for a response from Twitter
   :param parser: The object to use for parsing the response from Twitter
   :param compression: Whether or not to use GZIP compression for requests
   :param wait_on_rate_limit: Whether or not to automatically wait for rate limits to replenish
   :param wait_on_rate_limit_notify: Whether or not to print a notification when Tweepy is waiting for rate limits to replenish
   :param proxy: The full url to an HTTPS proxy to use for connecting to Twitter.

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

.. method:: API.statuses_lookup(id_, [include_entities], [trim_user], [map_])

   Returns full Tweet objects for up to 100 tweets per request, specified by the
   `id` parameter.

   :param id_: A list of Tweet IDs to lookup, up to 100
   :param include_entities: A boolean indicating whether or not to include `entities <https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/entities-object>`_ in the returned tweets. Defaults to False.
   :param trim_user: A boolean indicating if user IDs should be provided, instead of full user information. Defaults to False.
   :param map_: A boolean indicating whether or not to include tweets that cannot be shown. Defaults to False.
   :rtype: list of :class:`Status` objects


.. method:: API.user_timeline([id/user_id/screen_name], [since_id], [max_id], [count], [page])

   Returns the 20 most recent statuses posted from the authenticating
   user or the user specified. It's also possible to request another user's timeline via the id
   parameter.

   :param id: |uid|
   :param user_id: |user_id|
   :param screen_name: |screen_name|
   :param since_id: |since_id|
   :param max_id: |max_id|
   :param count: |count|
   :param page: |page|
   :rtype: list of :class:`Status` objects


.. method:: API.retweets_of_me([since_id], [max_id], [count], [page])

   Returns the 20 most recent tweets of the authenticated user that have
   been retweeted by others.

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

.. method:: API.get_status(id)

   Returns a single status specified by the ID parameter.

   :param id: |sid|
   :rtype: :class:`Status` object


.. method:: API.update_status(status, [in_reply_to_status_id], [in_reply_to_status_id_str], [auto_populate_reply_metadata], [lat], [long], [source], [place_id], [display_coordinates], [media_ids])

   Update the authenticated user's status. Statuses that are duplicates
   or too long will be silently ignored.

   :param status: The text of your status update.
   :param in_reply_to_status_id: The ID of an existing status that the update is in reply to.
   :param in_reply_to_status_id_str: The ID of an existing status that the update is in reply to (as string).
   :param auto_populate_reply_metadata: Whether to automatically include the @mentions in the status metadata.
   :param lat: The location's latitude that this tweet refers to.
   :param long: The location's longitude that this tweet refers to.
   :param source: Source of the update. Only supported by Identi.ca. Twitter ignores this parameter.
   :param place_id: Twitter ID of location which is listed in the Tweet if geolocation is enabled for the user.
   :param display_coordinates: Whether or not to put a pin on the exact coordinates a Tweet has been sent from.
   :param media_ids: A list of media_ids to associate with the Tweet.
   :rtype: :class:`Status` object


.. method:: API.update_with_media(filename, [status], [in_reply_to_status_id], [auto_populate_reply_metadata], [lat], [long], [source], [place_id], [file])

   *Deprecated*: Use :func:`API.media_upload` instead. Update the authenticated user's status. Statuses that are duplicates
   or too long will be silently ignored.

   :param filename: The filename of the image to upload. This will automatically be opened unless `file` is specified
   :param status: The text of your status update.
   :param in_reply_to_status_id: The ID of an existing status that the update is in reply to.
   :param auto_populate_reply_metadata: Whether to automatically include the @mentions in the status metadata.
   :param lat: The location's latitude that this tweet refers to.
   :param long: The location's longitude that this tweet refers to.
   :param source: Source of the update. Only supported by Identi.ca. Twitter ignores this parameter.
   :param place_id: Twitter ID of location which is listed in the Tweet if geolocation is enabled for the user.
   :param file: A file object, which will be used instead of opening `filename`. `filename` is still required, for MIME type detection and to use as a form field in the POST data
   :rtype: :class:`Status` object


.. method:: API.destroy_status(id)

   Destroy the status specified by the id parameter. The authenticated
   user must be the author of the status to destroy.

   :param id: |sid|
   :rtype: :class:`Status` object


.. method:: API.retweet(id)

   Retweets a tweet. Requires the id of the tweet you are retweeting.

   :param id: |sid|
   :rtype: :class:`Status` object

.. method:: API.retweeters(id, [cursor], [stringify_ids])

   Returns up to 100 user IDs belonging to users who have retweeted the Tweet specified by the id parameter.

   :param id: |sid|
   :param cursor: |cursor|
   :param stringify_ids: Have ids returned as strings instead.
   :rtype: list of Integers

.. method:: API.retweets(id[,count])

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


.. method:: API.friends([id/user_id/screen_name], [cursor], [skip_status], [include_user_entities])

   Returns an user's friends ordered in which they were added 100 at a time. If no user is specified it defaults to the authenticated user.

   :param id: |uid|
   :param user_id: |user_id|
   :param screen_name: |screen_name|
   :param cursor: |cursor|
   :param count: |count|
   :param skip_status: |skip_status|
   :param include_user_entities: |include_user_entities|
   :rtype: list of :class:`User` objects


.. method:: API.followers([id/screen_name/user_id], [cursor])

   Returns a user's followers ordered in which they were added.
   If no user is specified by id/screen name, it defaults to the
   authenticated user.

   :param id: |uid|
   :param user_id: |user_id|
   :param screen_name: |screen_name|
   :param cursor: |cursor|
   :param count: |count|
   :param skip_status: |skip_status|
   :param include_user_entities: |include_user_entities|
   :rtype: list of :class:`User` objects

.. method:: API.search_users(q, [count], [page])

   Run a search for users similar to Find People button on Twitter.com;
   the same results returned by people search on Twitter.com will be
   returned by using this API (about being listed in the People
   Search). It is only possible to retrieve the first 1000 matches from
   this API.

   :param q: The query to run against people search.
   :param count: Specifies the number of statuses to retrieve. May not be greater than 20.
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

   Returns all Direct Message events (both sent and received)
   within the last 30 days. Sorted in reverse-chronological order.

   :param count: |count|
   :param cursor: |cursor|
   :rtype: list of :class:`DirectMessage` objects


.. method:: API.send_direct_message(recipient_id, text, [quick_reply_type], [attachment_type], [attachment_media_id])

   Sends a new direct message to the specified user from the
   authenticating user.

   :param recipient_id: The ID of the user who should receive the direct message.
   :param text: The text of your Direct Message. Max length of 10,000 characters.
   :param quick_reply_type: The Quick Reply type to present to the user:

                       * options - Array of Options objects (20 max).
                       * text_input - Text Input object.
                       * location - Location object.
   :param attachment_type: The attachment type. Can be media or location.
   :param attachment_media_id: A media id to associate with the message. A Direct Message may only reference a single media_id.
   :rtype: :class:`DirectMessage` object


.. method:: API.destroy_direct_message(id)

   Deletes the direct message specified in the required ID parameter.
   The authenticating user must be the recipient of the specified direct message.
   Direct Messages are only removed from the interface of the user context provided.
   Other members of the conversation can still access the Direct Messages.

   :param id: The id of the Direct Message that should be deleted.
   :rtype: None


Friendship Methods
------------------

.. method:: API.create_friendship(id/screen_name/user_id[,follow])

   Create a new friendship with the specified user (aka follow).

   :param id: |uid|
   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :param follow: Enable notifications for the target user in addition to becoming friends.
   :rtype: :class:`User` object


.. method:: API.destroy_friendship(id/screen_name/user_id)

   Destroy a friendship with the specified user (aka unfollow).

   :param id: |uid|
   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :rtype: :class:`User` object


.. method:: API.show_friendship(source_id/source_screen_name, target_id/target_screen_name)

   Returns detailed information about the relationship between two users.

   :param source_id: The user_id of the subject user.
   :param source_screen_name: The screen_name of the subject user.
   :param target_id: The user_id of the target user.
   :param target_screen_name: The screen_name of the target user.
   :rtype: :class:`Friendship` object


.. method:: API.friends_ids(id/screen_name/user_id[,cursor])

   Returns an array containing the IDs of users being followed by the
   specified user.

   :param id: |uid|
   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :param cursor: |cursor|
   :rtype: list of Integers


.. method:: API.followers_ids(id/screen_name/user_id)

   Returns an array containing the IDs of users following the specified
   user.

   :param id: |uid|
   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :param cursor: |cursor|
   :rtype: list of Integers


Account Methods
---------------

.. method:: API.verify_credentials()

   Verify the supplied user credentials are valid.

   :rtype: :class:`User` object if credentials are valid, otherwise False


.. method:: API.rate_limit_status()

   Returns the remaining number of API requests available to the
   requesting user before the API limit is reached for the current
   hour. Calls to rate_limit_status do not count against the rate
   limit. If authentication credentials are provided, the rate limit
   status for the authenticating user is returned. Otherwise, the rate
   limit status for the requester's IP address is returned.

   :rtype: :class:`JSON` object


.. method:: API.update_profile_image(filename)

   Update the authenticating user's profile image. Valid formats: GIF,
   JPG, or PNG

   :param filename: local path to image file to upload. Not a remote URL!
   :rtype: :class:`User` object


.. method:: API.update_profile_background_image(filename)

   Update authenticating user's background image. Valid formats: GIF,
   JPG, or PNG

   :param filename: local path to image file to upload. Not a remote URL!
   :rtype: :class:`User` object


.. method:: API.update_profile([name], [url], [location], [description])

   Sets values that users are able to set under the "Account" tab of
   their settings page.

   :param name: Maximum of 20 characters
   :param url: Maximum of 100 characters. Will be prepended with "http://" if not present
   :param location: Maximum of 30 characters
   :param description: Maximum of 160 characters
   :rtype: :class:`User` object


Favorite Methods
----------------

.. method:: API.favorites([id], [page])

   Returns the favorite statuses for the authenticating user or user
   specified by the ID parameter.

   :param id: The ID or screen name of the user to request favorites
   :param page: |page|
   :rtype: list of :class:`Status` objects


.. method:: API.create_favorite(id)

   Favorites the status specified in the ID parameter as the
   authenticating user.

   :param id: |sid|
   :rtype: :class:`Status` object


.. method:: API.destroy_favorite(id)

   Un-favorites the status specified in the ID parameter as the
   authenticating user.

   :param id: |sid|
   :rtype: :class:`Status` object


Block Methods
-------------

.. method:: API.create_block(id/screen_name/user_id)

   Blocks the user specified in the ID parameter as the authenticating
   user. Destroys a friendship to the blocked user if it exists.

   :param id: |uid|
   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :rtype: :class:`User` object


.. method:: API.destroy_block(id/screen_name/user_id)

   Un-blocks the user specified in the ID parameter for the
   authenticating user.

   :param id: |uid|
   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :rtype: :class:`User` object


.. method:: API.blocks([page])

   Returns an array of user objects that the authenticating user is
   blocking.

   :param page: |page|
   :rtype: list of :class:`User` objects


.. method:: API.blocks_ids([cursor])

   Returns an array of numeric user ids the authenticating user is
   blocking.

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
   :param perform_block: A boolean indicating if the reported account should be blocked. Defaults to True.
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

   Destroys a saved search for the authenticated user. The search
   specified by id must be owned by the authenticating user.

   :param id: The id of the saved search to be deleted.
   :rtype: :class:`SavedSearch` object


Help Methods
------------

.. method:: API.search(q, [geocode], [lang], [locale], [result_type], [count], [until], [since_id], [max_id], [include_entities])

   Returns tweets that match a specified query.

   :param q: the search query string of 500 characters maximum, including operators. Queries may additionally be limited by complexity.
   :param geocode: Returns tweets by users located within a given radius of the given latitude/longitude.  The location is preferentially taking from the Geotagging API, but will fall back to their Twitter profile. The parameter value is specified by "latitide,longitude,radius", where radius units must be specified as either "mi" (miles) or "km" (kilometers). Note that you cannot use the near operator via the API to geocode arbitrary locations; however you can use this geocode parameter to search near geocodes directly. A maximum of 1,000 distinct "sub-regions" will be considered when using the radius modifier.
   :param lang: Restricts tweets to the given language, given by an ISO 639-1 code. Language detection is best-effort.
   :param locale: Specify the language of the query you are sending (only ja is currently effective). This is intended for language-specific consumers and the default should work in the majority of cases.
   :param result_type: Specifies what type of search results you would prefer to receive. The current default is "mixed." Valid values include:

                       * mixed : include both popular and real time results in the response
                       * recent : return only the most recent results in the response
                       * popular : return only the most popular results in the response
   :param count: The number of tweets to return per page, up to a maximum of 100. Defaults to 15.
   :param until: Returns tweets created before the given date. Date should be formatted as YYYY-MM-DD. Keep in mind that the search index has a 7-day limit. In other words, no tweets will be found for a date older than one week.
   :param since_id: |since_id| There are limits to the number of Tweets which can be accessed through the API. If the limit of Tweets has occured since the since_id, the since_id will be forced to the oldest ID available.	
   :param max_id: |max_id|
   :param include_entities: |include_entities|
   :rtype: :class:`SearchResults` object


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


.. method:: API.update_list(list_id/slug, [name], [mode], [description], [owner_screen_name/owner_id])

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


.. method:: API.lists_all([cursor])

   List the lists of the specified user. Private lists will be included
   if the authenticated users is the same as the user who's lists are
   being returned.

   :param cursor: |cursor|
   :rtype: list of :class:`List` objects


.. method:: API.lists_memberships([cursor])

   List the lists the specified user has been added to.

   :param cursor: |cursor|
   :rtype: list of :class:`List` objects


.. method:: API.lists_subscriptions([cursor])

   List the lists the specified user follows.

   :param cursor: |cursor|
   :rtype: list of :class:`List` objects


.. method:: API.list_timeline(owner, slug, [since_id], [max_id], [count], [page])

   Show tweet timeline for members of the specified list.

   :param owner: |list_owner|
   :param slug: |slug|
   :param since_id: |since_id|
   :param max_id: |max_id|
   :param count: Number of results per a page
   :param page: |page|
   :rtype: list of :class:`Status` objects


.. method:: API.get_list(list_id/slug, [owner_id/owner_screen_name])

   Returns the specified list. Private lists will only be shown if the
   authenticated user owns the specified list.

   :param list_id: |list_id|
   :param slug: |slug|
   :param owner_id: |owner_id|
   :param owner_screen_name: |owner_screen_name|
   :rtype: :class:`List` object


.. method:: API.add_list_member(list_id/slug, screen_name/user_id, [owner_id/owner_screen_name])

   Add a member to a list. The authenticated user must own the list to be
   able to add members to it. Lists are limited to 5,000 members.

   :param list_id: |list_id|
   :param slug: |slug|
   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :param owner_id: |owner_id|
   :param owner_screen_name: |owner_screen_name|
   :rtype: :class:`List` object


.. method:: API.add_list_members(list_id/slug, screen_name/user_id, [owner_id/owner_screen_name])

   Add up to 100 members to a list. The authenticated user must own the list to be
   able to add members to it. Lists are limited to 5,000 members.

   :param list_id: |list_id|
   :param slug: |slug|
   :param screen_name: A comma separated list of screen names, up to 100 are allowed in a single request
   :param user_id: A comma separated list of user IDs, up to 100 are allowed in a single request
   :param owner_id: |owner_id|
   :param owner_screen_name: |owner_screen_name|
   :rtype: :class:`List` object


.. method:: API.remove_list_member(slug, id)

   Removes the specified member from the list. The authenticated user
   must be the list's owner to remove members from the list.

   :param slug: |slug|
   :param id: the ID of the user to remove as a member
   :rtype: :class:`List` object


.. method:: API.remove_list_members(list_id/slug, screen_name/user_id, [owner_id/owner_screen_name])

   Remove up to 100 members from a list. The authenticated user must own the list to be
   able to remove members from it. Lists are limited to 5,000 members.

   :param list_id: |list_id|
   :param slug: |slug|
   :param screen_name: A comma separated list of screen names, up to 100 are allowed in a single request
   :param user_id: A comma separated list of user IDs, up to 100 are allowed in a single request
   :param owner_id: |owner_id|
   :param owner_screen_name: |owner_screen_name|
   :rtype: :class:`List` object


.. method:: API.list_members(list_id/slug, [owner_id/owner_screen_name], [cursor])

   Returns the members of the specified list.

   :param list_id: |list_id|
   :param slug: |slug|
   :param owner_id: |owner_id|
   :param owner_screen_name: |owner_screen_name|
   :param cursor: |cursor|
   :rtype: list of :class:`User` objects


.. method:: API.show_list_member(list_id/slug, screen_name/user_id, [owner_id/owner_screen_name])

   Check if the specified user is a member of the specified list.

   :param list_id: |list_id|
   :param slug: |slug|
   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :param owner_id: |owner_id|
   :param owner_screen_name: |owner_screen_name|
   :rtype: :class:`User` object if user is a member of list


.. method:: API.subscribe_list(owner, slug)

   Make the authenticated user follow the specified list.

   :param owner: |list_owner|
   :param slug: |slug|
   :rtype: :class:`List` object


.. method:: API.unsubscribe_list(owner, slug)

   Unsubscribes the authenticated user form the specified list.

   :param owner: |list_owner|
   :param slug: |slug|
   :rtype: :class:`List` object


.. method:: API.list_subscribers(owner, slug, [cursor])

   Returns the subscribers of the specified list.

   :param owner: |list_owner|
   :param slug: |slug|
   :param cursor: |cursor|
   :rtype: list of :class:`User` objects


.. method:: API.show_list_subscriber(list_id/slug, screen_name/user_id, [owner_id/owner_screen_name])

   Check if the specified user is a subscriber of the specified list.

   :param list_id: |list_id|
   :param slug: |slug|
   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :param owner_id: |owner_id|
   :param owner_screen_name: |owner_screen_name|
   :rtype: :class:`User` object if user is subscribed to list


Trends Methods
--------------------

.. method:: API.trends_available()

   Returns the locations that Twitter has trending topic information for. The response is an array of "locations" that encode the location's WOEID (a Yahoo! Where On Earth ID) and some other human-readable information such as a canonical name and country the location belongs in.

   :rtype: :class:`JSON` object


.. method:: API.trends_place(id, [exclude])

   Returns the top 50 trending topics for a specific WOEID, if trending information is available for it.

   The response is an array of “trend” objects that encode the name of the trending topic, the query parameter that can be used to search for the topic on Twitter Search, and the Twitter Search URL.

   This information is cached for 5 minutes. Requesting more frequently than that will not return any more data, and will count against your rate limit usage.

   The tweet_volume for the last 24 hours is also returned for many trends if this is available.

   :param id: The Yahoo! Where On Earth ID of the location to return trending information for. Global information is available by using 1 as the WOEID.
   :param exclude: Setting this equal to hashtags will remove all hashtags from the trends list.
   :rtype: :class:`JSON` object

.. method:: API.trends_closest(lat, long)

   Returns the locations that Twitter has trending topic information for, closest to a specified location.

   The response is an array of “locations” that encode the location’s WOEID and some other human-readable information such as a canonical name and country the location belongs in.

   A WOEID is a Yahoo! Where On Earth ID.

   :param lat: If provided with a long parameter the available trend locations will be sorted by distance, nearest to furthest, to the co-ordinate pair. The valid ranges for longitude is -180.0 to +180.0 (West is negative, East is positive) inclusive.
   :param long: If provided with a lat parameter the available trend locations will be sorted by distance, nearest to furthest, to the co-ordinate pair. The valid ranges for longitude is -180.0 to +180.0 (West is negative, East is positive) inclusive.
   :rtype: :class:`JSON` object


Geo Methods
-----------

.. method:: API.reverse_geocode([lat], [long], [accuracy], [granularity], [max_results])

   Given a latitude and longitude, looks for places (cities and
   neighbourhoods) whose IDs can be specified in a call to
   :func:`update_status` to appear as the name of the location. This
   call provides a detailed response about the location in question;
   the :func:`nearby_places` function should be preferred for getting
   a list of places nearby without great detail.

   :param lat: The location's latitude.
   :param long: The location's longitude.
   :param accuracy: Specify the "region" in which to search, such as a number (then this is a radius in meters, but it can also take a string that is suffixed with ft to specify feet).  If this is not passed in, then it is assumed to be 0m
   :param granularity: Assumed to be `neighborhood' by default; can also be `city'.
   :param max_results: A hint as to the maximum number of results to return. This is only a guideline, which may not be adhered to.

.. method:: API.reverse_geocode([lat], [long], [ip], [accuracy], [granularity], [max_results])

   Given a latitude and longitude, looks for nearby places (cities and
   neighbourhoods) whose IDs can be specified in a call to
   :func:`update_status` to appear as the name of the location. This
   call provides a detailed response about the location in question;
   the :func:`nearby_places` function should be preferred for getting
   a list of places nearby without great detail.

   :param lat: The location's latitude.
   :param long: The location's longitude.
   :param ip: The location's IP address. Twitter will attempt to geolocate using the IP address.
   :param accuracy: Specify the "region" in which to search, such as a number (then this is a radius in meters, but it can also take a string that is suffixed with ft to specify feet).  If this is not passed in, then it is assumed to be 0m
   :param granularity: Assumed to be `neighborhood' by default; can also be `city'.
   :param max_results: A hint as to the maximum number of results to return. This is only a guideline, which may not be adhered to.

.. method:: API.geo_id(id)

   Given *id* of a place, provide more details about that place.

   :param id: Valid Twitter ID of a location.


Utility methods
---------------

.. method:: API.configuration()

   Returns the current configuration used by Twitter including twitter.com slugs which are not usernames, maximum photo resolutions, and t.co shortened URL length.
   It is recommended applications request this endpoint when they are loaded, but no more than once a day.

Media methods
-------------

.. method:: API.media_upload()

   Uploads images to twitter and returns a `media_id`.

   :param media: The raw binary file content being uploaded. Cannot be used with `media_data`.
   :param media_data: The base64-encoded file content being uploaded. Cannot be used with `media`.
   :param additional_owners: A comma-separated list of user IDs to set as additional owners allowed to use the returned `media_id` in Tweets or Cards. Up to 100 additional owners may be specified.

:mod:`tweepy.error` --- Exceptions
==================================

The exceptions are available in the ``tweepy`` module directly,
which means ``tweepy.error`` itself does not need to be imported. For
example, ``tweepy.error.TweepError`` is available as ``tweepy.TweepError``.

.. exception:: TweepError

   The main exception Tweepy uses. Is raised for a number of things.

   When a ``TweepError`` is raised due to an error Twitter responded with,
   the error code (`as described in the API documentation
   <https://developer.twitter.com/en/docs/basics/response-codes>`_) can be accessed
   at ``TweepError.response.text``. Note, however, that ``TweepError``\ s
   also may be raised with other things as message (for example plain
   error reason strings).

.. exception:: RateLimitError

   Is raised when an API method fails due to hitting Twitter's rate
   limit. Makes for easy handling of the rate limit specifically.

   Inherits from :exc:`TweepError`, so ``except TweepError`` will
   catch a ``RateLimitError`` too.
