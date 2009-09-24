# Tweepy
# Copyright 2009 Joshua Roesslein
# See LICENSE

import os
import mimetypes

from . binder import bind_api
from . error import TweepError
from . auth import BasicAuthHandler, OAuthHandler
from . logging import DummyLogger
from tweepy.parsers import *


class API(object):
    """Twitter API"""

    def __init__(self, auth_handler=None, host='twitter.com', cache=None,
            secure=False, api_root='', validate=True, logger=DummyLogger()):
        # you may access these freely
        self.auth_handler = auth_handler
        self.host = host
        self.api_root = api_root
        self.cache = cache
        self.secure = secure
        self.validate = validate
        self.logger = logger

        # not a good idea to touch these
        self._username = None

    @staticmethod
    def new(auth='basic', *args, **kargs):
        if auth == 'basic':
            return API(BasicAuthHandler(*args, **kargs))
        elif auth == 'oauth':
            return API(OAuthHandler(*args, **kargs))
        else:
            raise TweepError('Invalid auth type')

    """ statuses/public_timeline

        Returns the 20 most recent statuses from non-protected users who
        have set a custom user icon. The public timeline is cached for 60 
        seconds so requesting it more often than that is a waste of resources.

        Parameters: None
        Returns: list[Status]

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-statuses-public_timeline
	"""
    public_timeline = bind_api(
        path = '/statuses/public_timeline.json',
        parser = parse_statuses,
        allowed_param = []
    )

    """ statuses/home_timeline [Coming soon]

        Returns the 20 most recent statuses, including retweets, posted
        by the authenticating user and that user's friends. This is the
        equivalent of /timeline/home on the Web.

        Parameters: since_id, max_id, count, page
        Returns: list[Status]

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-statuses-home_timeline
    """
    home_timeline = bind_api(
        path = '/statuses/home_timeline.json',
        parser = parse_statuses,
        allowed_param = ['since_id', 'max_id', 'count', 'page'],
        require_auth = True
    )

    """ statuses/friends_timeline

        Returns the 20 most recent statuses posted by the
        authenticating user and that user's friends.

        Parameters: since_id, max_id, count, page
        Returns: list[Status]

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-statuses-friends_timeline
    """
    friends_timeline = bind_api(
        path = '/statuses/friends_timeline.json',
        parser = parse_statuses,
        allowed_param = ['since_id', 'max_id', 'count', 'page'],
        require_auth = True
    )

    """ statuses/user_timeline

        Returns the 20 most recent statuses posted from the
        authenticating user. It's also possible to request another
        user's timeline via the id parameter.

        Parameters: (id or user_id or screen_name), since_id, max_id, count, page
        Returns: list[Status]

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-statuses-user_timeline
    """
    user_timeline = bind_api(
        path = '/statuses/user_timeline.json',
        parser = parse_statuses,
        allowed_param = ['id', 'user_id', 'screen_name', 'since_id',
                          'max_id', 'count', 'page']
    )

    """ statuses/mentions

        Returns the 20 most recent mentions (status containing @username)
        for the authenticating user.

        Parameters: since_id, max_id, count, page
        Returns: list[Status]

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-statuses-mentions
    """
    mentions = bind_api(
        path = '/statuses/mentions.json',
        parser = parse_statuses,
        allowed_param = ['since_id', 'max_id', 'count', 'page'],
        require_auth = True
    )

    """ statuses/retweeted_by_me [Coming soon]

        Returns the 20 most recent retweets posted by the authenticating user.

        Parameters: since_id, max_id, count, page
        Returns: list[Status]

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-statuses-retweeted_by_me
    """
    retweeted_by_me = bind_api(
        path = '/statuses/retweeted_by_me.json',
        parser = parse_statuses,
        allowed_param = ['since_id', 'max_id', 'count', 'page'],
        require_auth = True
    )

    """ statuses/retweeted_to_me

        Returns the 20 most recent retweets posted by the
        authenticating user's friends.

        Parameters: since_id, max_id, count, page
        Returns: list[Status]

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-statuses-retweeted_to_me
    """
    retweeted_to_me = bind_api(
        path = '/statuses/retweeted_to_me.json',
        parser = parse_statuses,
        allowed_param = ['since_id', 'max_id', 'count', 'page'],
        require_auth = True
    )

    """ statuses/retweets_of_me

        Returns the 20 most recent tweets of the authenticated
        user that have been retweeted by others.

        Parameters: since_id, max_id, count, page
        Returns: list[Status]

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-statuses-retweets_of_me
    """
    retweets_of_me = bind_api(
        path = '/statuses/retweets_of_me.json',
        parser = parse_statuses,
        allowed_param = ['since_id', 'max_id', 'count', 'page'],
        require_auth = True
    )

    """ statuses/show

        Returns a single status, specified by the id parameter below.
        The status's author will be returned inline.

        Parameters: id (Required)
        Returns: Status

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-statuses%C2%A0show
    """
    get_status = bind_api(
        path = '/statuses/show.json',
        parser = parse_status,
        allowed_param = ['id']
    )

    """ statuses/update [Geolocation parameters coming soon]

        Updates the authenticating user's status.
        A status update with text identical to the authenticating user's
        current status will be ignored to prevent duplicates.

        Parameters: status (Required), in_reply_to_status_id, lat, long
        Returns: Status

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-statuses%C2%A0update
    """
    update_status = bind_api(
        path = '/statuses/update.json',
        method = 'POST',
        parser = parse_status,
        allowed_param = ['status', 'in_reply_to_status_id', 'lat', 'long'],
        require_auth = True
    )

    """ statuses/destroy

        Destroys the status specified by the required ID parameter.
        The authenticating user must be the author of the specified status.

        Parameters: id (Required)
        Returns: Status
    """
    destroy_status = bind_api(
        path = '/statuses/destroy.json',
        method = 'DELETE',
        parser = parse_status,
        allowed_param = ['id'],
        require_auth = True
    )

    """ statuses/retweet [Coming soon]

        Retweets a tweet. Requires the id parameter of the tweet you are
        retweeting. Returns the original tweet with retweet details.

        Parameters: id (Required)
        Returns: Status

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-statuses-retweet
    """
    retweet = bind_api(
        path = '/statuses/retweet/id.json',
        method = 'POST',
        parser = parse_status,
        allowed_param = ['id'],
        require_auth = True
    )

    """ statuses/retweets [Coming soon]

        Returns up to 100 of the first retweets of a given tweet.

        Parameters: id (Required), count
        Returns: Retweet

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-statuses-retweets
    """
    def retweets(self, id, *args, **kargs):
        return bind_api(
            path = '/statuses/retweets/%s.json' % id,
            parser = parse_retweets,
            allowed_param = ['count'],
            require_auth = True
        )(self, *args, **kargs)

    """ users/show

        Returns extended information of a given user, specified by ID or
        screen name as per the required id parameter.

        Parameters: id or user_id or screen_name (One of these is required)
        Returns: User

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-users%C2%A0show
    """
    get_user = bind_api(
        path = '/users/show.json',
        parser = parse_user,
        allowed_param = ['id', 'user_id', 'screen_name']
    )

    """ Get the authenticated user

        Equivalent of calling API.get_user(authenticated_user_name)

        Parameters: None
        Returns: User

        See: API.get_user()
    """
    def me(self):
        # if username not fetched, go get it...
        if self._username is None:
            if self.auth_handler is None:
                raise TweepError('Authentication required')

            try:
                user = bind_api(
                    path = '/account/verify_credentials.json',
                    parser = parse_user
                )(self)
            except TweepError, e:
                raise TweepError('Failed to fetch username: %s' % e)

            self._username = user.screen_name

        return self.get_user(screen_name=self._username)

    """ statuses/friends

        Returns a user's friends. They are ordered by the order in
        which they were added as friends, 100 at a time.
        (Please note that the result set isn't guaranteed to be 100
        every time as suspended users will be filtered out.)
        Use the page option to access older friends. With no user specified,
        request defaults to the authenticated user's friends. It's also
        possible to request another user's friends list via the id,
        screen_name or user_id parameter.

        Parameters: (id or user_id or screen_name), page
        Returns: list[Users]

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-statuses%C2%A0friends
    """
    friends = bind_api(
        path = '/statuses/friends.json',
        parser = parse_users,
        allowed_param = ['id', 'user_id', 'screen_name', 'page']
    )

    """ statuses/followers

        Returns the authenticating user's followers.They are ordered by
        the order in which they joined Twitter, 100 at a time.
        (Please note that the result set isn't guaranteed to be 100 every
        time as suspended users will be filtered out.)
        Use the page option to access earlier followers.

        Parameters: (id or user_id or screen_name), page
        Returns: list[User]

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-statuses%C2%A0followers
    """
    followers = bind_api(
        path = '/statuses/followers.json',
        parser = parse_users,
        allowed_param = ['id', 'user_id', 'screen_name', 'page'],
        require_auth = True
    )

    """ direct_messages

        Returns a list of the 20 most recent direct messages sent
        to the authenticating user.

        Parameters: since_id, max_id, count, page
        Returns: list[DirectMessage]

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-direct_messages
    """
    direct_messages = bind_api(
        path = '/direct_messages.json',
        parser = parse_directmessages,
        allowed_param = ['since_id', 'max_id', 'count', 'page'],
        require_auth = True
    )

    """ direct_messages/sent

        Returns a list of the 20 most recent direct messages sent
        by the authenticating user.

        Parameters: since_id, max_id, count, page
        Returns: list[DirectMessage]

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-direct_messages%C2%A0sent
    """
    sent_direct_messages = bind_api(
        path = '/direct_messages/sent.json',
        parser = parse_directmessages,
        allowed_param = ['since_id', 'max_id', 'count', 'page'],
        require_auth = True
    )

    """ direct_messages/new

        Sends a new direct message to the specified user from
        the authenticating user.

        Parameters: user (Required), text (Required)
        Returns: DirectMessage

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-direct_messages%C2%A0new
    """
    send_direct_message = bind_api(
        path = '/direct_messages/new.json',
        method = 'POST',
        parser = parse_dm,
        allowed_param = ['user', 'text'],
        require_auth = True
    )

    """ direct_messages/destroy

        Destroys the direct message specified in the required ID parameter.
        The authenticating user must be the recipient of the
        specified direct message.

        Parameters: id (Required)
        Returns: DirectMessage

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-direct_messages%C2%A0destroy
    """
    destroy_direct_message = bind_api(
        path = '/direct_messages/destroy.json',
        method = 'DELETE',
        parser = parse_dm,
        allowed_param = ['id'],
        require_auth = True
    )

    """ friendships/create

        Allows the authenticating users to follow the user specified in
        the ID parameter.  Returns the befriended user when successful.

        Parameters:
            id or user_id or screen_name (One of these is required)
            follow
        Returns: User

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-friendships%C2%A0create
    """
    create_friendship = bind_api(
        path = '/friendships/create.json',
        method = 'POST',
        parser = parse_user,
        allowed_param = ['id', 'user_id', 'screen_name', 'follow'],
        require_auth = True
    )

    """ friendships/destroy

        Allows the authenticating users to unfollow the user specified
        in the ID parameter.  Returns the unfollowed user when successful.

        Parameters: id or user_id or screen_name (One of these is required)
        Returns: User

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-friendships%C2%A0destroy
    """
    destroy_friendship = bind_api(
        path = '/friendships/destroy.json',
        method = 'DELETE',
        parser = parse_user,
        allowed_param = ['id', 'user_id', 'screen_name'],
        require_auth = True
    )

    """ friendships/exists

        Tests for the existence of friendship between two users.

        Parameters: user_a (Required), user_b (Required)
        Returns: Boolean (True if user_a follows user_b, otherwise False)

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-friendships-exists
    """
    exists_friendship = bind_api(
        path = '/friendships/exists.json',
        parser = parse_json,
        allowed_param = ['user_a', 'user_b']
    )

    """ friendships/show

        Returns detailed information about the relationship between two users.

        Parameters:
            source_id or source_screen_name (One of these is required)
            target_id or target_screen_name (One of these is required)
        Returns: tuple(Friendship - source, Friendship - target)

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-friendships-show
    """
    show_friendship = bind_api(
        path = '/friendships/show.json',
        parser = parse_friendship,
        allowed_param = ['source_id', 'source_screen_name',
                          'target_id', 'target_screen_name']
    )

    """ friends/ids

        Returns an array of numeric IDs for every user the
        specified user is following.

        Parameters:
            id or user_id or screen_name (One of these is required)
            cursor
        Returns: json object

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-friends%C2%A0ids
    """
    friends_ids = bind_api(
        path = '/friends/ids.json',
        parser = parse_json,
        allowed_param = ['id', 'user_id', 'screen_name', 'cursor']
    )

    """ followers/ids

        Returns an array of numeric IDs for every user following
        the specified user.

        Parameters:
            id or user_id or screen_name (One of these is required)
            cursor
        Returns: json object

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-followers%C2%A0ids
    """
    followers_ids = bind_api(
        path = '/followers/ids.json',
        parser = parse_json,
        allowed_param = ['id', 'user_id', 'screen_name', 'cursor']
    )

    """ account/verify_credentials

        Use this method to test if supplied user credentials are valid.
        Because this method can be a vector for a brute force dictionary
        attack to determine a user's password, it is limited to 15 requests
        per 60 minute period (starting from your first request).

        Parameters: None
        Returns: True if credentials are valid, otherwise False

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-account%C2%A0verify_credentials
    """
    def verify_credentials(self):
        try:
            return bind_api(
                path = '/account/verify_credentials.json',
                parser = parse_return_true,
                require_auth = True
            )(self)
        except TweepError:
            return False

    """ account/rate_limit_status

        Returns the remaining number of API requests available to the
        requesting user before the API limit is reached for the current hour.
        Calls to rate_limit_status do not count against the rate limit.
        If authentication credentials are provided, the rate limit status for
        the authenticating user is returned.  Otherwise, the rate limit status
        for the requester's IP address is returned.

        Parameters: None
        Returns: json object

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-account%C2%A0rate_limit_status
    """
    rate_limit_status = bind_api(
        path = '/account/rate_limit_status.json',
        parser = parse_json
    )

    """ account/update_delivery_device

        Sets which device Twitter delivers updates to for the authenticating
        user.  Sending "none" as the device parameter will disable IM or SMS
        updates.

        Parameters: device (Required)
        Returns: User

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-account%C2%A0update_delivery_device
    """
    set_delivery_device = bind_api(
        path = '/account/update_delivery_device.json',
        method = 'POST',
        allowed_param = ['device'],
        parser = parse_user,
        require_auth = True
    )

    """ account/update_profile_colors

        Sets one or more hex values that control the color scheme of the
        authenticating user's profile page on twitter.com.

        Parameters: profile_background_color, profile_text_color,
            profile_link_color, profile_sidebar_fill_color,
            profile_sidebar_border_color
        Returns: User

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-account%C2%A0update_profile_colors
    """
    update_profile_colors = bind_api(
        path = '/account/update_profile_colors.json',
        method = 'POST',
        parser = parse_user,
        allowed_param = ['profile_background_color', 'profile_text_color',
                          'profile_link_color', 'profile_sidebar_fill_color',
                          'profile_sidebar_border_color'],
        require_auth = True
    )

    """ account/update_profile_image

        Updates the authenticating user's profile image.

        Parameters:
            filename - local file path to image (Required)
        Returns: User

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-account%C2%A0update_profile_image
    """
    def update_profile_image(self, filename):
        headers, post_data = _pack_image(filename, 700)
        bind_api(
            path = '/account/update_profile_image.json',
            method = 'POST',
            parser = parse_none,
            require_auth = True
        )(self, post_data=post_data, headers=headers)

    """ account/update_profile_background_image

        Updates the authenticating user's profile background image.

        Parameters:
            filename - local file path to image (Required)
            tile
        Returns: User

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-account%C2%A0update_profile_background_image
    """
    def update_profile_background_image(self, filename, *args, **kargs):
        headers, post_data = _pack_image(filename, 800)
        bind_api(
            path = '/account/update_profile_background_image.json',
            method = 'POST',
            parser = parse_none,
            allowed_param = ['tile'],
            require_auth = True
        )(self, post_data=post_data, headers=headers)

    """ account/update_profile

        Sets values that users are able to set under the "Account" tab of
        their settings page. Only the parameters specified will be updated.

        Parameters: name, email, url, location, description
        Returns: User

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-account%C2%A0update_profile
    """
    update_profile = bind_api(
        path = '/account/update_profile.json',
        method = 'POST',
        parser = parse_user,
        allowed_param = ['name', 'email', 'url', 'location', 'description'],
        require_auth = True
    )

    """ favorites

        Returns the 20 most recent favorite statuses for the authenticating
        user or user specified by the ID parameter.

        Parameters: id, page
        Returns: list[Status]

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-favorites
    """
    favorites = bind_api(
        path = '/favorites.json',
        parser = parse_statuses,
        allowed_param = ['id', 'page']
    )

    """ favorites/create

        Favorites the status specified in the ID parameter as the
        authenticating user. Returns the favorite status when successful.

        Parameters: id (Required)
        Returns: Status

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-favorites%C2%A0create
    """
    create_favorite = bind_api(
        path = '/favorites/create.json',
        method = 'POST',
        parser = parse_status,
        allowed_param = ['id'],
        require_auth = True
    )

    """ favorites/destroy

        Un-favorites the status specified in the ID parameter as the
        authenticating user. Returns the un-favorited status.

        Parameters: id (Required)
        Returns: Status

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-favorites%C2%A0destroy
    """
    destroy_favorite = bind_api(
        path = '/favorites/destroy.json',
        method = 'DELETE',
        parser = parse_status,
        allowed_param = ['id'],
        require_auth = True
    )

    """ notifications/follow

        Enables device notifications for updates from the specified user.
        Returns the specified user when successful.

        Parameters: id or user_id or screen_name (One of these is required)
        Returns: User

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-notifications%C2%A0follow
    """
    enable_notifications = bind_api(
        path = '/notifications/follow.json',
        method = 'POST',
        parser = parse_user,
        allowed_param = ['id', 'user_id', 'screen_name'],
        require_auth = True
    )

    """ notifications/leave

        Disables notifications for updates from the specified user to the
        authenticating user.  Returns the specified user when successful.

        Parameters: id or user_id or screen_name (One of these is required)
        Returns: User

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-notifications%C2%A0leave
    """
    disable_notifications = bind_api(
        path = '/notifications/leave.json',
        method = 'POST',
        parser = parse_user,
        allowed_param = ['id', 'user_id', 'screen_name'],
        require_auth = True
    )

    """ blocks/create

        Blocks the user specified in the ID parameter as the authenticating
        user. Destroys a friendship to the blocked user if it exists.
        Returns the blocked user when successful.

        Parameters: id (Required)
        Returns: User

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-blocks%C2%A0create
    """
    create_block = bind_api(
        path = '/blocks/create.json',
        method = 'POST',
        parser = parse_user,
        allowed_param = ['id'],
        require_auth = True
    )

    """ blocks/destroy

        Un-blocks the user specified in the ID parameter for the
        authenticating user. Returns the un-blocked user when successful.

        Parameters: id (Required)
        Returns: User

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-blocks%C2%A0destroy
    """
    destroy_block = bind_api(
        path = '/blocks/destroy.json',
        method = 'DELETE',
        parser = parse_user,
        allowed_param = ['id'],
        require_auth = True
    )

    """ blocks/exists

        Checks if the authenticating user is blocking a target user.

        Parameters: id or user_id or screen_name (One of these is required)
        Returns: Boolean (True if blocked, otherwise False)

        http://apiwiki.twitter.com/Twitter+REST+API+Method%3A-blocks-exists
    """
    def exists_block(self, **kargs):
        try:
            bind_api(
                path = '/blocks/exists.json',
                parser = parse_none,
                allowed_param = ['id', 'user_id', 'screen_name'],
                require_auth = True
            )(self, **kargs)
        except TweepError:
            return False

        return True

    """ blocks/blocking

        Returns an array of user objects that the authenticating
        user is blocking.

        Parameters: page
        Returns: list[User]

        http://apiwiki.twitter.com/Twitter+REST+API+Method%3A-blocks-blocking
    """
    blocks = bind_api(
        path = '/blocks/blocking.json',
        parser = parse_users,
        allowed_param = ['page'],
        require_auth = True
    )

    """ blocks/blocking/ids

        Returns an array of numeric user ids the authenticating
        user is blocking.

        Parameters: None
        Returns: json object

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-blocks-blocking-ids
    """
    blocks_ids = bind_api(
        path = '/blocks/blocking/ids.json',
        parser = parse_json,
        require_auth = True
    )

    """ saved_searches

        Returns the authenticated user's saved search queries.

        Parameters: None
        Returns: list[SavedSearch]

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-saved_searches
    """
    saved_searches = bind_api(
        path = '/saved_searches.json',
        parser = parse_saved_searches,
        require_auth = True
    )

    """ saved_searches/show

        Retrieve the data for a saved search owned by the
        authenticating user specified by the given id.

        Parameters: id (Required)
        Returns: SavedSearch

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-saved_searches-show
    """
    def get_saved_search(self, id):
        return bind_api(
            path = '/saved_searches/show/%s.json' % id,
            parser = parse_saved_search,
            require_auth = True
        )(self)

    """ saved_searches/create

        Creates a saved search for the authenticated user.

        Parameters: query (Required)
        Returns: SavedSearch

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-saved_searches-create
    """
    create_saved_search = bind_api(
        path = '/saved_searches/create.json',
        method = 'POST',
        parser = parse_saved_search,
        allowed_param = ['query'],
        require_auth = True
    )

    """ saved_searches/destroy

        Destroys a saved search for the authenticated user.
        The search specified by id must be owned by the authenticating user.

        Parameters: id (Required)
        Returns: SavedSearch

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-saved_searches-destroy
    """
    def destroy_saved_search(self, id):
        return bind_api(
            path = '/saved_searches/destroy/%s.json' % id,
            method = 'DELETE',
            parser = parse_saved_search,
            allowed_param = ['id'],
            require_auth = True
        )(self)

    """ help/test

        Invokes the test method in the Twitter API.

        Parameters: None
        Returns: Boolean (True if 200 status code returned, otherwise False)

        http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-help%C2%A0test
    """
    def test(self):
        try:
            return bind_api(
                path = '/help/test.json',
                parser = parse_return_true
            )(self)
        except TweepError:
            return False

    """ search

        Returns tweets that match a specified query.

        Parameters: q (Required), lang, locale, rpp, page, since_id
            geocode, show_user
        Returns: list[SearchResult]

        http://apiwiki.twitter.com/Twitter-Search-API-Method%3A-search
    """

    def search(self, *args, **kargs):
        return bind_api(
            host = 'search.' + self.host,
            path = '/search.json',
            parser = parse_search_results,
            allowed_param = ['q', 'lang', 'locale', 'rpp', 'page', 'since_id', 'geocode', 'show_user'],
        )(self, *args, **kargs)

    """ trends

        Returns the top ten topics that are currently trending on Twitter.
        The response includes the time of the request, the name of each trend,
        and the url to the Twitter Search results page for that topic.

        Parameters: None
        Returns: json object

        http://apiwiki.twitter.com/Twitter-Search-API-Method%3A-trends
    """
    def trends(self):
        return bind_api(
            host = 'search.' + self.host,
            path = '/trends.json',
            parser = parse_json
        )(self)

    """ trends/current

        Returns the current top 10 trending topics on Twitter.
        The response includes the time of the request, the name of each
        trending topic, and query used on Twitter Search results
        page for that topic.

        Parameters: exclude
        Returns: json object

        http://apiwiki.twitter.com/Twitter-Search-API-Method%3A-trends-current
    """
    def trends_current(self, *args, **kargs):
        return bind_api(
            host = 'search.' + self.host,
            path = '/trends/current.json',
            parser = parse_json,
            allowed_param = ['exclude']
        )(self, *args, **kargs)

    """ trends/daily

        Returns the top 20 trending topics for each hour in a given day.

        Parameters: date, exclude
        Returns: json object

        http://apiwiki.twitter.com/Twitter-Search-API-Method%3A-trends-daily
    """
    def trends_daily(self, *args, **kargs):
        return bind_api(
            host = "search." + self.host,
            path = '/trends/daily.json',
            parser = parse_json,
            allowed_param = ['date', 'exclude']
        )(self, *args, **kargs)

    """ trends/weekly

        Returns the top 30 trending topics for each day in a given week.

        Parameters: date, exclude
        Returns: json object

        http://apiwiki.twitter.com/Twitter-Search-API-Method%3A-trends-weekly
    """
    def trends_weekly(self, *args, **kargs):
        return bind_api(
            host = "search." + self.host,
            path = '/trends/weekly.json',
            parser = parse_json,
            allowed_param = ['date', 'exclude']
        )(self, *args, **kargs)

    """ Internal use only """

    def _pack_image(filename, max_size):
        """Pack image from file into multipart-formdata post body"""
        # image must be less than 700kb in size
        try:
            if os.path.getsize(filename) > (max_size * 1024):
                raise TweepError('File is too big, must be less than 700kb.')
        except os.error, e:
            raise TweepError('Unable to access file')

        # image must be gif, jpeg, or png
        file_type = mimetypes.guess_type(filename)
        if file_type is None:
            raise TweepError('Could not determine file type')
        file_type = file_type[0]
        if file_type not in ['image/gif', 'image/jpeg', 'image/png']:
            raise TweepError('Invalid file type for image: %s' % file_type)

        # build the mulitpart-formdata body
        fp = open(filename, 'rb')
        BOUNDARY = 'Tw3ePy'
        body = []
        body.append('--' + BOUNDARY)
        body.append('Content-Disposition: form-data; name="image"; filename="%s"' % filename)
        body.append('Content-Type: %s' % file_type)
        body.append('')
        body.append(fp.read())
        body.append('--' + BOUNDARY + '--')
        body.append('')
        fp.close()
        body = '\r\n'.join(body)

        # build headers
        headers = {
            'Content-Type': 'multipart/form-data; boundary=Tw3ePy',
            'Content-Length': len(body)
        }

        return headers, body

