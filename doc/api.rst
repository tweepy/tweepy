.. _api_reference:

API Reference
=============

This page contains some basic documentation for the Tweepy module.


:mod:`tweepy.api` --- Twitter API wrapper
=========================================

.. class:: API([auth_handler], [host], [search_host], [cache], [secure], [api_root], [search_root], [retry_count], [retry_delay], [retry_errors])

   This class provides a wrapper for the API as provided by
   Twitter. The functions provided in this class are listed below.


Timeline methods
----------------

.. method:: API.public_timeline()

   Returns the 20 most recent statuses from non-protected users who have
   set a custom user icon. The public timeline is cached for 60 seconds
   so requesting it more often than that is a waste of resources.

   Parameters: None

   Returns: list of :class:`Status` objects


.. method:: API.home_timeline([since_id], [max_id], [count], [page])

   Returns the 20 most recent statuses, including retweets, posted by the
   authenticating user and that user's friends. This is the equivalent of
   /timeline/home on the Web.

   Parameters: *since_id*, *max_id*, *count*, *page*

   Returns: list of :class:`Status` objects


.. method:: API.friends_timeline([since_id], [max_id], [count], [page])

   Returns the 20 most recent statuses posted by the authenticating user
   and that user's friends.

   Parameters: *since_id*, *max_id*, *count*, *page*

   Returns: list of :class:`Status` objects


.. method:: API.user_timeline([id/user_id/screen_name], [since_id], [max_id], [count], [page])

   Returns the 20 most recent statuses posted from the authenticating
   user. It's also possible to request another user's timeline via the id
   parameter.

   Parameters: *id* or *user_id* or *screen_name*, *since_id*, *max_id*, *count*, *page*

   Returns: list of :class:`Status` objects


.. method:: API.mentions([since_id], [max_id], [count], [page])

   Returns the 20 most recent mentions (status containing @username) for
   the authenticating user.

   Parameters: *since_id*, *max_id*, *count*, *page*

   Returns: list of :class:`Status` objects


.. method:: API.retweeted_by_me([since_id], [max_id], [count], [page])

   Returns the 20 most recent retweets posted by the authenticating user.

   Parameters: *since_id*, *max_id*, *count*, *page*

   Returns: list of :class:`Status` objects


.. method:: API.retweeted_to_me([since_id], [max_id], [count], [page])

   Returns the 20 most recent retweets posted by the authenticating
   user's friends.

   Parameters: *since_id*, *max_id*, *count*, *page*

   Returns: list of :class:`Status` objects


.. method:: API.retweets_of_me

   Returns the 20 most recent tweets of the authenticated user that have
   been retweeted by others.

   Parameters: *since_id*, *max_id*, *count*, *page*

   Returns: list of :class:`Status` objects


Status methods
--------------

.. method:: API.get_status(id)

Returns a single status specified by the ID parameter.

Parameters: *id* (Required)

Returns: :class:`Status` object


.. method:: API.update_status(status, [in_reply_to_status_id], [lat], [long])

   Update the authenticated user's status. Statuses that are duplicates
   or too long will be silently ignored.

   Parameters: *status* (Required), *in_reply_to_status_id*, *lat*, *long*

   Returns: :class:`Status` object


.. method:: API.destroy_status(id)

   Destroy the status specified by the id parameter. The authenticated
   user must be the author of the status to destroy.

   Parameters: *id* (Required)

   Returns: :class:`Status` object


.. method:: API.retweet(id)

   Retweets a tweet. Requires the id of the tweet you are retweeting.

   Parameters: *id* (Required)

   Returns: :class:`Status` object


.. method:: API.retweets(id)

   Returns up to 100 of the first retweets of the given tweet.

   Parameters: *id* (Required), count

   Returns: list of :class:`Status` objects


User methods
------------

.. method:: API.get_user(id)

   Returns information about the specified user.

   Parameters: *id* OR screen_name OR id (One of these is Required)

   Returns: :class:`User` object


.. method:: API.me()

   Returns the authenticated user's information.

   Parameters: None

   Returns: User object

.. method::API.friends([id/screen_name/user_id], [cursor])

   Returns an user's friends ordered in which they were added 100 at a time. If no user is specified by id/screen name, it defaults to the authenticated user.

   Parameters: *id* OR *screen_name* OR *user_id*, *cursor*

   Returns: list of :class:`User` objects


