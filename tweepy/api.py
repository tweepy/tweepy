# Tweepy
# Copyright 2009-2010 Joshua Roesslein
# See LICENSE for details.

import os
import mimetypes

from tweepy.binder import bind_api
from tweepy.error import TweepError
from tweepy.parsers import ModelParser
from tweepy.utils import list_to_csv


class API(object):
    """Twitter API"""

    def __init__(self, auth_handler=None,
            host='api.twitter.com', search_host='search.twitter.com',
             cache=None, secure=False, api_root='/1', search_root='',
            retry_count=0, retry_delay=0, retry_errors=None,
            parser=None):
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
        self.parser = parser or ModelParser()

    """ statuses/home_timeline """
    home_timeline = bind_api(
        path = '/statuses/home_timeline.json',
        payload_type = 'status', payload_list = True,
        allowed_param = ['since_id', 'max_id', 'count', 'page'],
        require_auth = True
    )

    """ statuses/friends_timeline """
    friends_timeline = bind_api(
        path = '/statuses/friends_timeline.json',
        payload_type = 'status', payload_list = True,
        allowed_param = ['since_id', 'max_id', 'count', 'page'],
        require_auth = True
    )

    """ statuses/user_timeline """
    user_timeline = bind_api(
        path = '/statuses/user_timeline.json',
        payload_type = 'status', payload_list = True,
        allowed_param = ['id', 'user_id', 'screen_name', 'since_id',
                          'max_id', 'count', 'page', 'include_rts']
    )

    """ statuses/mentions """
    mentions = bind_api(
        path = '/statuses/mentions.json',
        payload_type = 'status', payload_list = True,
        allowed_param = ['since_id', 'max_id', 'count', 'page'],
        require_auth = True
    )

    """/statuses/retweeted_by_user.format"""
    retweeted_by_user = bind_api(
        path = '/statuses/retweeted_by_user.json',
        payload_type = 'status', payload_list = True,
        allowed_param = ['screen_name', 'id', 'count', 'since_id',
                            'max_id', 'page', 'include_entities']
    )

    """/statuses/:id/retweeted_by.format"""
    retweeted_by = bind_api(
        path = '/statuses/{id}/retweeted_by.json',
        payload_type = 'status', payload_list = True,
        allowed_param = ['id', 'count', 'page'],
        require_auth = True
    )

    """/related_results/show/:id.format"""
    related_results = bind_api(
        path = '/related_results/show/{id}.json',
        payload_type = 'relation', payload_list = True,
        allowed_param = ['id'],
        require_auth = False
	)

    """/statuses/:id/retweeted_by/ids.format"""
    retweeted_by_ids = bind_api(
        path = '/statuses/{id}/retweeted_by/ids.json',
        payload_type = 'ids',
        allowed_param = ['id', 'count', 'page'],
        require_auth = True
    )

    """ statuses/retweeted_by_me """
    retweeted_by_me = bind_api(
        path = '/statuses/retweeted_by_me.json',
        payload_type = 'status', payload_list = True,
        allowed_param = ['since_id', 'max_id', 'count', 'page'],
        require_auth = True
    )

    """ statuses/retweeted_to_me """
    retweeted_to_me = bind_api(
        path = '/statuses/retweeted_to_me.json',
        payload_type = 'status', payload_list = True,
        allowed_param = ['since_id', 'max_id', 'count', 'page'],
        require_auth = True
    )

    """ statuses/retweeted_by_user """
    retweeted_by_user = bind_api(
        path = '/statuses/retweeted_by_user.json',
        payload_type = 'status', payload_list = True,
        allowed_param = ['screen_name', 'id', 'since_id', 'max_id', 'count', 'page', 'trim_user', 'include_entities'],
        require_auth = False
    )

    """ statuses/retweets_of_me """
    retweets_of_me = bind_api(
        path = '/statuses/retweets_of_me.json',
        payload_type = 'status', payload_list = True,
        allowed_param = ['since_id', 'max_id', 'count', 'page'],
        require_auth = True
    )

    """ statuses/show """
    get_status = bind_api(
        path = '/statuses/show.json',
        payload_type = 'status',
        allowed_param = ['id']
    )

    """ statuses/update """
    update_status = bind_api(
        path = '/statuses/update.json',
        method = 'POST',
        payload_type = 'status',
        allowed_param = ['status', 'in_reply_to_status_id', 'lat', 'long', 'source', 'place_id'],
        require_auth = True
    )

    """ statuses/destroy """
    destroy_status = bind_api(
        path = '/statuses/destroy.json',
        method = 'DELETE',
        payload_type = 'status',
        allowed_param = ['id'],
        require_auth = True
    )

    """ statuses/retweet """
    retweet = bind_api(
        path = '/statuses/retweet/{id}.json',
        method = 'POST',
        payload_type = 'status',
        allowed_param = ['id'],
        require_auth = True
    )

    """ statuses/retweets """
    retweets = bind_api(
        path = '/statuses/retweets/{id}.json',
        payload_type = 'status', payload_list = True,
        allowed_param = ['id', 'count'],
        require_auth = True
    )

    """ users/show """
    get_user = bind_api(
        path = '/users/show.json',
        payload_type = 'user',
        allowed_param = ['id', 'user_id', 'screen_name']
    )

    """ Perform bulk look up of users from user ID or screenname """
    def lookup_users(self, user_ids=None, screen_names=None):
        return self._lookup_users(list_to_csv(user_ids), list_to_csv(screen_names))

    _lookup_users = bind_api(
        path = '/users/lookup.json',
        payload_type = 'user', payload_list = True,
        allowed_param = ['user_id', 'screen_name'],
    )

    """ Get the authenticated user """
    def me(self):
        return self.get_user(screen_name=self.auth.get_username())

    """ users/search """
    search_users = bind_api(
        path = '/users/search.json',
        payload_type = 'user', payload_list = True,
        require_auth = True,
        allowed_param = ['q', 'per_page', 'page']
    )

    """ users/suggestions/:slug """
    suggested_users = bind_api(
        path = '/users/suggestions/{slug}.json',
        payload_type = 'user', payload_list = True,
        require_auth = True,
        allowed_param = ['slug', 'lang']
    )

    """ users/suggestions """
    suggested_categories = bind_api(
        path = '/users/suggestions.json',
        payload_type = 'category', payload_list = True,
        allowed_param = ['lang'],
        require_auth = True
    )

    """ users/suggestions/:slug/members """
    suggested_users_tweets = bind_api(
        path = '/users/suggestions/{slug}/members.json',
        payload_type = 'status', payload_list = True,
        allowed_param = ['slug'],
        require_auth = True
    )

    """ statuses/friends """
    friends = bind_api(
        path = '/statuses/friends.json',
        payload_type = 'user', payload_list = True,
        allowed_param = ['id', 'user_id', 'screen_name', 'page', 'cursor']
    )

    """ statuses/followers """
    followers = bind_api(
        path = '/statuses/followers.json',
        payload_type = 'user', payload_list = True,
        allowed_param = ['id', 'user_id', 'screen_name', 'page', 'cursor']
    )

    """ direct_messages """
    direct_messages = bind_api(
        path = '/direct_messages.json',
        payload_type = 'direct_message', payload_list = True,
        allowed_param = ['since_id', 'max_id', 'count', 'page'],
        require_auth = True
    )

    """ direct_messages/show """
    get_direct_message = bind_api(
        path = '/direct_messages/show/{id}.json',
        payload_type = 'direct_message',
        allowed_param = ['id'],
        require_auth = True
    )

    """ direct_messages/sent """
    sent_direct_messages = bind_api(
        path = '/direct_messages/sent.json',
        payload_type = 'direct_message', payload_list = True,
        allowed_param = ['since_id', 'max_id', 'count', 'page'],
        require_auth = True
    )

    """ direct_messages/new """
    send_direct_message = bind_api(
        path = '/direct_messages/new.json',
        method = 'POST',
        payload_type = 'direct_message',
        allowed_param = ['user', 'screen_name', 'user_id', 'text'],
        require_auth = True
    )

    """ direct_messages/destroy """
    destroy_direct_message = bind_api(
        path = '/direct_messages/destroy.json',
        method = 'DELETE',
        payload_type = 'direct_message',
        allowed_param = ['id'],
        require_auth = True
    )

    """ friendships/create """
    create_friendship = bind_api(
        path = '/friendships/create.json',
        method = 'POST',
        payload_type = 'user',
        allowed_param = ['id', 'user_id', 'screen_name', 'follow'],
        require_auth = True
    )

    """ friendships/destroy """
    destroy_friendship = bind_api(
        path = '/friendships/destroy.json',
        method = 'DELETE',
        payload_type = 'user',
        allowed_param = ['id', 'user_id', 'screen_name'],
        require_auth = True
    )

    """ friendships/exists """
    exists_friendship = bind_api(
        path = '/friendships/exists.json',
        payload_type = 'json',
        allowed_param = ['user_a', 'user_b']
    )

    """ friendships/show """
    show_friendship = bind_api(
        path = '/friendships/show.json',
        payload_type = 'friendship',
        allowed_param = ['source_id', 'source_screen_name',
                          'target_id', 'target_screen_name']
    )


    """ Perform bulk look up of friendships from user ID or screenname """
    def lookup_friendships(self, user_ids=None, screen_names=None):
	    return self._lookup_friendships(list_to_csv(user_ids), list_to_csv(screen_names))

    _lookup_friendships = bind_api(
        path = '/friendships/lookup.json',
        payload_type = 'relationship', payload_list = True,
        allowed_param = ['user_id', 'screen_name'],
        require_auth = True
    )


    """ friends/ids """
    friends_ids = bind_api(
        path = '/friends/ids.json',
        payload_type = 'ids',
        allowed_param = ['id', 'user_id', 'screen_name', 'cursor']
    )

    """ friendships/incoming """
    friendships_incoming = bind_api(
        path = '/friendships/incoming.json',
        payload_type = 'ids',
        allowed_param = ['cursor']
    )

    """ friendships/outgoing"""
    friendships_outgoing = bind_api(
        path = '/friendships/outgoing.json',
        payload_type = 'ids',
        allowed_param = ['cursor']
    )

    """ followers/ids """
    followers_ids = bind_api(
        path = '/followers/ids.json',
        payload_type = 'ids',
        allowed_param = ['id', 'user_id', 'screen_name', 'cursor']
    )

    """ account/verify_credentials """
    def verify_credentials(self, **kargs):
        try:
            return bind_api(
                path = '/account/verify_credentials.json',
                payload_type = 'user',
                require_auth = True,
                allowed_param = ['include_entities', 'skip_status'],
            )(self, **kargs)
        except TweepError, e:
            if e.response and e.response.status == 401:
                return False
            raise

    """ account/rate_limit_status """
    rate_limit_status = bind_api(
        path = '/account/rate_limit_status.json',
        payload_type = 'json',
        use_cache = False
    )

    """ account/update_delivery_device """
    set_delivery_device = bind_api(
        path = '/account/update_delivery_device.json',
        method = 'POST',
        allowed_param = ['device'],
        payload_type = 'user',
        require_auth = True
    )

    """ account/update_profile_colors """
    update_profile_colors = bind_api(
        path = '/account/update_profile_colors.json',
        method = 'POST',
        payload_type = 'user',
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
            payload_type = 'user',
            require_auth = True
        )(self, post_data=post_data, headers=headers)

    """ account/update_profile_background_image """
    def update_profile_background_image(self, filename, *args, **kargs):
        headers, post_data = API._pack_image(filename, 800)
        bind_api(
            path = '/account/update_profile_background_image.json',
            method = 'POST',
            payload_type = 'user',
            allowed_param = ['tile'],
            require_auth = True
        )(self, post_data=post_data, headers=headers)

    """ account/update_profile """
    update_profile = bind_api(
        path = '/account/update_profile.json',
        method = 'POST',
        payload_type = 'user',
        allowed_param = ['name', 'url', 'location', 'description'],
        require_auth = True
    )

    """ favorites """
    favorites = bind_api(
        path = '/favorites.json',
        payload_type = 'status', payload_list = True,
        allowed_param = ['id', 'max_id', 'page']
    )

    """ favorites/create """
    create_favorite = bind_api(
        path = '/favorites/create/{id}.json',
        method = 'POST',
        payload_type = 'status',
        allowed_param = ['id'],
        require_auth = True
    )

    """ favorites/destroy """
    destroy_favorite = bind_api(
        path = '/favorites/destroy/{id}.json',
        method = 'DELETE',
        payload_type = 'status',
        allowed_param = ['id'],
        require_auth = True
    )

    """ notifications/follow """
    enable_notifications = bind_api(
        path = '/notifications/follow.json',
        method = 'POST',
        payload_type = 'user',
        allowed_param = ['id', 'user_id', 'screen_name'],
        require_auth = True
    )

    """ notifications/leave """
    disable_notifications = bind_api(
        path = '/notifications/leave.json',
        method = 'POST',
        payload_type = 'user',
        allowed_param = ['id', 'user_id', 'screen_name'],
        require_auth = True
    )

    """ blocks/create """
    create_block = bind_api(
        path = '/blocks/create.json',
        method = 'POST',
        payload_type = 'user',
        allowed_param = ['id', 'user_id', 'screen_name'],
        require_auth = True
    )

    """ blocks/destroy """
    destroy_block = bind_api(
        path = '/blocks/destroy.json',
        method = 'DELETE',
        payload_type = 'user',
        allowed_param = ['id', 'user_id', 'screen_name'],
        require_auth = True
    )

    """ blocks/exists """
    def exists_block(self, *args, **kargs):
        try:
            bind_api(
                path = '/blocks/exists.json',
                allowed_param = ['id', 'user_id', 'screen_name'],
                require_auth = True
            )(self, *args, **kargs)
        except TweepError:
            return False
        return True

    """ blocks/blocking """
    blocks = bind_api(
        path = '/blocks/blocking.json',
        payload_type = 'user', payload_list = True,
        allowed_param = ['page'],
        require_auth = True
    )

    """ blocks/blocking/ids """
    blocks_ids = bind_api(
        path = '/blocks/blocking/ids.json',
        payload_type = 'json',
        require_auth = True
    )

    """ report_spam """
    report_spam = bind_api(
        path = '/report_spam.json',
        method = 'POST',
        payload_type = 'user',
        allowed_param = ['id', 'user_id', 'screen_name'],
        require_auth = True
    )

    """ saved_searches """
    saved_searches = bind_api(
        path = '/saved_searches.json',
        payload_type = 'saved_search', payload_list = True,
        require_auth = True
    )

    """ saved_searches/show """
    get_saved_search = bind_api(
        path = '/saved_searches/show/{id}.json',
        payload_type = 'saved_search',
        allowed_param = ['id'],
        require_auth = True
    )

    """ saved_searches/create """
    create_saved_search = bind_api(
        path = '/saved_searches/create.json',
        method = 'POST',
        payload_type = 'saved_search',
        allowed_param = ['query'],
        require_auth = True
    )

    """ saved_searches/destroy """
    destroy_saved_search = bind_api(
        path = '/saved_searches/destroy/{id}.json',
        method = 'DELETE',
        payload_type = 'saved_search',
        allowed_param = ['id'],
        require_auth = True
    )

    """ help/test """
    def test(self):
        try:
            bind_api(
                path = '/help/test.json',
            )(self)
        except TweepError:
            return False
        return True

    def create_list(self, *args, **kargs):
        return bind_api(
            path = '/%s/lists.json' % self.auth.get_username(),
            method = 'POST',
            payload_type = 'list',
            allowed_param = ['name', 'mode', 'description'],
            require_auth = True
        )(self, *args, **kargs)

    def destroy_list(self, slug):
        return bind_api(
            path = '/%s/lists/%s.json' % (self.auth.get_username(), slug),
            method = 'DELETE',
            payload_type = 'list',
            require_auth = True
        )(self)

    def update_list(self, slug, *args, **kargs):
        return bind_api(
            path = '/%s/lists/%s.json' % (self.auth.get_username(), slug),
            method = 'POST',
            payload_type = 'list',
            allowed_param = ['name', 'mode', 'description'],
            require_auth = True
        )(self, *args, **kargs)

    lists = bind_api(
        path = '/{user}/lists.json',
        payload_type = 'list', payload_list = True,
        allowed_param = ['user', 'cursor'],
        require_auth = True
    )

    lists_memberships = bind_api(
        path = '/{user}/lists/memberships.json',
        payload_type = 'list', payload_list = True,
        allowed_param = ['user', 'cursor'],
        require_auth = True
    )

    lists_subscriptions = bind_api(
        path = '/{user}/lists/subscriptions.json',
        payload_type = 'list', payload_list = True,
        allowed_param = ['user', 'cursor'],
        require_auth = True
    )

    list_timeline = bind_api(
        path = '/{owner}/lists/{slug}/statuses.json',
        payload_type = 'status', payload_list = True,
        allowed_param = ['owner', 'slug', 'since_id', 'max_id', 'per_page', 'page']
    )

    get_list = bind_api(
        path = '/{owner}/lists/{slug}.json',
        payload_type = 'list',
        allowed_param = ['owner', 'slug']
    )

    def add_list_member(self, slug, *args, **kargs):
        return bind_api(
            path = '/%s/%s/members.json' % (self.auth.get_username(), slug),
            method = 'POST',
            payload_type = 'list',
            allowed_param = ['id'],
            require_auth = True
        )(self, *args, **kargs)

    def remove_list_member(self, slug, *args, **kargs):
        return bind_api(
            path = '/%s/%s/members.json' % (self.auth.get_username(), slug),
            method = 'DELETE',
            payload_type = 'list',
            allowed_param = ['id'],
            require_auth = True
        )(self, *args, **kargs)

    list_members = bind_api(
        path = '/{owner}/{slug}/members.json',
        payload_type = 'user', payload_list = True,
        allowed_param = ['owner', 'slug', 'cursor']
    )

    def is_list_member(self, owner, slug, user_id):
        try:
            return bind_api(
                path = '/%s/%s/members/%s.json' % (owner, slug, user_id),
                payload_type = 'user'
            )(self)
        except TweepError:
            return False

    subscribe_list = bind_api(
        path = '/{owner}/{slug}/subscribers.json',
        method = 'POST',
        payload_type = 'list',
        allowed_param = ['owner', 'slug'],
        require_auth = True
    )

    unsubscribe_list = bind_api(
        path = '/{owner}/{slug}/subscribers.json',
        method = 'DELETE',
        payload_type = 'list',
        allowed_param = ['owner', 'slug'],
        require_auth = True
    )

    list_subscribers = bind_api(
        path = '/{owner}/{slug}/subscribers.json',
        payload_type = 'user', payload_list = True,
        allowed_param = ['owner', 'slug', 'cursor']
    )

    def is_subscribed_list(self, owner, slug, user_id):
        try:
            return bind_api(
                path = '/%s/%s/subscribers/%s.json' % (owner, slug, user_id),
                payload_type = 'user'
            )(self)
        except TweepError:
            return False

    """ trends/available """
    trends_available = bind_api(
        path = '/trends/available.json',
        payload_type = 'json',
        allowed_param = ['lat', 'long']
    )

    """ trends/location """
    trends_location = bind_api(
        path = '/trends/{woeid}.json',
        payload_type = 'json',
        allowed_param = ['woeid']
    )

    """ search """
    search = bind_api(
        search_api = True,
        path = '/search.json',
        payload_type = 'search_result', payload_list = True,
        allowed_param = ['q', 'lang', 'locale', 'rpp', 'page', 'since_id', 'geocode', 'show_user', 'max_id', 'since', 'until', 'result_type']
    )
    search.pagination_mode = 'page'

    """ trends/daily """
    trends_daily = bind_api(
        path = '/trends/daily.json',
        payload_type = 'json',
        allowed_param = ['date', 'exclude']
    )

    """ trends/weekly """
    trends_weekly = bind_api(
        path = '/trends/weekly.json',
        payload_type = 'json',
        allowed_param = ['date', 'exclude']
    )

    """ geo/reverse_geocode """
    reverse_geocode = bind_api(
        path = '/geo/reverse_geocode.json',
        payload_type = 'place', payload_list = True,
        allowed_param = ['lat', 'long', 'accuracy', 'granularity', 'max_results']
    )

    """ geo/nearby_places """
    # listed as deprecated on twitter's API documents
    nearby_places = bind_api(
        path = '/geo/nearby_places.json',
        payload_type = 'place', payload_list = True,
        allowed_param = ['lat', 'long', 'ip', 'accuracy', 'granularity', 'max_results']
    )

    """ geo/id """
    geo_id = bind_api(
        path = '/geo/id/{id}.json',
        payload_type = 'place',
        allowed_param = ['id']
    )

    """ geo/search """
    geo_search = bind_api(
        path = '/geo/search.json',
        payload_type = 'place', payload_list = True,
        allowed_param = ['lat', 'long', 'query', 'ip', 'granularity', 'accuracy', 'max_results', 'contained_within']
    )

    """ geo/similar_places """
    geo_similar_places = bind_api(
        path = '/geo/similar_places.json',
        payload_type = 'place', payload_list = True,
        allowed_param = ['lat', 'long', 'name', 'contained_within']
    )

    """ Internal use only """
    @staticmethod
    def _pack_image(filename, max_size):
        """Pack image from file into multipart-formdata post body"""
        # image must be less than 700kb in size
        try:
            if os.path.getsize(filename) > (max_size * 1024):
                raise TweepError('File is too big, must be less than 700kb.')
        except os.error:
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
            'Content-Length': str(len(body))
        }

        return headers, body

