# Tweepy
# Copyright 2009-2021 Joshua Roesslein
# See LICENSE for details.

import imghdr
import logging
import mimetypes
import os
import sys
import time
from urllib.parse import urlencode

import requests

from tweepy.error import is_rate_limit_error_message, RateLimitError, TweepError
from tweepy.models import Model
from tweepy.parsers import ModelParser, Parser
from tweepy.utils import list_to_csv

log = logging.getLogger(__name__)


def pagination(mode):
    def decorator(method):
        method.pagination_mode = mode
        return method
    return decorator


def payload(payload_type, **payload_kwargs):
    payload_list = payload_kwargs.get('list', False)
    def decorator(method):
        def wrapper(*args, **kwargs):
            kwargs['payload_list'] = payload_list
            kwargs['payload_type'] = payload_type
            return method(*args, **kwargs)
        wrapper.payload_list = payload_list
        wrapper.payload_type = payload_type
        return wrapper
    return decorator


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

        self.session = requests.Session()

    def request(
        self, method, endpoint, *args, endpoint_parameters=(), params=None,
        headers=None, json_payload=None, parser=None, payload_list=False,
        payload_type=None, post_data=None, require_auth=True,
        return_cursors=False, upload_api=False, use_cache=True, **kwargs
    ):
        # If authentication is required and no credentials
        # are provided, throw an error.
        if require_auth and not self.auth:
            raise TweepError('Authentication required!')

        self.cached_result = False

        # Build the request URL
        path = f'/1.1/{endpoint}.json'
        if upload_api:
            url = 'https://' + self.upload_host + path
        else:
            url = 'https://' + self.host + path

        if params is None:
            params = {}

        for idx, arg in enumerate(args):
            if arg is None:
                continue
            try:
                params[endpoint_parameters[idx]] = str(arg)
            except IndexError:
                raise TweepError('Too many parameters supplied!')

        for k, arg in kwargs.items():
            if arg is None:
                continue
            if k in params:
                raise TweepError(f'Multiple values for parameter {k} supplied!')
            if k not in endpoint_parameters:
                log.warning(f'Unexpected parameter: {k}')
            params[k] = str(arg)

        log.debug("PARAMS: %r", params)

        # Query the cache if one is available
        # and this request uses a GET method.
        if use_cache and self.cache and method == 'GET':
            cache_result = self.cache.get(f'{path}?{urlencode(params)}')
            # if cache result found and not expired, return it
            if cache_result:
                # must restore api reference
                if isinstance(cache_result, list):
                    for result in cache_result:
                        if isinstance(result, Model):
                            result._api = self
                else:
                    if isinstance(cache_result, Model):
                        cache_result._api = self
                self.cached_result = True
                return cache_result

        # Monitoring rate limits
        remaining_calls = None
        reset_time = None

        if parser is None:
            parser = self.parser

        try:
            # Continue attempting request until successful
            # or maximum number of retries is reached.
            retries_performed = 0
            while retries_performed <= self.retry_count:
                if (self.wait_on_rate_limit and reset_time is not None
                    and remaining_calls is not None
                    and remaining_calls < 1):
                    # Handle running out of API calls
                    sleep_time = reset_time - int(time.time())
                    if sleep_time > 0:
                        log.warning(f"Rate limit reached. Sleeping for: {sleep_time}")
                        time.sleep(sleep_time + 1)  # Sleep for extra sec

                # Apply authentication
                auth = None
                if self.auth:
                    auth = self.auth.apply_auth()

                # Execute request
                try:
                    resp = self.session.request(
                        method, url, params=params, headers=headers,
                        data=post_data, json=json_payload, timeout=self.timeout,
                        auth=auth, proxies=self.proxy
                    )
                except Exception as e:
                    raise TweepError(f'Failed to send request: {e}').with_traceback(sys.exc_info()[2])

                if 200 <= resp.status_code < 300:
                    break

                rem_calls = resp.headers.get('x-rate-limit-remaining')
                if rem_calls is not None:
                    remaining_calls = int(rem_calls)
                elif remaining_calls is not None:
                    remaining_calls -= 1

                reset_time = resp.headers.get('x-rate-limit-reset')
                if reset_time is not None:
                    reset_time = int(reset_time)

                retry_delay = self.retry_delay
                if resp.status_code in (420, 429) and self.wait_on_rate_limit:
                    if remaining_calls == 0:
                        # If ran out of calls before waiting switching retry last call
                        continue
                    if 'retry-after' in resp.headers:
                        retry_delay = float(resp.headers['retry-after'])
                elif self.retry_errors and resp.status_code not in self.retry_errors:
                    # Exit request loop if non-retry error code
                    break

                # Sleep before retrying request again
                time.sleep(retry_delay)
                retries_performed += 1

            # If an error was returned, throw an exception
            self.last_response = resp
            if resp.status_code and not 200 <= resp.status_code < 300:
                try:
                    error_msg, api_error_code = parser.parse_error(resp.text)
                except Exception:
                    error_msg = f"Twitter error response: status code = {resp.status_code}"
                    api_error_code = None

                if is_rate_limit_error_message(error_msg):
                    raise RateLimitError(error_msg, resp)
                else:
                    raise TweepError(error_msg, resp, api_code=api_error_code)

            # Parse the response payload
            return_cursors = return_cursors or 'cursor' in params or 'next' in params
            result = parser.parse(
                resp.text, api=self, payload_list=payload_list,
                payload_type=payload_type, return_cursors=return_cursors
            )

            # Store result into cache if one is available.
            if use_cache and self.cache and method == 'GET' and result:
                self.cache.store(f'{path}?{urlencode(params)}', result)

            return result
        finally:
            self.session.close()

    @pagination(mode='id')
    @payload('status', list=True)
    def home_timeline(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/timelines/api-reference/get-statuses-home_timeline
        """
        return self.request(
            'GET', 'statuses/home_timeline', endpoint_parameters=(
                'count', 'since_id', 'max_id', 'trim_user', 'exclude_replies',
                'include_entities'
            ), **kwargs
        )

    @payload('status', list=True)
    def statuses_lookup(self, id, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/get-statuses-lookup
        """
        return self.request(
            'GET', 'statuses/lookup', list_to_csv(id), endpoint_parameters=(
                'id', 'include_entities', 'trim_user', 'map',
                'include_ext_alt_text', 'include_card_uri'
            ), **kwargs
        )

    @pagination(mode='id')
    @payload('status', list=True)
    def user_timeline(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/timelines/api-reference/get-statuses-user_timeline
        """
        return self.request(
            'GET', 'statuses/user_timeline', endpoint_parameters=(
                'user_id', 'screen_name', 'since_id', 'count', 'max_id',
                'trim_user', 'exclude_replies', 'include_rts'
            ), **kwargs
        )

    @pagination(mode='id')
    @payload('status', list=True)
    def mentions_timeline(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/timelines/api-reference/get-statuses-mentions_timeline
        """
        return self.request(
            'GET', 'statuses/mentions_timeline', endpoint_parameters=(
                'count', 'since_id', 'max_id', 'trim_user', 'include_entities'
            ), **kwargs
        )

    @pagination(mode='id')
    @payload('status', list=True)
    def retweets_of_me(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/get-statuses-retweets_of_me
        """
        return self.request(
            'GET', 'statuses/retweets_of_me', endpoint_parameters=(
                'count', 'since_id', 'max_id', 'trim_user', 'include_entities',
                'include_user_entities'
            ), **kwargs
        )

    @payload('status')
    def get_status(self, id, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/get-statuses-show-id
        """
        return self.request(
            'GET', 'statuses/show', id, endpoint_parameters=(
                'id', 'trim_user', 'include_my_retweet', 'include_entities',
                'include_ext_alt_text', 'include_card_uri'
            ), **kwargs
        )

    @payload('status')
    def update_status(self, status, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/post-statuses-update
        """
        if 'media_ids' in kwargs:
            kwargs['media_ids'] = list_to_csv(kwargs['media_ids'])

        return self.request(
            'POST', 'statuses/update', status, endpoint_parameters=(
                'status', 'in_reply_to_status_id',
                'auto_populate_reply_metadata', 'exclude_reply_user_ids',
                'attachment_url', 'media_ids', 'possibly_sensitive', 'lat',
                'long', 'place_id', 'display_coordinates', 'trim_user',
                'enable_dmcommands', 'fail_dmcommands', 'card_uri'
            ), **kwargs
        )

    @payload('media')
    def media_upload(self, filename, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/media/upload-media/api-reference/post-media-upload
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

        return self.request(
            'POST', 'media/upload', *args,
            endpoint_parameters=(),
            upload_api=True, **kwargs
        )

    def create_media_metadata(self, media_id, alt_text, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/media/upload-media/api-reference/post-media-metadata-create
        """
        json_payload = {
            'media_id': media_id,
            'alt_text': {'text': alt_text}
        }

        return self.request(
            'POST', 'media/metadata/create', json_payload=json_payload,
            upload_api=True, **kwargs
        )

    @payload('status')
    def update_with_media(self, filename, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/post-statuses-update_with_media
        """
        f = kwargs.pop('file', None)
        headers, post_data = API._pack_image(filename, 3072,
                                             form_field='media[]', f=f)
        kwargs.update({'headers': headers, 'post_data': post_data})

        return self.request(
            'POST', 'statuses/update_with_media', *args, endpoint_parameters=(
                'status', 'possibly_sensitive', 'in_reply_to_status_id',
                'in_reply_to_status_id_str', 'auto_populate_reply_metadata',
                'lat', 'long', 'place_id', 'display_coordinates'
            ), **kwargs
        )

    @payload('status')
    def destroy_status(self, id, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/post-statuses-destroy-id
        """
        return self.request(
            'POST', f'statuses/destroy/{id}', endpoint_parameters=(
                'trim_user',
            ), **kwargs
        )

    @payload('status')
    def retweet(self, id, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/post-statuses-retweet-id
        """
        return self.request(
            'POST', f'statuses/retweet/{id}', endpoint_parameters=(
                'trim_user',
            ), **kwargs
        )

    @payload('status')
    def unretweet(self, id, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/post-statuses-unretweet-id
        """
        return self.request(
            'POST', f'statuses/unretweet/{id}', endpoint_parameters=(
                'trim_user',
            ), **kwargs
        )

    @payload('status', list=True)
    def retweets(self, id, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/get-statuses-retweets-id
        """
        return self.request(
            'GET', f'statuses/retweets/{id}', endpoint_parameters=(
                'count', 'trim_user'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('ids')
    def retweeters(self, id, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/get-statuses-retweeters-ids
        """
        return self.request(
            'GET', 'statuses/retweeters/ids', id, endpoint_parameters=(
                'id', 'count', 'cursor', 'stringify_ids'
            ), **kwargs
        )

    @payload('user')
    def get_user(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-users-show
        """
        return self.request(
            'GET', 'users/show', endpoint_parameters=(
                'user_id', 'screen_name', 'include_entities'
            ), **kwargs
        )

    @payload('json')
    def get_oembed(self, url, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/get-statuses-oembed
        """
        return self.request(
            'GET', 'statuses/oembed', url, endpoint_parameters=(
                'url', 'maxwidth', 'hide_media', 'hide_thread', 'omit_script',
                'align', 'related', 'lang', 'theme', 'link_color',
                'widget_type', 'dnt'
            ), require_auth=False, **kwargs
        )

    @payload('user', list=True)
    def lookup_users(self, *, screen_name=None, user_id=None, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-users-lookup
        """
        return self.request(
            'POST', 'users/lookup', list_to_csv(screen_name),
            list_to_csv(user_id), endpoint_parameters=(
                'screen_name', 'user_id', 'include_entities', 'tweet_mode'
            ), **kwargs
        )

    def me(self):
        """ Get the authenticated user """
        return self.get_user(screen_name=self.auth.get_username())

    @pagination(mode='page')
    @payload('user', list=True)
    def search_users(self, q, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-users-search
        """
        return self.request(
            'GET', 'users/search', q, endpoint_parameters=(
                'q', 'page', 'count', 'include_entities'
            ), **kwargs
        )

    @payload('direct_message')
    def get_direct_message(self, id, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/direct-messages/sending-and-receiving/api-reference/get-event
        """
        return self.request(
            'GET', 'direct_messages/events/show', id, endpoint_parameters=(
                'id',
            ), **kwargs
        )

    @pagination(mode='dm_cursor')
    @payload('direct_message', list=True)
    def list_direct_messages(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/direct-messages/sending-and-receiving/api-reference/list-events
        """
        return self.request(
            'GET', 'direct_messages/events/list', endpoint_parameters=(
                'count', 'cursor'
            ), **kwargs
        )

    @payload('direct_message')
    def send_direct_message(self, recipient_id, text, *, quick_reply_options=None,
                            attachment_type=None, attachment_media_id=None,
                            ctas=None, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/direct-messages/sending-and-receiving/api-reference/new-event
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
        return self.request(
            'POST', 'direct_messages/events/new',
            json_payload=json_payload, **kwargs
        )

    def destroy_direct_message(self, id, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/direct-messages/sending-and-receiving/api-reference/delete-message-event
        """
        return self.request(
            'DELETE', 'direct_messages/events/destroy', id,
            endpoint_parameters=(
                'id',
            ), **kwargs
        )

    @payload('user')
    def create_friendship(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/post-friendships-create
        """
        return self.request(
            'POST', 'friendships/create', endpoint_parameters=(
                'screen_name', 'user_id', 'follow'
            ), **kwargs
        )

    @payload('user')
    def destroy_friendship(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/post-friendships-destroy
        """
        return self.request(
            'POST', 'friendships/destroy', endpoint_parameters=(
                'screen_name', 'user_id'
            ), **kwargs
        )

    @payload('friendship')
    def show_friendship(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-friendships-show
        """
        return self.request(
            'GET', 'friendships/show', endpoint_parameters=(
                'source_id', 'source_screen_name', 'target_id',
                'target_screen_name'
            ), **kwargs
        )

    @payload('relationship', list=True)
    def lookup_friendships(self, *, screen_name=None, user_id=None, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-friendships-lookup
        """
        return self.request(
            'GET', 'friendships/lookup', list_to_csv(screen_name),
            list_to_csv(user_id), endpoint_parameters=(
                'screen_name', 'user_id'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('ids')
    def friends_ids(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-friends-ids
        """
        return self.request(
            'GET', 'friends/ids', endpoint_parameters=(
                'user_id', 'screen_name', 'cursor', 'stringify_ids', 'count'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('user', list=True)
    def friends(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-friends-list
        """
        return self.request(
            'GET', 'friends/list', endpoint_parameters=(
                'user_id', 'screen_name', 'cursor', 'count', 'skip_status',
                'include_user_entities'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('ids')
    def friendships_incoming(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-friendships-incoming
        """
        return self.request(
            'GET', 'friendships/incoming', endpoint_parameters=(
                'cursor', 'stringify_ids'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('ids')
    def friendships_outgoing(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-friendships-outgoing
        """
        return self.request(
            'GET', 'friendships/outgoing', endpoint_parameters=(
                'cursor', 'stringify_ids'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('ids')
    def followers_ids(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-followers-ids
        """
        return self.request(
            'GET', 'followers/ids', endpoint_parameters=(
                'user_id', 'screen_name', 'cursor', 'count'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('user', list=True)
    def followers(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-followers-list
        """
        return self.request(
            'GET', 'followers/list', endpoint_parameters=(
                'user_id', 'screen_name', 'cursor', 'count', 'skip_status',
                'include_user_entities'
            ), **kwargs
        )

    @payload('json')
    def get_settings(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/manage-account-settings/api-reference/get-account-settings
        """
        return self.request(
            'GET', 'account/settings', use_cache=False, **kwargs
        )

    @payload('json')
    def set_settings(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/manage-account-settings/api-reference/post-account-settings
        """
        return self.request(
            'POST', 'account/settings', endpoint_parameters=(
                'sleep_time_enabled', 'start_sleep_time', 'end_sleep_time',
                'time_zone', 'trend_location_woeid', 'lang'
            ), use_cache=False, **kwargs
        )

    @payload('user')
    def verify_credentials(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/manage-account-settings/api-reference/get-account-verify_credentials
        """
        if 'include_email' in kwargs:
            kwargs['include_email'] = str(kwargs['include_email']).lower()
        return self.request(
            'GET', 'account/verify_credentials', endpoint_parameters=(
                'include_entities', 'skip_status', 'include_email'
            ), **kwargs
        )

    @payload('json')
    def rate_limit_status(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/developer-utilities/rate-limit-status/api-reference/get-application-rate_limit_status
        """
        return self.request(
            'GET', 'application/rate_limit_status', endpoint_parameters=(
                'resources',
            ), use_cache=False, **kwargs
        )

    @payload('user')
    def update_profile_image(self, filename, file_=None, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/manage-account-settings/api-reference/post-account-update_profile_image
        """
        headers, post_data = API._pack_image(filename, 700, f=file_)
        return self.request(
            'POST', 'account/update_profile_image', endpoint_parameters=(
                'include_entities', 'skip_status'
            ), post_data=post_data, headers=headers, **kwargs
        )

    def update_profile_banner(self, filename, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/manage-account-settings/api-reference/post-account-update_profile_banner
        """
        f = kwargs.pop('file', None)
        headers, post_data = API._pack_image(filename, 700,
                                             form_field='banner', f=f)
        return self.request(
            'POST', 'account/update_profile_banner', endpoint_parameters=(
                'width', 'height', 'offset_left', 'offset_right'
            ), post_data=post_data, headers=headers, **kwargs
        )

    @payload('user')
    def update_profile(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/manage-account-settings/api-reference/post-account-update_profile
        """
        return self.request(
            'POST', 'account/update_profile', endpoint_parameters=(
                'name', 'url', 'location', 'description', 'profile_link_color',
                'include_entities', 'skip_status'
            ), **kwargs
        )

    @pagination(mode='id')
    @payload('status', list=True)
    def favorites(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/get-favorites-list
        """
        return self.request(
            'GET', 'favorites/list', endpoint_parameters=(
                'user_id', 'screen_name', 'count', 'since_id', 'max_id',
                'include_entities'
            ), **kwargs
        )

    @payload('status')
    def create_favorite(self, id, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/post-favorites-create
        """
        return self.request(
            'POST', 'favorites/create', id, endpoint_parameters=(
                'id', 'include_entities'
            ), **kwargs
        )

    @payload('status')
    def destroy_favorite(self, id, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/post-favorites-destroy
        """
        return self.request(
            'POST', 'favorites/destroy', id, endpoint_parameters=(
                'id', 'include_entities'
            ), **kwargs
        )

    @payload('user')
    def create_block(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/mute-block-report-users/api-reference/post-blocks-create
        """
        return self.request(
            'POST', 'blocks/create', endpoint_parameters=(
                'screen_name', 'user_id', 'include_entities', 'skip_status'
            ), **kwargs
        )

    @payload('user')
    def destroy_block(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/mute-block-report-users/api-reference/post-blocks-destroy
        """
        return self.request(
            'POST', 'blocks/destroy', endpoint_parameters=(
                'screen_name', 'user_id', 'include_entities', 'skip_status'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('ids')
    def mutes_ids(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/mute-block-report-users/api-reference/get-mutes-users-ids
        """
        return self.request(
            'GET', 'mutes/users/ids', endpoint_parameters=(
                'stringify_ids', 'cursor'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('user', list=True)
    def mutes(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/mute-block-report-users/api-reference/get-mutes-users-list
        """
        return self.request(
            'GET', 'mutes/users/list', endpoint_parameters=(
                'cursor', 'include_entities', 'skip_status'
            ), **kwargs
        )

    @payload('user')
    def create_mute(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/mute-block-report-users/api-reference/post-mutes-users-create
        """
        return self.request(
            'POST', 'mutes/users/create', endpoint_parameters=(
                'screen_name', 'user_id'
            ), **kwargs
        )

    @payload('user')
    def destroy_mute(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/mute-block-report-users/api-reference/post-mutes-users-destroy
        """
        return self.request(
            'POST', 'mutes/users/destroy', endpoint_parameters=(
                'screen_name', 'user_id'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('user', list=True)
    def blocks(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/mute-block-report-users/api-reference/get-blocks-list
        """
        return self.request(
            'GET', 'blocks/list', endpoint_parameters=(
                'include_entities', 'skip_status', 'cursor'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('ids')
    def blocks_ids(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/mute-block-report-users/api-reference/get-blocks-ids
        """
        return self.request(
            'GET', 'blocks/ids', endpoint_parameters=(
                'stringify_ids', 'cursor',
            ), **kwargs
        )

    @payload('user')
    def report_spam(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/mute-block-report-users/api-reference/post-users-report_spam
        """
        return self.request(
            'POST', 'users/report_spam', endpoint_parameters=(
                'screen_name', 'user_id', 'perform_block'
            ), **kwargs
        )

    @payload('saved_search', list=True)
    def saved_searches(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/manage-account-settings/api-reference/get-saved_searches-list
        """
        return self.request('GET', 'saved_searches/list', **kwargs)

    @payload('saved_search')
    def get_saved_search(self, id, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/manage-account-settings/api-reference/get-saved_searches-show-id
        """
        return self.request('GET', f'saved_searches/show/{id}', **kwargs)

    @payload('saved_search')
    def create_saved_search(self, query, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/manage-account-settings/api-reference/post-saved_searches-create
        """
        return self.request(
            'POST', 'saved_searches/create', query, endpoint_parameters=(
                'query',
            ), **kwargs
        )

    @payload('saved_search')
    def destroy_saved_search(self, id, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/manage-account-settings/api-reference/post-saved_searches-destroy-id
        """
        return self.request('POST', f'saved_searches/destroy/{id}', **kwargs)

    @payload('list')
    def create_list(self, name, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/post-lists-create
        """
        return self.request(
            'POST', 'lists/create', name, endpoint_parameters=(
                'name', 'mode', 'description'
            ), **kwargs
        )

    @payload('list')
    def destroy_list(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/post-lists-destroy
        """
        return self.request(
            'POST', 'lists/destroy', endpoint_parameters=(
                'owner_screen_name', 'owner_id', 'list_id', 'slug'
            ), **kwargs
        )

    @payload('list')
    def update_list(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/post-lists-update
        """
        return self.request(
            'POST', 'lists/update', endpoint_parameters=(
                'list_id', 'slug', 'name', 'mode', 'description',
                'owner_screen_name', 'owner_id'
            ), **kwargs
        )

    @payload('list', list=True)
    def lists_all(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/get-lists-list
        """
        return self.request(
            'GET', 'lists/list', endpoint_parameters=(
                'user_id', 'screen_name', 'reverse'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('list', list=True)
    def lists_memberships(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/get-lists-memberships
        """
        return self.request(
            'GET', 'lists/memberships', endpoint_parameters=(
                'user_id', 'screen_name', 'count', 'cursor',
                'filter_to_owned_lists'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('list', list=True)
    def lists_ownerships(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/get-lists-ownerships
        """
        return self.request(
            'GET', 'lists/ownerships', endpoint_parameters=(
                'user_id', 'screen_name', 'count', 'cursor'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('list', list=True)
    def lists_subscriptions(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/get-lists-subscriptions
        """
        return self.request(
            'GET', 'lists/subscriptions', endpoint_parameters=(
                'user_id', 'screen_name', 'count', 'cursor'
            ), **kwargs
        )

    @pagination(mode='id')
    @payload('status', list=True)
    def list_timeline(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/get-lists-statuses
        """
        return self.request(
            'GET', 'lists/statuses', endpoint_parameters=(
                'list_id', 'slug', 'owner_screen_name', 'owner_id', 'since_id',
                'max_id', 'count', 'include_entities', 'include_rts'
            ), **kwargs
        )

    @payload('list')
    def get_list(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/get-lists-show
        """
        return self.request(
            'GET', 'lists/show', endpoint_parameters=(
                'list_id', 'slug', 'owner_screen_name', 'owner_id'
            ), **kwargs
        )

    @payload('list')
    def add_list_member(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/post-lists-members-create
        """
        return self.request(
            'POST', 'lists/members/create', endpoint_parameters=(
                'list_id', 'slug', 'user_id', 'screen_name',
                'owner_screen_name', 'owner_id'
            ), **kwargs
        )

    @payload('list')
    def remove_list_member(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/post-lists-members-destroy
        """
        return self.request(
            'POST', 'lists/members/destroy', endpoint_parameters=(
                'list_id', 'slug', 'user_id', 'screen_name',
                'owner_screen_name', 'owner_id'
            ), **kwargs
        )

    @payload('list')
    def add_list_members(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/post-lists-members-create_all
        """
        if 'user_id' in kwargs:
            kwargs['user_id'] = list_to_csv(kwargs['user_id'])
        if 'screen_name' in kwargs:
            kwargs['screen_name'] = list_to_csv(kwargs['screen_name'])
        return self.request(
            'POST', 'lists/members/create_all', endpoint_parameters=(
                'list_id', 'slug', 'user_id', 'screen_name',
                'owner_screen_name', 'owner_id'
            ), **kwargs
        )

    @payload('list')
    def remove_list_members(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/post-lists-members-destroy_all
        """
        if 'user_id' in kwargs:
            kwargs['user_id'] = list_to_csv(kwargs['user_id'])
        if 'screen_name' in kwargs:
            kwargs['screen_name'] = list_to_csv(kwargs['screen_name'])
        return self.request(
            'POST', 'lists/members/destroy_all', endpoint_parameters=(
                'list_id', 'slug', 'user_id', 'screen_name',
                'owner_screen_name', 'owner_id'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('user', list=True)
    def list_members(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/get-lists-members
        """
        return self.request(
            'GET', 'lists/members', endpoint_parameters=(
                'list_id', 'slug', 'owner_screen_name', 'owner_id', 'count',
                'cursor', 'include_entities', 'skip_status'
            ), **kwargs
        )

    @payload('user')
    def show_list_member(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/get-lists-members-show
        """
        return self.request(
            'GET', 'lists/members/show', endpoint_parameters=(
                'list_id', 'slug', 'user_id', 'screen_name',
                'owner_screen_name', 'owner_id', 'include_entities',
                'skip_status'
            ), **kwargs
        )

    @payload('list')
    def subscribe_list(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/post-lists-subscribers-create
        """
        return self.request(
            'POST', 'lists/subscribers/create', endpoint_parameters=(
                'owner_screen_name', 'owner_id', 'list_id', 'slug'
            ), **kwargs
        )

    @payload('list')
    def unsubscribe_list(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/post-lists-subscribers-destroy
        """
        return self.request(
            'POST', 'lists/subscribers/destroy', endpoint_parameters=(
                'list_id', 'slug', 'owner_screen_name', 'owner_id'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('user', list=True)
    def list_subscribers(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/get-lists-subscribers
        """
        return self.request(
            'GET', 'lists/subscribers', endpoint_parameters=(
                'list_id', 'slug', 'owner_screen_name', 'owner_id', 'count',
                'cursor', 'include_entities', 'skip_status'
            ), **kwargs
        )

    @payload('user')
    def show_list_subscriber(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/create-manage-lists/api-reference/get-lists-subscribers-show
        """
        return self.request(
            'GET', 'lists/subscribers/show', endpoint_parameters=(
                'owner_screen_name', 'owner_id', 'list_id', 'slug', 'user_id',
                'screen_name', 'include_entities', 'skip_status'
            ), **kwargs
        )

    @payload('json')
    def trends_available(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/trends/locations-with-trending-topics/api-reference/get-trends-available
        """
        return self.request('GET', 'trends/available', *args, **kwargs)

    @payload('json')
    def trends_place(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/trends/trends-for-location/api-reference/get-trends-place
        """
        return self.request(
            'GET', 'trends/place', *args, endpoint_parameters=(
                'id', 'exclude'
            ), **kwargs
        )

    @payload('json')
    def trends_closest(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/trends/locations-with-trending-topics/api-reference/get-trends-closest
        """
        return self.request(
            'GET', 'trends/closest', *args, endpoint_parameters=(
                'lat', 'long'
            ), **kwargs
        )

    @pagination(mode='id')
    @payload('search_results')
    def search(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/search/api-reference/get-search-tweets
        """
        return self.request(
            'GET', 'search/tweets', *args, endpoint_parameters=(
                'q', 'lang', 'locale', 'since_id', 'geocode', 'max_id',
                'until', 'result_type', 'count', 'include_entities'
            ), **kwargs
        )

    @pagination(mode='next')
    @payload('status', list=True)
    def search_30_day(self, environment_name, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/search/api-reference/premium-search
        """
        return self.request(
            'GET', f'tweets/search/30day/{environment_name}', *args,
            endpoint_parameters=(
                'query', 'tag', 'fromDate', 'toDate', 'maxResults', 'next'
            ), **kwargs
        )

    @pagination(mode='next')
    @payload('status', list=True)
    def search_full_archive(self, environment_name, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/tweets/search/api-reference/premium-search
        """
        return self.request(
            'GET', f'tweets/search/fullarchive/{environment_name}', *args,
            endpoint_parameters=(
                'query', 'tag', 'fromDate', 'toDate', 'maxResults', 'next'
            ), **kwargs
        )

    @payload('place', list=True)
    def reverse_geocode(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/geo/places-near-location/api-reference/get-geo-reverse_geocode
        """
        return self.request(
            'GET', 'geo/reverse_geocode', *args, endpoint_parameters=(
                'lat', 'long', 'accuracy', 'granularity', 'max_results'
            ), **kwargs
        )

    @payload('place')
    def geo_id(self, place_id, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/geo/place-information/api-reference/get-geo-id-place_id
        """
        return self.request('GET', f'geo/id/{place_id}', *args, **kwargs)

    @payload('place', list=True)
    def geo_search(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/geo/places-near-location/api-reference/get-geo-search
        """
        return self.request(
            'GET', 'geo/search', *args, endpoint_parameters=(
                'lat', 'long', 'query', 'ip', 'granularity', 'accuracy',
                'max_results', 'contained_within'
            ), **kwargs
        )

    @payload('json')
    def supported_languages(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/developer-utilities/supported-languages/api-reference/get-help-languages
        """
        return self.request('GET', 'help/languages', *args, **kwargs)

    @payload('json')
    def configuration(self, *args, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/developer-utilities/configuration/api-reference/get-help-configuration
        """
        return self.request('GET', 'help/configuration', *args, **kwargs)

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
