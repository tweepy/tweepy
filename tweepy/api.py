# Tweepy
# Copyright 2009-2021 Joshua Roesslein
# See LICENSE for details.

import imghdr
import mimetypes
import os

from tweepy.binder import bind_api, pagination, payload
from tweepy.error import TweepError
from tweepy.parsers import ModelParser, Parser
from tweepy.utils import list_to_csv


class API:
    """Twitter API"""

    def __init__(self, auth_handler=None,
                 host='api.twitter.com', upload_host='upload.twitter.com',
                 cache=None, retry_count=0, retry_delay=0, retry_errors=None,
                 timeout=60, parser=None, wait_on_rate_limit=False, proxy=''):
        """
        API instance constructor

        :param auth_handler:
        :param host: url of the server of the rest api,
                     default: 'api.twitter.com'
        :param upload_host: url of the upload server,
                            default: 'upload.twitter.com'
        :param cache: Cache to query if a GET method is used, default: None
        :param retry_count: number of allowed retries, default: 0
        :param retry_delay: delay in second between retries, default: 0
        :param retry_errors: default: None
        :param timeout: delay before to consider the request as timed out in
                        seconds, default: 60
        :param parser: ModelParser instance to parse the responses,
                       default: None
        :param wait_on_rate_limit: If the api wait when it hits the rate limit,
                                   default: False
        :param proxy: Url to use as proxy during the HTTP request, default: ''

        :raise TypeError: If the given parser is not a ModelParser instance.
        """
        self.auth = auth_handler
        self.host = host
        self.upload_host = upload_host
        self.cache = cache
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.retry_errors = retry_errors
        self.timeout = timeout
        self.wait_on_rate_limit = wait_on_rate_limit
        self.parser = parser or ModelParser()
        self.proxy = {}
        if proxy:
            self.proxy['https'] = proxy

        # Attempt to explain more clearly the parser argument requirements
        # https://github.com/tweepy/tweepy/issues/421

        parser_type = Parser
        if not isinstance(self.parser, parser_type):
            raise TypeError(
                f'"parser" argument has to be an instance of "{parser_type.__name__}".'
                f' It is currently a {type(self.parser)}.'
            )

    @pagination(mode='id')
    @payload('status', list=True)
    def home_timeline(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/timelines/api-reference/get-statuses-home_timeline
            :allowed_param: 'count', 'since_id', 'max_id', 'trim_user',
                            'exclude_replies', 'include_entities'
        """
        return bind_api(
            self, 'GET', 'statuses/home_timeline', *args,
            allowed_param=['count', 'since_id', 'max_id', 'trim_user',
                           'exclude_replies', 'include_entities'],
            require_auth=True, **kwargs
        )

    @payload('status', list=True)
    def statuses_lookup(self, id_, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/get-statuses-lookup
            :allowed_param: 'id', 'include_entities', 'trim_user', 'map',
                            'include_ext_alt_text', 'include_card_uri'
        """
        if 'map_' in kwargs:
            kwargs['map'] = kwargs.pop('map_')

        return bind_api(
            self, 'GET', 'statuses/lookup', list_to_csv(id_), *args,
            allowed_param=['id', 'include_entities', 'trim_user', 'map',
                           'include_ext_alt_text', 'include_card_uri'],
            require_auth=True, **kwargs
        )

    @pagination(mode='id')
    @payload('status', list=True)
    def user_timeline(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/timelines/api-reference/get-statuses-user_timeline
            :allowed_param: 'user_id', 'screen_name', 'since_id', 'count',
                            'max_id', 'trim_user', 'exclude_replies',
                            'include_rts'
        """
        return bind_api(
            self, 'GET', 'statuses/user_timeline', *args,
            allowed_param=['user_id', 'screen_name', 'since_id', 'count',
                           'max_id', 'trim_user', 'exclude_replies',
                           'include_rts'], **kwargs
        )

    @pagination(mode='id')
    @payload('status', list=True)
    def mentions_timeline(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/timelines/api-reference/get-statuses-mentions_timeline
            :allowed_param: 'since_id', 'max_id', 'count'
        """
        return bind_api(
            self, 'GET', 'statuses/mentions_timeline', *args,
            allowed_param=['since_id', 'max_id', 'count'],
            require_auth=True, **kwargs
        )

    @pagination(mode='id')
    @payload('status', list=True)
    def retweets_of_me(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/get-statuses-retweets_of_me
            :allowed_param: 'since_id', 'max_id', 'count'
        """
        return bind_api(
            self, 'GET', 'statuses/retweets_of_me', *args,
            allowed_param=['since_id', 'max_id', 'count'],
            require_auth=True, **kwargs
        )

    @payload('status')
    def get_status(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/get-statuses-show-id
            :allowed_param: 'id', 'trim_user', 'include_my_retweet',
                            'include_entities', 'include_ext_alt_text',
                            'include_card_uri'
        """
        return bind_api(
            self, 'GET', 'statuses/show', *args,
            allowed_param=['id', 'trim_user', 'include_my_retweet',
                           'include_entities', 'include_ext_alt_text',
                           'include_card_uri'], **kwargs
        )

    @payload('status')
    def update_status(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/post-statuses-update
            :allowed_param: 'status', 'in_reply_to_status_id',
                            'auto_populate_reply_metadata',
                            'exclude_reply_user_ids', 'attachment_url',
                            'media_ids', 'possibly_sensitive', 'lat', 'long',
                            'place_id', 'display_coordinates', 'trim_user',
                            'enable_dmcommands', 'fail_dmcommands', 'card_uri'
        """
        if 'media_ids' in kwargs:
            kwargs['media_ids'] = list_to_csv(kwargs['media_ids'])

        return bind_api(
            self, 'POST', 'statuses/update', *args,
            allowed_param=['status', 'in_reply_to_status_id',
                           'auto_populate_reply_metadata',
                           'exclude_reply_user_ids', 'attachment_url',
                           'media_ids', 'possibly_sensitive', 'lat', 'long',
                           'place_id', 'display_coordinates', 'trim_user',
                           'enable_dmcommands', 'fail_dmcommands',
                           'card_uri'],
            require_auth=True, **kwargs
        )

    @payload('media')
    def media_upload(self, filename, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/media/upload-media/api-reference/post-media-upload
            :allowed_param:
        """
        f = kwargs.pop('file', None)

        h = None
        if f is not None:
            location = f.tell()
            h = f.read(32)
            f.seek(location)
        file_type = imghdr.what(filename, h=h) or mimetypes.guess_type(filename)[0]
        if file_type == 'gif':
            max_size = 14649
        else:
            max_size = 4883

        headers, post_data = API._pack_image(filename, max_size,
                                             form_field='media', f=f,
                                             file_type=file_type)
        kwargs.update({'headers': headers, 'post_data': post_data})

        return bind_api(
            self, 'POST', 'media/upload', *args,
            allowed_param=[],
            require_auth=True,
            upload_api=True, **kwargs
        )

    def create_media_metadata(self, media_id, alt_text, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/media/upload-media/api-reference/post-media-metadata-create
            :allowed_param:
        """
        kwargs['json_payload'] = {
            'media_id': media_id,
            'alt_text': {'text': alt_text}
        }

        return bind_api(
            self, 'POST', 'media/metadata/create', *args,
            allowed_param=[],
            require_auth=True,
            upload_api=True, **kwargs
        )

    @payload('status')
    def update_with_media(self, filename, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/post-statuses-update_with_media
            :allowed_param: 'status', 'possibly_sensitive',
                            'in_reply_to_status_id',
                            'in_reply_to_status_id_str',
                            'auto_populate_reply_metadata', 'lat', 'long',
                            'place_id', 'display_coordinates'
        """
        f = kwargs.pop('file', None)
        headers, post_data = API._pack_image(filename, 3072,
                                             form_field='media[]', f=f)
        kwargs.update({'headers': headers, 'post_data': post_data})

        return bind_api(
            self, 'POST', 'statuses/update_with_media', *args,
            allowed_param=['status', 'possibly_sensitive',
                           'in_reply_to_status_id',
                           'in_reply_to_status_id_str',
                           'auto_populate_reply_metadata', 'lat', 'long',
                           'place_id', 'display_coordinates'],
            require_auth=True, **kwargs
        )

    @payload('status')
    def destroy_status(self, status_id, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/post-statuses-destroy-id
            :allowed_param:
        """
        return bind_api(
            self, 'POST', f'statuses/destroy/{status_id}', *args,
            require_auth=True, **kwargs
        )

    @payload('status')
    def retweet(self, status_id, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/post-statuses-retweet-id
            :allowed_param:
        """
        return bind_api(
            self, 'POST', f'statuses/retweet/{status_id}', *args,
            require_auth=True, **kwargs
        )

    @payload('status')
    def unretweet(self, status_id, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/post-statuses-unretweet-id
            :allowed_param:
        """
        return bind_api(
            self, 'POST', f'statuses/unretweet/{status_id}', *args,
            require_auth=True, **kwargs
        )

    @payload('status', list=True)
    def retweets(self, status_id, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/get-statuses-retweets-id
            :allowed_param: 'count'
        """
        return bind_api(
            self, 'GET', f'statuses/retweets/{status_id}', *args,
            allowed_param=['count'],
            require_auth=True, **kwargs
        )

    @pagination(mode='cursor')
    @payload('ids')
    def retweeters(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/get-statuses-retweeters-ids
            :allowed_param: 'id', 'cursor', 'stringify_ids
        """
        return bind_api(
            self, 'GET', 'statuses/retweeters/ids', *args,
            allowed_param=['id', 'cursor', 'stringify_ids'], **kwargs
        )

    @payload('user')
    def get_user(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-users-show
            :allowed_param: 'id', 'user_id', 'screen_name'
        """
        return bind_api(
            self, 'GET', 'users/show', *args,
            allowed_param=['id', 'user_id', 'screen_name'], **kwargs
        )

    @payload('json')
    def get_oembed(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/get-statuses-oembed
            :allowed_param: 'url', 'maxwidth', 'hide_media', 'hide_thread',
                            'omit_script', 'align', 'related', 'lang', 'theme',
                            'link_color', 'widget_type', 'dnt'
        """
        return bind_api(
            self, 'GET', 'statuses/oembed', *args,
            allowed_param=['url', 'maxwidth', 'hide_media', 'hide_thread',
                           'omit_script', 'align', 'related', 'lang', 'theme',
                           'link_color', 'widget_type', 'dnt'], **kwargs
        )

    @payload('user', list=True)
    def lookup_users(self, user_ids=None, screen_names=None, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-users-lookup
            :allowed_param: 'user_id', 'screen_name', 'include_entities',
                            'tweet_mode'
        """
        return bind_api(
            self, 'POST', 'users/lookup', list_to_csv(user_ids),
            list_to_csv(screen_names), *args,
            allowed_param=['user_id', 'screen_name', 'include_entities',
                           'tweet_mode'], **kwargs
        )

    def me(self):
        """ Get the authenticated user """
        return self.get_user(screen_name=self.auth.get_username())

    @pagination(mode='page')
    @payload('user', list=True)
    def search_users(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-users-search
            :allowed_param: 'q', 'count', 'page'
        """
        return bind_api(
            self, 'GET', 'users/search', *args,
            require_auth=True,
            allowed_param=['q', 'count', 'page'], **kwargs
        )

    @payload('direct_message')
    def get_direct_message(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/direct-messages/sending-and-receiving/api-reference/get-event
            :allowed_param: 'id'
        """
        return bind_api(
            self, 'GET', 'direct_messages/events/show', *args,
            allowed_param=['id'],
            require_auth=True, **kwargs
        )

    @pagination(mode='dm_cursor')
    @payload('direct_message', list=True)
    def list_direct_messages(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/direct-messages/sending-and-receiving/api-reference/list-events
            :allowed_param: 'count', 'cursor'
        """
        return bind_api(
            self, 'GET', 'direct_messages/events/list', *args,
            allowed_param=['count', 'cursor'],
            require_auth=True, **kwargs
        )

    @payload('direct_message')
    def send_direct_message(self, recipient_id, text, quick_reply_options=None,
                            attachment_type=None, attachment_media_id=None,
                            ctas=None, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/direct-messages/sending-and-receiving/api-reference/new-event
            :allowed_param: 'recipient_id', 'text', 'quick_reply_type',
                            'attachment_type', attachment_media_id'
        """
        json_payload = {
            'event': {'type': 'message_create',
                      'message_create': {
                          'target': {'recipient_id': recipient_id},
                          'message_data': {'text': text}
                      }
            }
        }
        message_data = json_payload['event']['message_create']['message_data']
        if quick_reply_options is not None:
            message_data['quick_reply'] = {
                'type': 'options',
                'options': quick_reply_options
            }
        if attachment_type is not None and attachment_media_id is not None:
            message_data['attachment'] = {
                'type': attachment_type,
                'media': {'id': attachment_media_id}
            }
        if ctas is not None:
            message_data['ctas'] = ctas
        return bind_api(
            self, 'POST', 'direct_messages/events/new',
            require_auth=True, 
            json_payload=json_payload, **kwargs
        )

    def destroy_direct_message(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/direct-messages/sending-and-receiving/api-reference/delete-message-event
            :allowed_param: 'id'
        """
        return bind_api(
            self, 'DELETE', 'direct_messages/events/destroy', *args,
            allowed_param=['id'],
            require_auth=True, **kwargs
        )

    @payload('user')
    def create_friendship(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/post-friendships-create
            :allowed_param: 'id', 'user_id', 'screen_name', 'follow'
        """
        return bind_api(
            self, 'POST', 'friendships/create', *args,
            allowed_param=['id', 'user_id', 'screen_name', 'follow'],
            require_auth=True, **kwargs
        )

    @payload('user')
    def destroy_friendship(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/post-friendships-destroy
            :allowed_param: 'id', 'user_id', 'screen_name'
        """
        return bind_api(
            self, 'POST', 'friendships/destroy', *args,
            allowed_param=['id', 'user_id', 'screen_name'],
            require_auth=True, **kwargs
        )

    @payload('friendship')
    def show_friendship(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-friendships-show
            :allowed_param: 'source_id', 'source_screen_name', 'target_id',
                            'target_screen_name'
        """
        return bind_api(
            self, 'GET', 'friendships/show', *args,
            allowed_param=['source_id', 'source_screen_name',
                           'target_id', 'target_screen_name'], **kwargs
        )

    @payload('relationship', list=True)
    def lookup_friendships(self, user_ids=None, screen_names=None, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-friendships-lookup
            :allowed_param: 'user_id', 'screen_name'
        """
        return bind_api(
            self, 'GET', 'friendships/lookup', list_to_csv(user_ids),
            list_to_csv(screen_names),
            allowed_param=['user_id', 'screen_name'],
            require_auth=True, **kwargs
        )

    @pagination(mode='cursor')
    @payload('ids')
    def friends_ids(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-friends-ids
            :allowed_param: 'id', 'user_id', 'screen_name', 'cursor'
        """
        return bind_api(
            self, 'GET', 'friends/ids', *args,
            allowed_param=['id', 'user_id', 'screen_name', 'cursor'], **kwargs
        )

    @pagination(mode='cursor')
    @payload('user', list=True)
    def friends(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-friends-list
            :allowed_param: 'id', 'user_id', 'screen_name', 'cursor', 'count',
                            'skip_status', 'include_user_entities'
        """
        return bind_api(
            self, 'GET', 'friends/list', *args,
            allowed_param=['id', 'user_id', 'screen_name', 'cursor', 'count',
                           'skip_status', 'include_user_entities'], **kwargs
        )

    @pagination(mode='cursor')
    @payload('ids')
    def friendships_incoming(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-friendships-incoming
            :allowed_param: 'cursor'
        """
        return bind_api(
            self, 'GET', 'friendships/incoming', *args,
            allowed_param=['cursor'], **kwargs
        )

    @pagination(mode='cursor')
    @payload('ids')
    def friendships_outgoing(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-friendships-outgoing
            :allowed_param: 'cursor'
        """
        return bind_api(
            self, 'GET', 'friendships/outgoing', *args,
            allowed_param=['cursor'], **kwargs
        )

    @pagination(mode='cursor')
    @payload('ids')
    def followers_ids(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-followers-ids
            :allowed_param: 'id', 'user_id', 'screen_name', 'cursor', 'count'
        """
        return bind_api(
            self, 'GET', 'followers/ids', *args,
            allowed_param=['id', 'user_id', 'screen_name', 'cursor', 'count'],
            **kwargs
        )

    @pagination(mode='cursor')
    @payload('user', list=True)
    def followers(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-followers-list
            :allowed_param: 'id', 'user_id', 'screen_name', 'cursor', 'count',
                            'skip_status', 'include_user_entities'
        """
        return bind_api(
            self, 'GET', 'followers/list', *args,
            allowed_param=['id', 'user_id', 'screen_name', 'cursor', 'count',
                           'skip_status', 'include_user_entities'], **kwargs
        )

    @payload('json')
    def get_settings(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/manage-account-settings/api-reference/get-account-settings """
        return bind_api(
            self, 'GET', 'account/settings', *args,
            use_cache=False, **kwargs
        )

    @payload('json')
    def set_settings(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/manage-account-settings/api-reference/post-account-settings
            :allowed_param: 'sleep_time_enabled', 'start_sleep_time',
                            'end_sleep_time', 'time_zone',
                            'trend_location_woeid',
                            'allow_contributor_request', 'lang'
        """
        return bind_api(
            self, 'POST', 'account/settings', *args,
            allowed_param=['sleep_time_enabled', 'start_sleep_time',
                           'end_sleep_time', 'time_zone',
                           'trend_location_woeid',
                           'allow_contributor_request', 'lang'],
            use_cache=False, **kwargs
        )

    @payload('user')
    def verify_credentials(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/manage-account-settings/api-reference/get-account-verify_credentials
            :allowed_param: 'include_entities', 'skip_status', 'include_email'
        """
        if 'include_email' in kwargs:
            kwargs['include_email'] = str(kwargs['include_email']).lower()
        try:
            return bind_api(
                self, 'GET', 'account/verify_credentials',
                require_auth=True,
                allowed_param=['include_entities', 'skip_status',
                               'include_email'], **kwargs
            )
        except TweepError as e:
            if e.response is not None and e.response.status_code == 401:
                return False
            raise

    @payload('json')
    def rate_limit_status(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/developer-utilities/rate-limit-status/api-reference/get-application-rate_limit_status
            :allowed_param: 'resources'
        """
        return bind_api(
            self, 'GET', 'application/rate_limit_status', *args,
            allowed_param=['resources'],
            use_cache=False, **kwargs
        )

    @payload('user')
    def update_profile_image(self, filename, file_=None, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/manage-account-settings/api-reference/post-account-update_profile_image
            :allowed_param: 'include_entities', 'skip_status'
        """
        headers, post_data = API._pack_image(filename, 700, f=file_)
        return bind_api(
            self, 'POST', 'account/update_profile_image', *args,
            allowed_param=['include_entities', 'skip_status'],
            require_auth=True,
            post_data=post_data, headers=headers, **kwargs
        )

    def update_profile_banner(self, filename, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/manage-account-settings/api-reference/post-account-update_profile_banner
            :allowed_param: 'width', 'height', 'offset_left', 'offset_right'
        """
        f = kwargs.pop('file', None)
        headers, post_data = API._pack_image(filename, 700,
                                             form_field='banner', f=f)
        return bind_api(
            self, 'POST', 'account/update_profile_banner',
            allowed_param=['width', 'height', 'offset_left', 'offset_right'],
            require_auth=True,
            post_data=post_data, headers=headers
        )

    @payload('user')
    def update_profile(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/manage-account-settings/api-reference/post-account-update_profile
            :allowed_param: 'name', 'url', 'location', 'description',
                            'profile_link_color'
        """
        return bind_api(
            self, 'POST', 'account/update_profile', *args,
            allowed_param=['name', 'url', 'location', 'description',
                           'profile_link_color'],
            require_auth=True, **kwargs
        )

    @pagination(mode='id')
    @payload('status', list=True)
    def favorites(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/get-favorites-list
            :allowed_param: 'screen_name', 'user_id', 'max_id', 'count',
                            'since_id'
        """
        return bind_api(
            self, 'GET', 'favorites/list', *args,
            allowed_param=['screen_name', 'user_id', 'max_id', 'count',
                           'since_id'], **kwargs
        )

    @payload('status')
    def create_favorite(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/post-favorites-create
            :allowed_param: 'id'
        """
        return bind_api(
            self, 'POST', 'favorites/create', *args,
            allowed_param=['id'],
            require_auth=True, **kwargs
        )

    @payload('status')
    def destroy_favorite(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/post-favorites-destroy
            :allowed_param: 'id'
        """
        return bind_api(
            self, 'POST', 'favorites/destroy', *args,
            allowed_param=['id'],
            require_auth=True, **kwargs
        )

    @payload('user')
    def create_block(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/mute-block-report-users/api-reference/post-blocks-create
            :allowed_param: 'id', 'user_id', 'screen_name'
        """
        return bind_api(
            self, 'POST', 'blocks/create', *args,
            allowed_param=['id', 'user_id', 'screen_name'],
            require_auth=True, **kwargs
        )

    @payload('user')
    def destroy_block(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/mute-block-report-users/api-reference/post-blocks-destroy
            :allowed_param: 'id', 'user_id', 'screen_name'
        """
        return bind_api(
            self, 'POST', 'blocks/destroy', *args,
            allowed_param=['id', 'user_id', 'screen_name'],
            require_auth=True, **kwargs
        )

    @pagination(mode='cursor')
    @payload('ids')
    def mutes_ids(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/mute-block-report-users/api-reference/get-mutes-users-ids
            :allowed_param: 'cursor'
        """
        return bind_api(
            self, 'GET', 'mutes/users/ids', *args,
            allowed_param=['cursor'],
            require_auth=True, **kwargs
        )

    @pagination(mode='cursor')
    @payload('user', list=True)
    def mutes(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/mute-block-report-users/api-reference/get-mutes-users-list
            :allowed_param: 'cursor', 'include_entities', 'skip_status'
        """
        return bind_api(
            self, 'GET', 'mutes/users/list', *args,
            allowed_param=['cursor', 'include_entities', 'skip_status'],
            required_auth=True, **kwargs
        )

    @payload('user')
    def create_mute(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/mute-block-report-users/api-reference/post-mutes-users-create
            :allowed_param: 'id', 'user_id', 'screen_name'
        """
        return bind_api(
            self, 'POST', 'mutes/users/create', *args,
            allowed_param=['id', 'user_id', 'screen_name'],
            require_auth=True, **kwargs
        )

    @payload('user')
    def destroy_mute(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/mute-block-report-users/api-reference/post-mutes-users-destroy
            :allowed_param: 'id', 'user_id', 'screen_name'
        """
        return bind_api(
            self, 'POST', 'mutes/users/destroy', *args,
            allowed_param=['id', 'user_id', 'screen_name'],
            require_auth=True, **kwargs
        )

    @pagination(mode='cursor')
    @payload('user', list=True)
    def blocks(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/mute-block-report-users/api-reference/get-blocks-list
            :allowed_param: 'cursor'
        """
        return bind_api(
            self, 'GET', 'blocks/list', *args,
            allowed_param=['cursor'],
            require_auth=True, **kwargs
        )

    @pagination(mode='cursor')
    @payload('ids')
    def blocks_ids(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/mute-block-report-users/api-reference/get-blocks-ids
            :allowed_param: 'cursor'
        """
        return bind_api(
            self, 'GET', 'blocks/ids', *args,
            allowed_param=['cursor'],
            require_auth=True, **kwargs
        )

    @payload('user')
    def report_spam(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/mute-block-report-users/api-reference/post-users-report_spam
            :allowed_param: 'user_id', 'screen_name', 'perform_block'
        """
        return bind_api(
            self, 'POST', 'users/report_spam', *args,
            allowed_param=['user_id', 'screen_name', 'perform_block'],
            require_auth=True, **kwargs
        )

    @payload('saved_search', list=True)
    def saved_searches(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/manage-account-settings/api-reference/get-saved_searches-list """
        return bind_api(
            self, 'GET', 'saved_searches/list', *args,
            require_auth=True, **kwargs
        )

    @payload('saved_search')
    def get_saved_search(self, saved_search_id, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/manage-account-settings/api-reference/get-saved_searches-show-id
            :allowed_param:
        """
        return bind_api(
            self, 'GET', f'saved_searches/show/{saved_search_id}', *args,
            require_auth=True, **kwargs
        )

    @payload('saved_search')
    def create_saved_search(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/manage-account-settings/api-reference/post-saved_searches-create
            :allowed_param: 'query'
        """
        return bind_api(
            self, 'POST', 'saved_searches/create', *args,
            allowed_param=['query'],
            require_auth=True, **kwargs
        )

    @payload('saved_search')
    def destroy_saved_search(self, saved_search_id, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/manage-account-settings/api-reference/post-saved_searches-destroy-id
            :allowed_param:
        """
        return bind_api(
            self, 'POST', f'saved_searches/destroy/{saved_search_id}',
            *args,
            require_auth=True, **kwargs
        )

    @payload('list')
    def create_list(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/post-lists-create
            :allowed_param: 'name', 'mode', 'description'
        """
        return bind_api(
            self, 'POST', 'lists/create', *args,
            allowed_param=['name', 'mode', 'description'],
            require_auth=True, **kwargs
        )

    @payload('list')
    def destroy_list(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/post-lists-destroy
            :allowed_param: 'owner_screen_name', 'owner_id', 'list_id', 'slug'
        """
        return bind_api(
            self, 'POST', 'lists/destroy', *args,
            allowed_param=['owner_screen_name', 'owner_id', 'list_id', 'slug'],
            require_auth=True, **kwargs
        )

    @payload('list')
    def update_list(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/post-lists-update
            :allowed_param: 'list_id', 'slug', 'name', 'mode', 'description',
                            'owner_screen_name', 'owner_id'
        """
        return bind_api(
            self, 'POST', 'lists/update', *args,
            allowed_param=['list_id', 'slug', 'name', 'mode', 'description',
                           'owner_screen_name', 'owner_id'],
            require_auth=True, **kwargs
        )

    @payload('list', list=True)
    def lists_all(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/get-lists-list
            :allowed_param: 'screen_name', 'user_id', 'reverse'
        """
        return bind_api(
            self, 'GET', 'lists/list', *args,
            allowed_param=['screen_name', 'user_id', 'reverse'],
            require_auth=True, **kwargs
        )

    @pagination(mode='cursor')
    @payload('list', list=True)
    def lists_memberships(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/get-lists-memberships
            :allowed_param: 'screen_name', 'user_id', 'filter_to_owned_lists',
                            'cursor', 'count'
        """
        return bind_api(
            self, 'GET', 'lists/memberships', *args,
            allowed_param=['screen_name', 'user_id', 'filter_to_owned_lists',
                           'cursor', 'count'],
            require_auth=True, **kwargs
        )

    @pagination(mode='cursor')
    @payload('list', list=True)
    def lists_ownerships(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/get-lists-ownerships
            :allowed_param: 'user_id', 'screen_name', 'count', 'cursor'
        """
        return bind_api(
            self, 'GET', 'lists/ownerships', *args,
            allowed_param=['user_id', 'screen_name', 'count', 'cursor'],
            require_auth=True, **kwargs
        )

    @pagination(mode='cursor')
    @payload('list', list=True)
    def lists_subscriptions(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/get-lists-subscriptions
            :allowed_param: 'screen_name', 'user_id', 'cursor', 'count'
        """
        return bind_api(
            self, 'GET', 'lists/subscriptions', *args,
            allowed_param=['screen_name', 'user_id', 'cursor', 'count'],
            require_auth=True, **kwargs
        )

    @pagination(mode='id')
    @payload('status', list=True)
    def list_timeline(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/get-lists-statuses
            :allowed_param: 'owner_screen_name', 'slug', 'owner_id', 'list_id',
                            'since_id', 'max_id', 'count', 'include_entities',
                            'include_rts'
        """
        return bind_api(
            self, 'GET', 'lists/statuses', *args,
            allowed_param=['owner_screen_name', 'slug', 'owner_id', 'list_id',
                           'since_id', 'max_id', 'count', 'include_entities',
                           'include_rts'], **kwargs
        )

    @payload('list')
    def get_list(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/get-lists-show
            :allowed_param: 'owner_screen_name', 'owner_id', 'slug', 'list_id'
        """
        return bind_api(
            self, 'GET', 'lists/show', *args,
            allowed_param=['owner_screen_name', 'owner_id', 'slug', 'list_id'],
            **kwargs
        )

    @payload('list')
    def add_list_member(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/post-lists-members-create
            :allowed_param: 'screen_name', 'user_id', 'owner_screen_name',
                            'owner_id', 'slug', 'list_id'
        """
        return bind_api(
            self, 'POST', 'lists/members/create', *args,
            allowed_param=['screen_name', 'user_id', 'owner_screen_name',
                           'owner_id', 'slug', 'list_id'],
            require_auth=True, **kwargs
        )

    @payload('list')
    def remove_list_member(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/post-lists-members-destroy
            :allowed_param: 'screen_name', 'user_id', 'owner_screen_name',
                            'owner_id', 'slug', 'list_id'
        """
        return bind_api(
            self, 'POST', 'lists/members/destroy', *args,
            allowed_param=['screen_name', 'user_id', 'owner_screen_name',
                           'owner_id', 'slug', 'list_id'],
            require_auth=True, **kwargs
        )

    @payload('list')
    def add_list_members(self, screen_name=None, user_id=None, slug=None,
                         list_id=None, owner_id=None, owner_screen_name=None,
                         **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/post-lists-members-create_all
            :allowed_param: 'screen_name', 'user_id', 'slug', 'list_id',
                            'owner_id', 'owner_screen_name'
        """
        return bind_api(
            self, 'POST', 'lists/members/create_all',
            list_to_csv(screen_name), list_to_csv(user_id), slug, list_id,
            owner_id, owner_screen_name,
            allowed_param=['screen_name', 'user_id', 'slug', 'list_id',
                           'owner_id', 'owner_screen_name'],
            require_auth=True, **kwargs
        )

    @payload('list')
    def remove_list_members(self, screen_name=None, user_id=None, slug=None,
                            list_id=None, owner_id=None,
                            owner_screen_name=None, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/post-lists-members-destroy_all
            :allowed_param: 'screen_name', 'user_id', 'slug', 'list_id',
                            'owner_id', 'owner_screen_name'
        """
        return bind_api(
            self, 'POST', 'lists/members/destroy_all',
            list_to_csv(screen_name), list_to_csv(user_id), slug, list_id,
            owner_id, owner_screen_name,
            allowed_param=['screen_name', 'user_id', 'slug', 'list_id',
                           'owner_id', 'owner_screen_name'],
            require_auth=True, **kwargs
        )

    @pagination(mode='cursor')
    @payload('user', list=True)
    def list_members(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/get-lists-members
            :allowed_param: 'owner_screen_name', 'slug', 'list_id', 'owner_id',
                            'cursor'
        """
        return bind_api(
            self, 'GET', 'lists/members', *args,
            allowed_param=['owner_screen_name', 'slug', 'list_id', 'owner_id',
                           'cursor'], **kwargs
        )

    @payload('user')
    def show_list_member(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/get-lists-members-show
            :allowed_param: 'list_id', 'slug', 'user_id', 'screen_name',
                            'owner_screen_name', 'owner_id'
        """
        return bind_api(
            self, 'GET', 'lists/members/show', *args,
            allowed_param=['list_id', 'slug', 'user_id', 'screen_name',
                           'owner_screen_name', 'owner_id'], **kwargs
        )

    @payload('list')
    def subscribe_list(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/post-lists-subscribers-create
            :allowed_param: 'owner_screen_name', 'slug', 'owner_id', 'list_id'
        """
        return bind_api(
            self, 'POST', 'lists/subscribers/create', *args,
            allowed_param=['owner_screen_name', 'slug', 'owner_id', 'list_id'],
            require_auth=True, **kwargs
        )

    @payload('list')
    def unsubscribe_list(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/post-lists-subscribers-destroy
            :allowed_param: 'owner_screen_name', 'slug', 'owner_id', 'list_id'
        """
        return bind_api(
            self, 'POST', 'lists/subscribers/destroy', *args,
            allowed_param=['owner_screen_name', 'slug', 'owner_id', 'list_id'],
            require_auth=True, **kwargs
        )

    @pagination(mode='cursor')
    @payload('user', list=True)
    def list_subscribers(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/get-lists-subscribers
            :allowed_param: 'owner_screen_name', 'slug', 'owner_id', 'list_id',
                            'cursor', 'count', 'include_entities',
                            'skip_status'
        """
        return bind_api(
            self, 'GET', 'lists/subscribers', *args,
            allowed_param=['owner_screen_name', 'slug', 'owner_id', 'list_id',
                           'cursor', 'count', 'include_entities',
                           'skip_status'], **kwargs
        )

    @payload('user')
    def show_list_subscriber(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/get-lists-subscribers-show
            :allowed_param: 'owner_screen_name', 'slug', 'screen_name',
                            'owner_id', 'list_id', 'user_id'
        """
        return bind_api(
            self, 'GET', 'lists/subscribers/show', *args,
            allowed_param=['owner_screen_name', 'slug', 'screen_name',
                           'owner_id', 'list_id', 'user_id'], **kwargs
        )

    @payload('json')
    def trends_available(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/trends/locations-with-trending-topics/api-reference/get-trends-available """
        return bind_api(self, 'GET', 'trends/available', *args, **kwargs)

    @payload('json')
    def trends_place(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/trends/trends-for-location/api-reference/get-trends-place
            :allowed_param: 'id', 'exclude'
        """
        return bind_api(
            self, 'GET', 'trends/place', *args,
            allowed_param=['id', 'exclude'], **kwargs
        )

    @payload('json')
    def trends_closest(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/trends/locations-with-trending-topics/api-reference/get-trends-closest
            :allowed_param: 'lat', 'long'
        """
        return bind_api(
            self, 'GET', 'trends/closest', *args,
            allowed_param=['lat', 'long'], **kwargs
        )

    @pagination(mode='id')
    @payload('search_results')
    def search(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/search/api-reference/get-search-tweets
            :allowed_param: 'q', 'lang', 'locale', 'since_id', 'geocode',
                            'max_id', 'until', 'result_type', 'count',
                            'include_entities'
        """
        return bind_api(
            self, 'GET', 'search/tweets', *args,
            allowed_param=['q', 'lang', 'locale', 'since_id', 'geocode',
                           'max_id', 'until', 'result_type', 'count',
                           'include_entities'], **kwargs
        )

    @pagination(mode='next')
    @payload('status', list=True)
    def search_30_day(self, environment_name, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/search/api-reference/premium-search
            :allowed_param: 'query', 'tag', 'fromDate', 'toDate', 'maxResults',
                            'next'
        """
        return bind_api(
            self, 'GET', f'tweets/search/30day/{environment_name}',
            *args,
            allowed_param=['query', 'tag', 'fromDate', 'toDate', 'maxResults',
                           'next'],
            require_auth=True, **kwargs
        )

    @pagination(mode='next')
    @payload('status', list=True)
    def search_full_archive(self, environment_name, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/search/api-reference/premium-search
            :allowed_param: 'query', 'tag', 'fromDate', 'toDate', 'maxResults',
                            'next'
        """
        return bind_api(
            self, 'GET', f'tweets/search/fullarchive/{environment_name}',
            *args,
            allowed_param=['query', 'tag', 'fromDate', 'toDate', 'maxResults',
                           'next'],
            require_auth=True, **kwargs
        )

    @payload('place', list=True)
    def reverse_geocode(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/geo/places-near-location/api-reference/get-geo-reverse_geocode
            :allowed_param: 'lat', 'long', 'accuracy', 'granularity',
                            'max_results'
        """
        return bind_api(
            self, 'GET', 'geo/reverse_geocode', *args,
            allowed_param=['lat', 'long', 'accuracy', 'granularity',
                           'max_results'], **kwargs
        )

    @payload('place')
    def geo_id(self, place_id, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/geo/place-information/api-reference/get-geo-id-place_id
            :allowed_param:
        """
        return bind_api(
            self, 'GET', f'geo/id/{place_id}', *args, **kwargs
        )

    @payload('place', list=True)
    def geo_search(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/geo/places-near-location/api-reference/get-geo-search
            :allowed_param: 'lat', 'long', 'query', 'ip', 'granularity',
                            'accuracy', 'max_results', 'contained_within'

        """
        return bind_api(
            self, 'GET', 'geo/search', *args,
            allowed_param=['lat', 'long', 'query', 'ip', 'granularity',
                           'accuracy', 'max_results', 'contained_within'],
            **kwargs
        )

    @payload('json')
    def supported_languages(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/developer-utilities/supported-languages/api-reference/get-help-languages """
        return bind_api(
            self, 'GET', 'help/languages', *args,
            require_auth=True, **kwargs
        )

    @payload('json')
    def configuration(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/developer-utilities/configuration/api-reference/get-help-configuration """
        return bind_api(
            self, 'GET', 'help/configuration', *args,
            require_auth=True, **kwargs
        )

    """ Internal use only """

    @staticmethod
    def _pack_image(filename, max_size, form_field='image', f=None, file_type=None):
        """Pack image from file into multipart-formdata post body"""
        # image must be less than 700kb in size
        if f is None:
            try:
                if os.path.getsize(filename) > (max_size * 1024):
                    raise TweepError(f'File is too big, must be less than {max_size}kb.')
            except os.error as e:
                raise TweepError(f'Unable to access file: {e.strerror}')

            # build the mulitpart-formdata body
            fp = open(filename, 'rb')
        else:
            f.seek(0, 2)  # Seek to end of file
            if f.tell() > (max_size * 1024):
                raise TweepError(f'File is too big, must be less than {max_size}kb.')
            f.seek(0)  # Reset to beginning of file
            fp = f

        # image must be gif, jpeg, png, webp
        if not file_type:
            h = None
            if f is not None:
                h = f.read(32)
                f.seek(0)
            file_type = imghdr.what(filename, h=h) or mimetypes.guess_type(filename)[0]
        if file_type is None:
            raise TweepError('Could not determine file type')
        if file_type in ['gif', 'jpeg', 'png', 'webp']:
            file_type = 'image/' + file_type
        elif file_type not in ['image/gif', 'image/jpeg', 'image/png']:
            raise TweepError(f'Invalid file type for image: {file_type}')

        if isinstance(filename, str):
            filename = filename.encode('utf-8')

        BOUNDARY = b'Tw3ePy'
        body = []
        body.append(b'--' + BOUNDARY)
        body.append(f'Content-Disposition: form-data; name="{form_field}";'
                    f' filename="{filename}"'
                    .encode('utf-8'))
        body.append(f'Content-Type: {file_type}'.encode('utf-8'))
        body.append(b'')
        body.append(fp.read())
        body.append(b'--' + BOUNDARY + b'--')
        body.append(b'')
        fp.close()
        body = b'\r\n'.join(body)

        # build headers
        headers = {
            'Content-Type': 'multipart/form-data; boundary=Tw3ePy',
            'Content-Length': str(len(body))
        }

        return headers, body