.. method:: API.followers([id/screen_name/user_id], [cursor])

   Returns an user's followers ordered in which they were added 100 at a
   time. If no user is specified by id/screen name, it defaults to the
   authenticated user.

   Parameters: *id* OR *screen_name* OR *user_id*, *cursor*

   Returns: list of User objects


.. method:: API.search_users(q, [per_page], [page])

   Run a search for users similar to Find People button on Twitter.com;
   the same results returned by people search on Twitter.com will be
   returned by using this API (about being listed in the People
   Search). It is only possible to retrieve the first 1000 matches from
   this API.

   Parameters: *q* (Required. The query.), *per_page*, *page*

   Returns: list of :class:`User` objects


Direct Message Methods
----------------------

.. method:: API.direct_messages([since_id], [max_id], [count], [page])

   Returns direct messages sent to the authenticating user.

   Parameters: *since_id*, *max_id*, *count*, *page*

   Returns: list of DirectMessage objects


.. method:: API.sent_direct_messages([since_id], [max_id], [count], [page])

   Returns direct messages sent by the authenticating user.

   Parameters: *since_id*, *max_id*, *count*, *page*

   Returns: list of DirectMessage objects


.. method:: API.send_direct_message(user, text)

   Sends a new direct message to the specified user from the
   authenticating user.

   Parameters: *user* (Required), *text* (Required)

   Returns: :class:`DirectMessage` object


.. method:: API.destroy_direct_message(id)

   Destroy a direct message. Authenticating user must be the recipient of
   the direct message.

   Parameters: *id* (Required)

   Returns: :class:`DirectMessage` object


Friendship Methods
------------------

.. method:: API.create_friendship(id/screen_name/user_id)

   Create a new friendship with the specified user (aka follow).

   Parameters: *id* OR *screen_name* OR *user_id* (One of these is required)

   Returns: User object


.. method:: API.destroy_friendship(id/screen_name/user_id)

   Destroy a friendship with the specified user (aka unfollow).

   Parameters: *id* OR *screen_name* OR *user_id* (One of these is required)

   Returns: User object


.. method:: API.exists_friendship(user_a, user_b)

   Checks if a friendship exists between two users. Will return True if
   user_a follows user_b, otherwise False.

   Parameters: *user_a* (Required), *user_b* (Required)

   Returns: True/False


.. method:: API.show_friendship(id/screen_name/user_id, target_id/target_screen_name)

   Returns detailed information about the relationship between two users.

   Parameters: *id* OR *screen_name* OR *user_id* (One of these is
   required), *target_id* OR *target_screen_name* (One of these is
   required)

   Returns: Friendship object


.. method:: API.friends_ids(id/screen_name/user_id)

   Returns an array containing the IDs of users being followed by the
   specified user.

   Parameters: *id* OR *screen_name* OR *user_id* (One of these is required)

   Returns: list of Integers


.. method:: API.followers_ids(id/screen_name/user_id)

   Returns an array containing the IDs of users following the specified
   user.

   Parameters: *id* OR screen_name OR user_id (One of these is required)

   Returns: list of Integers


Account Methods
---------------

.. method:: API.verify_credentials()

   Verify the supplied user credentials are valid.

   Parameters: None

   Returns: :class:`User` object if credentials are valid, otherwise False


.. method:: API.rate_limit_status()

   Returns the remaining number of API requests available to the
   requesting user before the API limit is reached for the current
   hour. Calls to rate_limit_status do not count against the rate
   limit. If authentication credentials are provided, the rate limit
   status for the authenticating user is returned. Otherwise, the rate
   limit status for the requester's IP address is returned.

   Parameters: None

   Returns: :class:`JSON` object


.. method:: API.set_delivery_device(device)

   Sets which device Twitter delivers updates to for the authenticating
   user. Sending "none" as the device parameter will disable SMS updates.

   Parameters: *device* (Required. Valid values: sms OR none)

   Returns: :class:`User` object


.. method:: API.update_profile_colors([profile_background_color], [profile_text_color], [profile_link_color], [profile_sidebar_fill_color], [profile_sidebar_border_color])

   Sets one or more hex values that control the color scheme of the
   authenticating user's profile page on twitter.com.

   Parameters: *profile_background_color*, *profile_text_color*, *profile_link_color*, *profile_sidebar_fill_color*, *profile_sidebar_border_color*

   Returns: :class:`User` object


.. method:: API.update_profile_image(filename)

   Update the authenticating user's profile image. Valid formats: GIF,
   JPG, or PNG

   Parameters: filename (Path to image file. Required)

   Returns: :class:`User` object


