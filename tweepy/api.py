# Tweepy
# Copyright 2009 Joshua Roesslein
# See LICENSE

import os
import mimetypes

from tweepy.binder import bind_api
from tweepy.error import TweepError
from tweepy.parsers import *


class API(object):
    """Twitter API"""

    def __init__(self, auth_handler=None,
            host='api.twitter.com', search_host='search.twitter.com',
             cache=None, secure=False, api_root='/1', search_root='',
            retry_count=0, retry_delay=0, retry_errors=None):
        # you may access these freely
        self.auth = auth_handler
        self.host = host
        self.search_host = search_host
        self.api_root = api_root
        self.search_root = search_root
        self.cache = cache
        self.secure = secure
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.retry_errors = retry_errors

    """ statuses/public_timeline """
    public_timeline = bind_api(
        path = '/statuses/public_timeline.json',
        parser = parse_statuses,
        allowed_param = []
    )

    """ statuses/home_timeline [Coming soon] """
    home_timeline = bind_api(
        path = '/statuses/home_timeline.json',
        parser = parse_statuses,
        allowed_param = ['since_id', 'max_id', 'count', 'page'],
        require_auth = True
    )

    """ statuses/friends_timeline """
    friends_timeline = bind_api(
        path = '/statuses/friends_timeline.json',
        parser = parse_statuses,
        allowed_param = ['since_id', 'max_id', 'count', 'page'],
        require_auth = True
    )

    """ statuses/user_timeline """
    user_timeline = bind_api(
        path = '/statuses/user_timeline.json',
        parser = parse_statuses,
        allowed_param = ['id', 'user_id', 'screen_name', 'since_id',
                          'max_id', 'count', 'page']
    )

    """ statuses/mentions """
    mentions = bind_api(
        path = '/statuses/mentions.json',
        parser = parse_statuses,
        allowed_param = ['since_id', 'max_id', 'count', 'page'],
        require_auth = True
    )

    """ statuses/retweeted_by_me [Coming soon] """
    retweeted_by_me = bind_api(
        path = '/statuses/retweeted_by_me.json',
        parser = parse_statuses,
        allowed_param = ['since_id', 'max_id', 'count', 'page'],
        require_auth = True
    )

    """ statuses/retweeted_to_me """
    retweeted_to_me = bind_api(
        path = '/statuses/retweeted_to_me.json',
        parser = parse_statuses,
        allowed_param = ['since_id', 'max_id', 'count', 'page'],
        require_auth = True
    )

    """ statuses/retweets_of_me """
    retweets_of_me = bind_api(
        path = '/statuses/retweets_of_me.json',
        parser = parse_statuses,
        allowed_param = ['since_id', 'max_id', 'count', 'page'],
        require_auth = True
    )

    """ statuses/show """
    get_status = bind_api(
        path = '/statuses/show.json',
        parser = parse_status,
        allowed_param = ['id']
    )

    """ statuses/update [Geolocation parameters coming soon] """
    update_status = bind_api(
        path = '/statuses/update.json',
        method = 'POST',
        parser = parse_status,
        allowed_param = ['status', 'in_reply_to_status_id', 'lat', 'long'],
        require_auth = True
    )

    """ statuses/destroy """
    destroy_status = bind_api(
        path = '/statuses/destroy.json',
        method = 'DELETE',
        parser = parse_status,
        allowed_param = ['id'],
        require_auth = True
    )

    """ statuses/retweet [Coming soon] """
    retweet = bind_api(
        path = '/statuses/retweet/id.json',
        method = 'POST',
        parser = parse_status,
        allowed_param = ['id'],
        require_auth = True
    )

    """ statuses/retweets [Coming soon] """
    def retweets(self, id, *args, **kargs):
        return bind_api(
            path = '/statuses/retweets/%s.json' % id,
            parser = parse_statuses,
            allowed_param = ['count'],
            require_auth = True
        )(self, *args, **kargs)

    """ users/show """
    get_user = bind_api(
        path = '/users/show.json',
        parser = parse_user,
        allowed_param = ['id', 'user_id', 'screen_name']
    )

    """ Get the authenticated user """
    def me(self):
        return self.get_user(screen_name=self.auth.get_username())

    """ users/search """
    search_users = bind_api(
        path = '/users/search.json',
        parser = parse_users,
        require_auth = True,
        allowed_param = ['q', 'per_page', 'page']
    )

    """ statuses/friends """
    friends = bind_api(
        path = '/statuses/friends.json',
        parser = parse_users,
        allowed_param = ['id', 'user_id', 'screen_name', 'page', 'cursor']
    )

    """ statuses/followers """
    followers = bind_api(
        path = '/statuses/followers.json',
        parser = parse_users,
        allowed_param = ['id', 'user_id', 'screen_name', 'page', 'cursor']
    )

    """ direct_messages """
    direct_messages = bind_api(
        path = '/direct_messages.json',
        parser = parse_directmessages,
        allowed_param = ['since_id', 'max_id', 'count', 'page'],
        require_auth = True
    )

    """ direct_messages/sent """
    sent_direct_messages = bind_api(
        path = '/direct_messages/sent.json',
        parser = parse_directmessages,
        allowed_param = ['since_id', 'max_id', 'count', 'page'],
        require_auth = True
    )

    """ direct_messages/new """
    send_direct_message = bind_api(
        path = '/direct_messages/new.json',
        method = 'POST',
        parser = parse_dm,
        allowed_param = ['user', 'text'],
        require_auth = True
    )

    """ direct_messages/destroy """
    destroy_direct_message = bind_api(
        path = '/direct_messages/destroy.json',
        method = 'DELETE',
        parser = parse_dm,
        allowed_param = ['id'],
        require_auth = True
    )

    """ friendships/create """
    create_friendship = bind_api(
        path = '/friendships/create.json',
        method = 'POST',
        parser = parse_user,
        allowed_param = ['id', 'user_id', 'screen_name', 'follow'],
        require_auth = True
    )

    """ friendships/destroy """
    destroy_friendship = bind_api(
        path = '/friendships/destroy.json',
        method = 'DELETE',
        parser = parse_user,
        allowed_param = ['id', 'user_id', 'screen_name'],
        require_auth = True
    )

    """ friendships/exists """
    exists_friendship = bind_api(
        path = '/friendships/exists.json',
        parser = parse_json,
        allowed_param = ['user_a', 'user_b']
    )

    """ friendships/show """
    show_friendship = bind_api(
        path = '/friendships/show.json',
        parser = parse_friendship,
        allowed_param = ['source_id', 'source_screen_name',
                          'target_id', 'target_screen_name']
    )

    """ friends/ids """
    friends_ids = bind_api(
        path = '/friends/ids.json',
        parser = parse_ids,
        allowed_param = ['id', 'user_id', 'screen_name', 'cursor']
    )

    """ followers/ids """
    followers_ids = bind_api(
        path = '/followers/ids.json',
        parser = parse_ids,
        allowed_param = ['id', 'user_id', 'screen_name', 'cursor']
    )

    """ account/verify_credentials """
    def verify_credentials(self):
        try:
            return bind_api(
                path = '/account/verify_credentials.json',
                parser = parse_user,
                require_auth = True
            )(self)
        except TweepError:
            return False

    """ account/rate_limit_status """
    rate_limit_status = bind_api(
        path = '/account/rate_limit_status.json',
        parser = parse_json
    )

    """ account/update_delivery_device """
    set_delivery_device = bind_api(
        path = '/account/update_delivery_device.json',
        method = 'POST',
        allowed_param = ['device'],
        parser = parse_user,
        require_auth = True
    )

    """ account/update_profile_colors """
    update_profile_colors = bind_api(
        path = '/account/update_profile_colors.json',
        method = 'POST',
        parser = parse_user,
        allowed_param = ['profile_background_color', 'profile_text_color',
                          'profile_link_color', 'profile_sidebar_fill_color',
                          'profile_sidebar_border_color'],
        require_auth = True
    )

    """ account/update_profile_image """
    def update_profile_image(self, filename):
        headers, post_data = API._pack_image(filename, 700)
        return bind_api(
            path = '/account/update_profile_image.json',
            method = 'POST',
            parser = parse_user,
            require_auth = True
        )(self, post_data=post_data, headers=headers)

    """ account/update_profile_background_image """
    def update_profile_background_image(self, filename, *args, **kargs):
        headers, post_data = API._pack_image(filename, 800)
        bind_api(
            path = '/account/update_profile_background_image.json',
            method = 'POST',
            parser = parse_user,
            allowed_param = ['tile'],
            require_auth = True
        )(self, post_data=post_data, headers=headers)

    """ account/update_profile """
    update_profile = bind_api(
        path = '/account/update_profile.json',
        method = 'POST',
        parser = parse_user,
        allowed_param = ['name', 'url', 'location', 'description'],
        require_auth = True
    )

    """ favorites """
    favorites = bind_api(
        path = '/favorites.json',
        parser = parse_statuses,
        allowed_param = ['id', 'page']
    )

    """ favorites/create """
    def create_favorite(self, id):
        return bind_api(
            path = '/favorites/create/%s.json' % id,
            method = 'POST',
            parser = parse_status,
            allowed_param = ['id'],
            require_auth = True
        )(self, id)

    """ favorites/destroy """
    def destroy_favorite(self, id):
        return bind_api(
            path = '/favorites/destroy/%s.json' % id,
            method = 'DELETE',
            parser = parse_status,
            allowed_param = ['id'],
            require_auth = True
        )(self, id)

    """ notifications/follow """
    enable_notifications = bind_api(
        path = '/notifications/follow.json',
        method = 'POST',
        parser = parse_user,
        allowed_param = ['id', 'user_id', 'screen_name'],
        require_auth = True
    )

    """ notifications/leave """
    disable_notifications = bind_api(
        path = '/notifications/leave.json',
        method = 'POST',
        parser = parse_user,
        allowed_param = ['id', 'user_id', 'screen_name'],
        require_auth = True
    )

    """ blocks/create """
    create_block = bind_api(
        path = '/blocks/create.json',
        method = 'POST',
        parser = parse_user,
        allowed_param = ['id', 'user_id', 'screen_name'],
        require_auth = True
    )

    """ blocks/destroy """
    destroy_block = bind_api(
        path = '/blocks/destroy.json',
        method = 'DELETE',
        parser = parse_user,
        allowed_param = ['id', 'user_id', 'screen_name'],
        require_auth = True
    )

    """ blocks/exists """
    def exists_block(self, *args, **kargs):
        try:
            bind_api(
                path = '/blocks/exists.json',
                parser = parse_none,
                allowed_param = ['id', 'user_id', 'screen_name'],
                require_auth = True
            )(self, *args, **kargs)
        except TweepError:
            return False

        return True

    """ blocks/blocking """
    blocks = bind_api(
        path = '/blocks/blocking.json',
        parser = parse_users,
        allowed_param = ['page'],
        require_auth = True
    )

    """ blocks/blocking/ids """
    blocks_ids = bind_api(
        path = '/blocks/blocking/ids.json',
        parser = parse_json,
        require_auth = True
    )

    """ report_spam """
    report_spam = bind_api(
        path = '/report_spam.json',
        method = 'POST',
        parser = parse_user,
        allowed_param = ['id', 'user_id', 'screen_name'],
        require_auth = True
    )

    """ saved_searches """
    saved_searches = bind_api(
        path = '/saved_searches.json',
        parser = parse_saved_searches,
        require_auth = True
    )

    """ saved_searches/show """
    def get_saved_search(self, id):
        return bind_api(
            path = '/saved_searches/show/%s.json' % id,
            parser = parse_saved_search,
            require_auth = True
        )(self)

    """ saved_searches/create """
    create_saved_search = bind_api(
        path = '/saved_searches/create.json',
        method = 'POST',
        parser = parse_saved_search,
        allowed_param = ['query'],
        require_auth = True
    )

    """ saved_searches/destroy """
    def destroy_saved_search(self, id):
        return bind_api(
            path = '/saved_searches/destroy/%s.json' % id,
            method = 'DELETE',
            parser = parse_saved_search,
            allowed_param = ['id'],
            require_auth = True
        )(self)

    """ help/test """
    def test(self):
        try:
            return bind_api(
                path = '/help/test.json',
                parser = parse_return_true
            )(self)
        except TweepError:
            return False

    def create_list(self, *args, **kargs):
        return bind_api(
            path = '/%s/lists.json' % self.auth.get_username(),
            method = 'POST',
            parser = parse_list,
            allowed_param = ['name', 'mode'],
            require_auth = True
        )(self, *args, **kargs)

    def destroy_list(self, slug):
        return bind_api(
            path = '/%s/lists/%s.json' % (self.auth.get_username(), slug),
            method = 'DELETE',
            parser = parse_list,
            require_auth = True
        )(self)

    def update_list(self, slug, *args, **kargs):
        return bind_api(
            path = '/%s/lists/%s.json' % (self.auth.get_username(), slug),
            method = 'POST',
            parser = parse_list,
            allowed_param = ['name', 'mode'],
            require_auth = True
        )(self, *args, **kargs)

    def lists(self, *args, **kargs):
        return bind_api(
            path = '/%s/lists.json' % self.auth.get_username(),
            parser = parse_lists,
            allowed_param = ['cursor'],
            require_auth = True
        )(self, *args, **kargs)
    lists.pagination_mode = 'cursor'

    def lists_memberships(self, *args, **kargs):
        return bind_api(
            path = '/%s/lists/memberships.json' % self.auth.get_username(),
            parser = parse_lists,
            allowed_param = ['cursor'],
            require_auth = True
        )(self, *args, **kargs)
    lists_memberships.pagination_mode = 'cursor'

    def lists_subscriptions(self, *args, **kargs):
        return bind_api(
            path = '/%s/lists/subscriptions.json' % self.auth.get_username(),
            parser = parse_lists,
            allowed_param = ['cursor'],
            require_auth = True
        )(self, *args, **kargs)
    lists_subscriptions.pagination_mode = 'cursor'

    def list_timeline(self, owner, slug, *args, **kargs):
        return bind_api(
            path = '/%s/lists/%s/statuses.json' % (owner, slug),
            parser = parse_statuses,
            allowed_param = ['since_id', 'max_id', 'count', 'page']
        )(self, *args, **kargs)
    list_timeline.pagination_mode = 'page'

    def get_list(self, owner, slug):
        return bind_api(
            path = '/%s/lists/%s.json' % (owner, slug),
            parser = parse_list
        )(self)

    def add_list_member(self, slug, *args, **kargs):
        return bind_api(
            path = '/%s/%s/members.json' % (self.auth.get_username(), slug),
            method = 'POST',
            parser = parse_list,
            allowed_param = ['id'],
            require_auth = True
        )(self, *args, **kargs)

    def remove_list_member(self, slug, *args, **kargs):
        return bind_api(
            path = '/%s/%s/members.json' % (self.auth.get_username(), slug),
            method = 'DELETE',
            parser = parse_user,
            allowed_param = ['id'],
            require_auth = True
        )(self, *args, **kargs)

    def list_members(self, owner, slug, *args, **kargs):
        return bind_api(
            path = '/%s/%s/members.json' % (owner, slug),
            parser = parse_users,
            allowed_param = ['cursor']
        )(self, *args, **kargs)
    list_members.pagination_mode = 'cursor'

    def is_list_member(self, owner, slug, user_id):
        try:
            return bind_api(
                path = '/%s/%s/members/%s.json' % (owner, slug, user_id),
                parser = parse_user
            )(self)
        except TweepError:
            return False

    def subscribe_list(self, owner, slug):
        return bind_api(
            path = '/%s/%s/subscribers.json' % (owner, slug),
            method = 'POST',
            parser = parse_list,
            require_auth = True
        )(self)

    def unsubscribe_list(self, owner, slug):
        return bind_api(
            path = '/%s/%s/subscribers.json' % (owner, slug),
            method = 'DELETE',
            parser = parse_list,
            require_auth = True
        )(self)

    def list_subscribers(self, owner, slug, *args, **kargs):
        return bind_api(
            path = '/%s/%s/subscribers.json' % (owner, slug),
            parser = parse_users,
            allowed_param = ['cursor']
        )(self, *args, **kargs)
    list_subscribers.pagination_mode = 'cursor'

    def is_subscribed_list(self, owner, slug, user_id):
        try:
            return bind_api(
                path = '/%s/%s/subscribers/%s.json' % (owner, slug, user_id),
                parser = parse_user
            )(self)
        except TweepError:
            return False

    """ search """
    search = bind_api(
        search_api = True,
        path = '/search.json',
        parser = parse_search_results,
        allowed_param = ['q', 'lang', 'locale', 'rpp', 'page', 'since_id', 'geocode', 'show_user']
    )
    search.pagination_mode = 'page'

    """ trends """
    trends = bind_api(
        search_api = True,
        path = '/trends.json',
        parser = parse_json
    )

    """ trends/current """
    trends_current = bind_api(
        search_api = True,
        path = '/trends/current.json',
        parser = parse_json,
        allowed_param = ['exclude']
    )

    """ trends/daily """
    trends_daily = bind_api(
        search_api = True,
        path = '/trends/daily.json',
        parser = parse_json,
        allowed_param = ['date', 'exclude']
    )

    """ trends/weekly """
    trends_weekly = bind_api(
        search_api = True,
        path = '/trends/weekly.json',
        parser = parse_json,
        allowed_param = ['date', 'exclude']
    )

    """ Internal use only """
    @staticmethod
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