.. method:: API.update_profile_background_image(filename)

   Update authenticating user's background image. Valid formats: GIF,
   JPG, or PNG

   Parameters: filename (Path to image file. Required), tile

   Returns: :class:`User` object


.. method:: API.update_profile([name], [url], [location], [description])

   Sets values that users are able to set under the "Account" tab of
   their settings page.

   Parameters: *name*, *url*, *location*, *description*

   Returns: :class:`User` object


Favorite Methods
----------------

.. method:: API.favorites([id], [page])

   Returns the favorite statuses for the authenticating user or user
   specified by the ID parameter.

   Parameters: *id*, *page*

   Returns: list of :class:`Status` objects


.. method:: API.create_favorite(id)

   Favorites the status specified in the ID parameter as the
   authenticating user.

   Parameters: *id* (Required)

   Returns: :class:`Status` object


.. method:: API.destroy_favorite(id)

   Un-favorites the status specified in the ID parameter as the
   authenticating user.

   Parameters: *id* (Required)

   Returns: :class:`Status` object


Notification Methods
--------------------

.. method:: API.enable_notifications(id/screen_name/user_id)

   Enables device notifications for updates from the specified user.

   Parameters: *id* OR *screen_name* OR *user_id* (One of these is required)

   Returns: :class:`User` object


.. method:: API.disable_notifications(id/screen_name/user_id)

   Disables notifications for updates from the specified user to the
   authenticating user.

   Parameters: *id* OR *screen_name* OR *user_id* (One of these is required)

   Returns: :class:`User` object


Block Methods
-------------

.. method:: API.create_block(id/screen_name/user_id)

   Blocks the user specified in the ID parameter as the authenticating
   user. Destroys a friendship to the blocked user if it exists.

   Parameters: *id* OR *screen_name* OR *user_id* (One of these is required)

   Returns: :class:`User` object


.. method:: API.destroy_block(id/screen_name/user_id)

   Un-blocks the user specified in the ID parameter for the
   authenticating user.

   Parameters: *id* OR *screen_name* OR *user_id* (One of these is required)

   Returns: :class:`User` object


.. method:: API.exists_block(id/screen_name/user_id)

   Checks if the authenticated user is blocking the specified user.

   Parameters: *id* OR *screen_name* OR *user_id* (One of these is required)

   Returns: True/False


.. method:: API.blocks([page])

   Returns an array of user objects that the authenticating user is
   blocking.

   Parameters: page

   Returns: list of :class:`User` objects


.. method:: API.blocks_ids

   Returns an array of numeric user ids the authenticating user is
   blocking.

   Parameters: None

   Returns: list of Integers


Spam Reporting Methods
----------------------

.. method:: API.report_spam([id/user_id/screen_name])

   The user specified in the id is blocked by the authenticated user and
   reported as a spammer.

   Parameters: *id* OR *screen_name* OR *user_id* (One of these is required)

   Returns: :class:`User` object


Saved Searches Methods
----------------------

.. method:: API.saved_searches

   Returns the authenticated user's saved search queries.

   Parameters: None

   Returns: list of :class:`SavedSearch` objects


.. method:: API.get_saved_search(id)

   Retrieve the data for a saved search owned by the authenticating user
   specified by the given id.

   Parameters: *id* (Required)

   Returns: :class:`SavedSearch` object


.. method:: API.create_saved_search(query)

   Creates a saved search for the authenticated user.

   Parameters: *query* (Required)

   Returns: :class:`SavedSearch` object


.. method:: API.destroy_saved_search(id)

   Destroys a saved search for the authenticated user. The search
   specified by id must be owned by the authenticating user.

   Parameters: *id* (Required)

   Returns: :class:`SavedSearch` object


Help Methods
------------

.. method:: API.test()

   Invokes the test method in the Twitter API. Return True if successful,
   otherwise False.

   Parameters: None

   Returns: True/False


.. method:: API.search()

   Returns tweets that match a specified query.

   Parameters: q (Required. The search query string.), lang, locale, rpp, page, since_id, geocode, show_user

   Returns: list of :class:`SearchResult` objects


.. method:: API.trends()

   Returns the top ten topics that are currently trending on Twitter. The
   response includes the time of the request, the name of each trend, and
   the url to the Twitter Search results page for that topic.

   Parameters: None

   Returns: :class:`JSON` object


.. method:: API.trends_current([exclude])

   Returns the current top 10 trending topics on Twitter. The response
   includes the time of the request, the name of each trending topic, and
   query used on Twitter Search results page for that topic.

   Parameters: *exclude*

   Returns: :class:`JSON` object


.. method:: API.trends_daily([date], [exclude])

   Returns the top 20 trending topics for each hour in a given day.

   Parameters: *date*, *exclude*

   Returns: :class:`JSON` object


.. method:: API.trends_weekly([date], [exclude])

   Returns the top 30 trending topics for each day in a given week.

   Parameters: *date*, *exclude*

   Returns: :class:`JSON` object


List Methods
------------

.. method:: API.create_list(name, [mode])

   Creates a new list for the authenticated user. Accounts are limited to
   20 lists.

   Parameters: *name* (Required), *mode* (public/private default: public)

   Returns: :class:`List` object


.. method:: API.destroy_list(slug)

   Deletes the specified list. Must be owned by the authenticated user.

   Parameters: *slug* (Required. May also be the list ID.)

   Returns: :class:`List` object


.. method:: API.update_list(slug, [name], [mode])

   Updates the specified list. Note: this current throws a 500. Twitter
   is looking into the issue.

   Parameters: *slug* (Required. May also be the list ID.), *name*, *mode* (public/private)

   Returns: :class:`List` object


.. method:: API.lists([cursor])

   List the lists of the specified user. Private lists will be included
   if the authenticated users is the same as the user who's lists are
   being returned.

   Parameters: *cursor*

   Returns: list of :class:`List` objects


.. method:: API.lists_memberships([cursor])

   List the lists the specified user has been added to.

   Parameters: *cursor*

   Returns: list of :class:`List` objects


.. method:: API.lists_subscriptions([cursor])

   List the lists the specified user follows.

   Parameters: *cursor*

   Returns: list of :class:`List` objects


.. method:: API.list_timeline(owner, slug, [since_id], [max_id], [count], [page])

   Show tweet timeline for members of the specified list.

   Parameters: *owner* (Required.), *slug* (Required. May also be the list ID.), *since_id*, *max_id*, *count*, *page*

   Returns: list of :class:`Status` objects


.. method:: API.get_list(owner, slug)

   Show the specified list. Private lists will only be shown if the
   authenticated user owns the specified list.

   Parameters: *owner* (Required.), *slug* (Required. May also be the list ID.)

   Returns: :class:`List` object


.. method:: API.add_list_member*slug, id)

   Add a member to a list. The authenticated user must own the list to be
   able to add members to it. Lists are limited to having 500 members.

   Parameters: *slug* (Required. May also be the list ID.), *id* (Required. ID of user to add.)

   Returns: :class:`List` object


.. method:: API.remove_list_member(slug, id)

   Removes the specified member from the list. The authenticated user
   must be the list's owner to remove members from the list.

   Parameters: *slug* (Required. May also be the list ID.), *id* (Required. ID of user to remove.)

   Returns: :class:`List` object


.. method:: API.list_members(owner, slug, cursor)

   Returns the members of the specified list.

   Parameters: *owner* (Required.), *slug* (Required. May also be list ID.), *cursor*

   Returns: list of :class:`User` objects


.. method:: API.is_list_member(owner, slug, id)

   Check if a user is a member of the specified list.

   Parameters: *owner* (Required.), *slug* (Required. May also be list ID.), *id* (Required. :class:`User` to check if subscribed to the list.)

   Returns: :class:`User` object if user is a member of list, otherwise False.


.. method:: API.subscribe_list(owner, slug)

   Make the authenticated user follow the specified list.

   Parameters: *owner* (Required.), *slug* (Required. May also be list ID.)

   Returns: :class:`List` object


.. method:: API.unsubscribe_list(owner, slug)

   Unsubscribes the authenticated user form the specified list.

   Parameters: *owner* (Required.), *slug* (Required. May also be list ID.)

   Returns: :class:`List` object


.. method:: API.list_subscribers(owner, slug, [cursor])

   Returns the subscribers of the specified list.

   Parameters: *owner* (Required.), *slug* (Required. May also be list ID.), *cursor*

   Returns: list of :class:`User` objects


.. method:: API.is_subscribed_list(owner, slug, id)

   Check if the specified user is a subscriber of the specified list.

   Parameters: *owner* (Required.), *slug* (Required. May also be list ID.), *id* (Required. :class:`User` to check if subscribed to the list.)

   Returns: :class:`User` object if user is subscribed to the list, otherwise False.

