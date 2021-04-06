# Tweepy
# Copyright 2009-2021 Joshua Roesslein
# See LICENSE for details.

import functools
import imghdr
import logging
import mimetypes
import os
import sys
import time
from urllib.parse import urlencode

import requests

from tweepy.errors import (
    BadRequest, Forbidden, HTTPException, NotFound, TooManyRequests,
    TweepyException, TwitterServerError, Unauthorized
)
from tweepy.models import Model
from tweepy.parsers import ModelParser, Parser
from tweepy.utils import list_to_csv

log = logging.getLogger(__name__)


def pagination(mode):
    def decorator(method):
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            return method(*args, **kwargs)
        wrapper.pagination_mode = mode
        return wrapper
    return decorator


def payload(payload_type, **payload_kwargs):
    payload_list = payload_kwargs.get('list', False)
    def decorator(method):
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            kwargs['payload_list'] = payload_list
            kwargs['payload_type'] = payload_type
            return method(*args, **kwargs)
        wrapper.payload_list = payload_list
        wrapper.payload_type = payload_type
        return wrapper
    return decorator


class API:
    """This class provides a wrapper for the API as provided by Twitter.
    The functions provided in this class are listed below.

    :param auth_handler: The authentication handler to be used
    :param cache: The cache to query if a GET method is used
    :param host: The general REST API host server URL
    :param parser: The Parser instance to use for parsing the response from
                   Twitter; defaults to an instance of ModelParser
    :param proxy: The full url to an HTTPS proxy to use for connecting to
                  Twitter
    :param retry_count: Number of retries to attempt when an error occurs
    :param retry_delay: Number of seconds to wait between retries
    :param retry_errors: Which HTTP status codes to retry
    :param timeout: The maximum amount of time to wait for a response from
                    Twitter
    :param upload_host: The URL of the upload server
    :param wait_on_rate_limit: Whether or not to automatically wait for rate
                               limits to replenish
    
    :raise TypeError: If the given parser is not a Parser instance

    :reference: https://developer.twitter.com/en/docs/api-reference-index
    """

    def __init__(self, auth_handler=None, *, cache=None,
                 host='api.twitter.com', parser=None, proxy=None,
                 retry_count=0, retry_delay=0, retry_errors=None, timeout=60,
                 upload_host='upload.twitter.com', wait_on_rate_limit=False):
        self.auth = auth_handler
        self.cache = cache
        self.host = host

        if parser is None:
            parser = ModelParser()
        self.parser = parser

        self.proxy = {}
        if proxy is not None:
            self.proxy['https'] = proxy

        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.retry_errors = retry_errors
        self.timeout = timeout
        self.upload_host = upload_host
        self.wait_on_rate_limit = wait_on_rate_limit

        # Attempt to explain more clearly the parser argument requirements
        # https://github.com/tweepy/tweepy/issues/421

        if not isinstance(self.parser, Parser):
            raise TypeError(
                "parser should be an instance of Parser, not " +
                str(type(self.parser))
            )

        self.session = requests.Session()

    def request(
        self, method, endpoint, *, endpoint_parameters=(), params=None,
        headers=None, json_payload=None, parser=None, payload_list=False,
        payload_type=None, post_data=None, files=None, require_auth=True,
        return_cursors=False, upload_api=False, use_cache=True, **kwargs
    ):
        # If authentication is required and no credentials
        # are provided, throw an error.
        if require_auth and not self.auth:
            raise TweepyException('Authentication required!')

        self.cached_result = False

        # Build the request URL
        path = f'/1.1/{endpoint}.json'
        if upload_api:
            url = 'https://' + self.upload_host + path
        else:
            url = 'https://' + self.host + path

        if params is None:
            params = {}
        for k, arg in kwargs.items():
            if arg is None:
                continue
            if k not in endpoint_parameters and k != "tweet_mode":
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
                        data=post_data, files=files, json=json_payload,
                        timeout=self.timeout, auth=auth, proxies=self.proxy
                    )
                except Exception as e:
                    raise TweepyException(f'Failed to send request: {e}').with_traceback(sys.exc_info()[2])

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
            if resp.status_code == 400:
                raise BadRequest(resp)
            if resp.status_code == 401:
                raise Unauthorized(resp)
            if resp.status_code == 403:
                raise Forbidden(resp)
            if resp.status_code == 404:
                raise NotFound(resp)
            if resp.status_code == 429:
                raise TooManyRequests(resp)
            if resp.status_code >= 500:
                raise TwitterServerError(resp)
            if resp.status_code and not 200 <= resp.status_code < 300:
                raise HTTPException(resp)

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
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/timelines/api-reference/get-statuses-home_timeline
        """
        return self.request(
            'GET', 'statuses/home_timeline', endpoint_parameters=(
                'count', 'since_id', 'max_id', 'trim_user', 'exclude_replies',
                'include_entities'
            ), **kwargs
        )

    @payload('status', list=True)
    def statuses_lookup(self, id, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-statuses-lookup
        """
        return self.request(
            'GET', 'statuses/lookup', endpoint_parameters=(
                'id', 'include_entities', 'trim_user', 'map',
                'include_ext_alt_text', 'include_card_uri'
            ), id=list_to_csv(id), **kwargs
        )

    @pagination(mode='id')
    @payload('status', list=True)
    def user_timeline(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/timelines/api-reference/get-statuses-user_timeline
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
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/timelines/api-reference/get-statuses-mentions_timeline
        """
        return self.request(
            'GET', 'statuses/mentions_timeline', endpoint_parameters=(
                'count', 'since_id', 'max_id', 'trim_user', 'include_entities'
            ), **kwargs
        )

    @pagination(mode='id')
    @payload('status', list=True)
    def retweets_of_me(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-statuses-retweets_of_me
        """
        return self.request(
            'GET', 'statuses/retweets_of_me', endpoint_parameters=(
                'count', 'since_id', 'max_id', 'trim_user', 'include_entities',
                'include_user_entities'
            ), **kwargs
        )

    @payload('status')
    def get_status(self, id, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-statuses-show-id
        """
        return self.request(
            'GET', 'statuses/show', endpoint_parameters=(
                'id', 'trim_user', 'include_my_retweet', 'include_entities',
                'include_ext_alt_text', 'include_card_uri'
            ), id=id, **kwargs
        )

    @payload('status')
    def update_status(self, status, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-statuses-update
        """
        if 'media_ids' in kwargs:
            kwargs['media_ids'] = list_to_csv(kwargs['media_ids'])

        return self.request(
            'POST', 'statuses/update', endpoint_parameters=(
                'status', 'in_reply_to_status_id',
                'auto_populate_reply_metadata', 'exclude_reply_user_ids',
                'attachment_url', 'media_ids', 'possibly_sensitive', 'lat',
                'long', 'place_id', 'display_coordinates', 'trim_user',
                'enable_dmcommands', 'fail_dmcommands', 'card_uri'
            ), status=status, **kwargs
        )

    def media_upload(self, filename, *, file=None, chunked=False,
                     media_category=None, additional_owners=None, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/media/upload-media/overview
        """
        h = None
        if file is not None:
            location = file.tell()
            h = file.read(32)
            file.seek(location)
        file_type = imghdr.what(filename, h=h)
        if file_type is not None:
            file_type = 'image/' + file_type
        else:
            file_type = mimetypes.guess_type(filename)[0]

        if chunked or file_type.startswith('video/'):
            return self.chunked_upload(
                filename, file=file, file_type=file_type,
                media_category=media_category,
                additional_owners=additional_owners, **kwargs
            )
        else:
            return self.simple_upload(
                filename, file=file, media_category=media_category,
                additional_owners=additional_owners, **kwargs
            )

    @payload('media')
    def simple_upload(self, filename, *, file=None, media_category=None,
                      additional_owners=None, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/media/upload-media/api-reference/post-media-upload
        """
        if file is not None:
            files = {'media': (filename, file)}
        else:
            files = {'media': open(filename, 'rb')}

        post_data = {}
        if media_category is not None:
            post_data['media_category'] = media_category
        if additional_owners is not None:
            post_data['additional_owners'] = additional_owners

        return self.request(
            'POST', 'media/upload', post_data=post_data, files=files,
            upload_api=True, **kwargs
        )

    def chunked_upload(self, filename, *, file=None, file_type=None,
                       wait_for_async_finalize=True, media_category=None,
                       additional_owners=None, **kwargs):
        """ :reference https://developer.twitter.com/en/docs/twitter-api/v1/media/upload-media/uploading-media/chunked-media-upload
        """
        fp = file or open(filename, 'rb')

        start = fp.tell()
        fp.seek(0, 2)  # Seek to end of file
        file_size = fp.tell() - start
        fp.seek(start)

        media_id = self.chunked_upload_init(
            file_size, file_type, media_category=media_category,
            additional_owners=additional_owners, **kwargs
        ).media_id

        min_chunk_size, remainder = divmod(file_size, 1000)
        min_chunk_size += bool(remainder)

        # Use 1 MiB as default chunk size
        chunk_size = kwargs.pop('chunk_size', 1024 * 1024)
        # Max chunk size is 5 MiB
        chunk_size = max(min(chunk_size, 5 * 1024 * 1024), min_chunk_size)

        segments, remainder = divmod(file_size, chunk_size)
        segments += bool(remainder)

        for segment_index in range(segments):
            # The APPEND command returns an empty response body
            self.chunked_upload_append(
                media_id, (filename, fp.read(chunk_size)), segment_index,
                **kwargs
            )

        fp.close()
        media =  self.chunked_upload_finalize(media_id, **kwargs)

        if wait_for_async_finalize and hasattr(media, 'processing_info'):
            while media.processing_info['state'] in ('pending', 'in_progress'):
                time.sleep(media.processing_info['check_after_secs'])
                media = self.get_media_upload_status(media.media_id, **kwargs)

        return media

    @payload('media')
    def chunked_upload_init(self, total_bytes, media_type, *,
                            media_category=None, additional_owners=None,
                            **kwargs):
        """ :reference https://developer.twitter.com/en/docs/twitter-api/v1/media/upload-media/api-reference/post-media-upload-init
        """
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        post_data = {
            'command': 'INIT',
            'total_bytes': total_bytes,
            'media_type': media_type,
        }
        if media_category is not None:
            post_data['media_category'] = media_category
        if additional_owners is not None:
            post_data['additional_owners'] = list_to_csv(additional_owners)

        return self.request(
            'POST', 'media/upload', headers=headers, post_data=post_data,
            upload_api=True, **kwargs
        )

    def chunked_upload_append(self, media_id, media, segment_index, **kwargs):
        """ :reference https://developer.twitter.com/en/docs/twitter-api/v1/media/upload-media/api-reference/post-media-upload-append
        """
        post_data = {
            'command': 'APPEND',
            'media_id': media_id,
            'segment_index': segment_index
        }
        files = {'media': media}
        return self.request(
            'POST', 'media/upload', post_data=post_data, files=files,
            upload_api=True, **kwargs
        )

    @payload('media')
    def chunked_upload_finalize(self, media_id, **kwargs):
        """ :reference https://developer.twitter.com/en/docs/twitter-api/v1/media/upload-media/api-reference/post-media-upload-finalize
        """
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        post_data = {
            'command': 'FINALIZE',
            'media_id': media_id
        }
        return self.request(
            'POST', 'media/upload', headers=headers, post_data=post_data,
            upload_api=True, **kwargs
        )

    def create_media_metadata(self, media_id, alt_text, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/media/upload-media/api-reference/post-media-metadata-create
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
    def update_with_media(self, status, filename, *, file=None, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-statuses-update_with_media
        """
        if file is not None:
            files = {'media[]': (filename, file)}
        else:
            files = {'media[]': open(filename, 'rb')}
        return self.request(
            'POST', 'statuses/update_with_media', endpoint_parameters=(
                'status', 'possibly_sensitive', 'in_reply_to_status_id',
                'lat', 'long', 'place_id', 'display_coordinates'
            ), status=status, files=files, **kwargs
        )

    @payload('media')
    def get_media_upload_status(self, media_id, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/media/upload-media/api-reference/get-media-upload-status
        """
        return self.request(
            'GET', 'media/upload', endpoint_parameters=(
                'command', 'media_id'
            ), command='STATUS', media_id=media_id, upload_api=True, **kwargs
        )

    @payload('status')
    def destroy_status(self, id, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-statuses-destroy-id
        """
        return self.request(
            'POST', f'statuses/destroy/{id}', endpoint_parameters=(
                'trim_user',
            ), **kwargs
        )

    @payload('status')
    def retweet(self, id, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-statuses-retweet-id
        """
        return self.request(
            'POST', f'statuses/retweet/{id}', endpoint_parameters=(
                'trim_user',
            ), **kwargs
        )

    @payload('status')
    def unretweet(self, id, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-statuses-unretweet-id
        """
        return self.request(
            'POST', f'statuses/unretweet/{id}', endpoint_parameters=(
                'trim_user',
            ), **kwargs
        )

    @payload('status', list=True)
    def retweets(self, id, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-statuses-retweets-id
        """
        return self.request(
            'GET', f'statuses/retweets/{id}', endpoint_parameters=(
                'count', 'trim_user'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('ids')
    def retweeters(self, id, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-statuses-retweeters-ids
        """
        return self.request(
            'GET', 'statuses/retweeters/ids', endpoint_parameters=(
                'id', 'count', 'cursor', 'stringify_ids'
            ), id=id, **kwargs
        )

    @payload('user')
    def get_user(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-users-show
        """
        return self.request(
            'GET', 'users/show', endpoint_parameters=(
                'user_id', 'screen_name', 'include_entities'
            ), **kwargs
        )

    @payload('json')
    def get_oembed(self, url, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-statuses-oembed
        """
        return self.request(
            'GET', 'statuses/oembed', endpoint_parameters=(
                'url', 'maxwidth', 'hide_media', 'hide_thread', 'omit_script',
                'align', 'related', 'lang', 'theme', 'link_color',
                'widget_type', 'dnt'
            ), url=url, require_auth=False, **kwargs
        )

    @payload('user', list=True)
    def lookup_users(self, *, screen_name=None, user_id=None, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-users-lookup
        """
        return self.request(
            'POST', 'users/lookup', endpoint_parameters=(
                'screen_name', 'user_id', 'include_entities', 'tweet_mode'
            ), screen_name=list_to_csv(screen_name),
            user_id=list_to_csv(user_id), **kwargs
        )

    def me(self):
        """ Get the authenticated user """
        return self.get_user(screen_name=self.auth.get_username())

    @pagination(mode='page')
    @payload('user', list=True)
    def search_users(self, q, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-users-search
        """
        return self.request(
            'GET', 'users/search', endpoint_parameters=(
                'q', 'page', 'count', 'include_entities'
            ), q=q, **kwargs
        )

    @payload('direct_message')
    def get_direct_message(self, id, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/direct-messages/sending-and-receiving/api-reference/get-event
        """
        return self.request(
            'GET', 'direct_messages/events/show', endpoint_parameters=(
                'id',
            ), id=id, **kwargs
        )

    @pagination(mode='dm_cursor')
    @payload('direct_message', list=True)
    def list_direct_messages(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/direct-messages/sending-and-receiving/api-reference/list-events
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
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/direct-messages/sending-and-receiving/api-reference/new-event
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
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/direct-messages/sending-and-receiving/api-reference/delete-message-event
        """
        return self.request(
            'DELETE', 'direct_messages/events/destroy', endpoint_parameters=(
                'id',
            ), id=id, **kwargs
        )

    @payload('user')
    def create_friendship(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/post-friendships-create
        """
        return self.request(
            'POST', 'friendships/create', endpoint_parameters=(
                'screen_name', 'user_id', 'follow'
            ), **kwargs
        )

    @payload('user')
    def destroy_friendship(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/post-friendships-destroy
        """
        return self.request(
            'POST', 'friendships/destroy', endpoint_parameters=(
                'screen_name', 'user_id'
            ), **kwargs
        )

    @payload('friendship')
    def show_friendship(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friendships-show
        """
        return self.request(
            'GET', 'friendships/show', endpoint_parameters=(
                'source_id', 'source_screen_name', 'target_id',
                'target_screen_name'
            ), **kwargs
        )

    @payload('relationship', list=True)
    def lookup_friendships(self, *, screen_name=None, user_id=None, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friendships-lookup
        """
        return self.request(
            'GET', 'friendships/lookup', endpoint_parameters=(
                'screen_name', 'user_id'
            ), screen_name=list_to_csv(screen_name),
            user_id=list_to_csv(user_id), **kwargs
        )

    @pagination(mode='cursor')
    @payload('ids')
    def friends_ids(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friends-ids
        """
        return self.request(
            'GET', 'friends/ids', endpoint_parameters=(
                'user_id', 'screen_name', 'cursor', 'stringify_ids', 'count'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('user', list=True)
    def friends(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friends-list
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
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friendships-incoming
        """
        return self.request(
            'GET', 'friendships/incoming', endpoint_parameters=(
                'cursor', 'stringify_ids'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('ids')
    def friendships_outgoing(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friendships-outgoing
        """
        return self.request(
            'GET', 'friendships/outgoing', endpoint_parameters=(
                'cursor', 'stringify_ids'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('ids')
    def followers_ids(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-followers-ids
        """
        return self.request(
            'GET', 'followers/ids', endpoint_parameters=(
                'user_id', 'screen_name', 'cursor', 'count'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('user', list=True)
    def followers(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-followers-list
        """
        return self.request(
            'GET', 'followers/list', endpoint_parameters=(
                'user_id', 'screen_name', 'cursor', 'count', 'skip_status',
                'include_user_entities'
            ), **kwargs
        )

    @payload('json')
    def get_settings(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/get-account-settings
        """
        return self.request(
            'GET', 'account/settings', use_cache=False, **kwargs
        )

    @payload('json')
    def set_settings(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/post-account-settings
        """
        return self.request(
            'POST', 'account/settings', endpoint_parameters=(
                'sleep_time_enabled', 'start_sleep_time', 'end_sleep_time',
                'time_zone', 'trend_location_woeid', 'lang'
            ), use_cache=False, **kwargs
        )

    @payload('user')
    def verify_credentials(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/get-account-verify_credentials
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
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/developer-utilities/rate-limit-status/api-reference/get-application-rate_limit_status
        """
        return self.request(
            'GET', 'application/rate_limit_status', endpoint_parameters=(
                'resources',
            ), use_cache=False, **kwargs
        )

    @payload('user')
    def update_profile_image(self, filename, *, file=None, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/post-account-update_profile_image
        """
        if file is not None:
            files = {'image': (filename, file)}
        else:
            files = {'image': open(filename, 'rb')}
        return self.request(
            'POST', 'account/update_profile_image', endpoint_parameters=(
                'include_entities', 'skip_status'
            ), files=files, **kwargs
        )

    def update_profile_banner(self, filename, *, file=None, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/post-account-update_profile_banner
        """
        if file is not None:
            files = {'banner': (filename, file)}
        else:
            files = {'banner': open(filename, 'rb')}
        return self.request(
            'POST', 'account/update_profile_banner', endpoint_parameters=(
                'width', 'height', 'offset_left', 'offset_right'
            ), files=files, **kwargs
        )

    @payload('user')
    def update_profile(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/post-account-update_profile
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
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-favorites-list
        """
        return self.request(
            'GET', 'favorites/list', endpoint_parameters=(
                'user_id', 'screen_name', 'count', 'since_id', 'max_id',
                'include_entities'
            ), **kwargs
        )

    @payload('status')
    def create_favorite(self, id, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-favorites-create
        """
        return self.request(
            'POST', 'favorites/create', endpoint_parameters=(
                'id', 'include_entities'
            ), id=id, **kwargs
        )

    @payload('status')
    def destroy_favorite(self, id, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-favorites-destroy
        """
        return self.request(
            'POST', 'favorites/destroy', endpoint_parameters=(
                'id', 'include_entities'
            ), id=id, **kwargs
        )

    @payload('user')
    def create_block(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/mute-block-report-users/api-reference/post-blocks-create
        """
        return self.request(
            'POST', 'blocks/create', endpoint_parameters=(
                'screen_name', 'user_id', 'include_entities', 'skip_status'
            ), **kwargs
        )

    @payload('user')
    def destroy_block(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/mute-block-report-users/api-reference/post-blocks-destroy
        """
        return self.request(
            'POST', 'blocks/destroy', endpoint_parameters=(
                'screen_name', 'user_id', 'include_entities', 'skip_status'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('ids')
    def mutes_ids(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/mute-block-report-users/api-reference/get-mutes-users-ids
        """
        return self.request(
            'GET', 'mutes/users/ids', endpoint_parameters=(
                'stringify_ids', 'cursor'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('user', list=True)
    def mutes(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/mute-block-report-users/api-reference/get-mutes-users-list
        """
        return self.request(
            'GET', 'mutes/users/list', endpoint_parameters=(
                'cursor', 'include_entities', 'skip_status'
            ), **kwargs
        )

    @payload('user')
    def create_mute(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/mute-block-report-users/api-reference/post-mutes-users-create
        """
        return self.request(
            'POST', 'mutes/users/create', endpoint_parameters=(
                'screen_name', 'user_id'
            ), **kwargs
        )

    @payload('user')
    def destroy_mute(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/mute-block-report-users/api-reference/post-mutes-users-destroy
        """
        return self.request(
            'POST', 'mutes/users/destroy', endpoint_parameters=(
                'screen_name', 'user_id'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('user', list=True)
    def blocks(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/mute-block-report-users/api-reference/get-blocks-list
        """
        return self.request(
            'GET', 'blocks/list', endpoint_parameters=(
                'include_entities', 'skip_status', 'cursor'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('ids')
    def blocks_ids(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/mute-block-report-users/api-reference/get-blocks-ids
        """
        return self.request(
            'GET', 'blocks/ids', endpoint_parameters=(
                'stringify_ids', 'cursor',
            ), **kwargs
        )

    @payload('user')
    def report_spam(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/mute-block-report-users/api-reference/post-users-report_spam
        """
        return self.request(
            'POST', 'users/report_spam', endpoint_parameters=(
                'screen_name', 'user_id', 'perform_block'
            ), **kwargs
        )

    @payload('saved_search', list=True)
    def saved_searches(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/get-saved_searches-list
        """
        return self.request('GET', 'saved_searches/list', **kwargs)

    @payload('saved_search')
    def get_saved_search(self, id, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/get-saved_searches-show-id
        """
        return self.request('GET', f'saved_searches/show/{id}', **kwargs)

    @payload('saved_search')
    def create_saved_search(self, query, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/post-saved_searches-create
        """
        return self.request(
            'POST', 'saved_searches/create', endpoint_parameters=(
                'query',
            ), query=query, **kwargs
        )

    @payload('saved_search')
    def destroy_saved_search(self, id, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/post-saved_searches-destroy-id
        """
        return self.request('POST', f'saved_searches/destroy/{id}', **kwargs)

    @payload('list')
    def create_list(self, name, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/post-lists-create
        """
        return self.request(
            'POST', 'lists/create', endpoint_parameters=(
                'name', 'mode', 'description'
            ), name=name, **kwargs
        )

    @payload('list')
    def destroy_list(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/post-lists-destroy
        """
        return self.request(
            'POST', 'lists/destroy', endpoint_parameters=(
                'owner_screen_name', 'owner_id', 'list_id', 'slug'
            ), **kwargs
        )

    @payload('list')
    def update_list(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/post-lists-update
        """
        return self.request(
            'POST', 'lists/update', endpoint_parameters=(
                'list_id', 'slug', 'name', 'mode', 'description',
                'owner_screen_name', 'owner_id'
            ), **kwargs
        )

    @payload('list', list=True)
    def lists_all(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-list
        """
        return self.request(
            'GET', 'lists/list', endpoint_parameters=(
                'user_id', 'screen_name', 'reverse'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('list', list=True)
    def lists_memberships(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-memberships
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
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-ownerships
        """
        return self.request(
            'GET', 'lists/ownerships', endpoint_parameters=(
                'user_id', 'screen_name', 'count', 'cursor'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('list', list=True)
    def lists_subscriptions(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-subscriptions
        """
        return self.request(
            'GET', 'lists/subscriptions', endpoint_parameters=(
                'user_id', 'screen_name', 'count', 'cursor'
            ), **kwargs
        )

    @pagination(mode='id')
    @payload('status', list=True)
    def list_timeline(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-statuses
        """
        return self.request(
            'GET', 'lists/statuses', endpoint_parameters=(
                'list_id', 'slug', 'owner_screen_name', 'owner_id', 'since_id',
                'max_id', 'count', 'include_entities', 'include_rts'
            ), **kwargs
        )

    @payload('list')
    def get_list(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-show
        """
        return self.request(
            'GET', 'lists/show', endpoint_parameters=(
                'list_id', 'slug', 'owner_screen_name', 'owner_id'
            ), **kwargs
        )

    @payload('list')
    def add_list_member(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/post-lists-members-create
        """
        return self.request(
            'POST', 'lists/members/create', endpoint_parameters=(
                'list_id', 'slug', 'user_id', 'screen_name',
                'owner_screen_name', 'owner_id'
            ), **kwargs
        )

    @payload('list')
    def remove_list_member(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/post-lists-members-destroy
        """
        return self.request(
            'POST', 'lists/members/destroy', endpoint_parameters=(
                'list_id', 'slug', 'user_id', 'screen_name',
                'owner_screen_name', 'owner_id'
            ), **kwargs
        )

    @payload('list')
    def add_list_members(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/post-lists-members-create_all
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
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/post-lists-members-destroy_all
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
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-members
        """
        return self.request(
            'GET', 'lists/members', endpoint_parameters=(
                'list_id', 'slug', 'owner_screen_name', 'owner_id', 'count',
                'cursor', 'include_entities', 'skip_status'
            ), **kwargs
        )

    @payload('user')
    def show_list_member(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-members-show
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
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/post-lists-subscribers-create
        """
        return self.request(
            'POST', 'lists/subscribers/create', endpoint_parameters=(
                'owner_screen_name', 'owner_id', 'list_id', 'slug'
            ), **kwargs
        )

    @payload('list')
    def unsubscribe_list(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/post-lists-subscribers-destroy
        """
        return self.request(
            'POST', 'lists/subscribers/destroy', endpoint_parameters=(
                'list_id', 'slug', 'owner_screen_name', 'owner_id'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('user', list=True)
    def list_subscribers(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-subscribers
        """
        return self.request(
            'GET', 'lists/subscribers', endpoint_parameters=(
                'list_id', 'slug', 'owner_screen_name', 'owner_id', 'count',
                'cursor', 'include_entities', 'skip_status'
            ), **kwargs
        )

    @payload('user')
    def show_list_subscriber(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-subscribers-show
        """
        return self.request(
            'GET', 'lists/subscribers/show', endpoint_parameters=(
                'owner_screen_name', 'owner_id', 'list_id', 'slug', 'user_id',
                'screen_name', 'include_entities', 'skip_status'
            ), **kwargs
        )

    @payload('json')
    def trends_available(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/trends/locations-with-trending-topics/api-reference/get-trends-available
        """
        return self.request('GET', 'trends/available', **kwargs)

    @payload('json')
    def trends_place(self, id, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/trends/trends-for-location/api-reference/get-trends-place
        """
        return self.request(
            'GET', 'trends/place', endpoint_parameters=(
                'id', 'exclude'
            ), id=id, **kwargs
        )

    @payload('json')
    def trends_closest(self, lat, long, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/trends/locations-with-trending-topics/api-reference/get-trends-closest
        """
        return self.request(
            'GET', 'trends/closest', endpoint_parameters=(
                'lat', 'long'
            ), lat=lat, long=long, **kwargs
        )

    @pagination(mode='id')
    @payload('search_results')
    def search(self, q, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/search/api-reference/get-search-tweets
        """
        return self.request(
            'GET', 'search/tweets', endpoint_parameters=(
                'q', 'geocode', 'lang', 'locale', 'result_type', 'count',
                'until', 'since_id', 'max_id', 'include_entities'
            ), q=q, **kwargs
        )

    @pagination(mode='next')
    @payload('status', list=True)
    def search_30_day(self, label, query, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/premium/search-api/api-reference/premium-search
        """
        return self.request(
            'GET', f'tweets/search/30day/{label}', endpoint_parameters=(
                'query', 'tag', 'fromDate', 'toDate', 'maxResults', 'next'
            ), query=query, **kwargs
        )

    @pagination(mode='next')
    @payload('status', list=True)
    def search_full_archive(self, label, query, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/premium/search-api/api-reference/premium-search
        """
        return self.request(
            'GET', f'tweets/search/fullarchive/{label}', endpoint_parameters=(
                'query', 'tag', 'fromDate', 'toDate', 'maxResults', 'next'
            ), query=query, **kwargs
        )

    @payload('place', list=True)
    def reverse_geocode(self, lat, long, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/geo/places-near-location/api-reference/get-geo-reverse_geocode
        """
        return self.request(
            'GET', 'geo/reverse_geocode', endpoint_parameters=(
                'lat', 'long', 'accuracy', 'granularity', 'max_results'
            ), lat=lat, long=long, **kwargs
        )

    @payload('place')
    def geo_id(self, place_id, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/geo/place-information/api-reference/get-geo-id-place_id
        """
        return self.request('GET', f'geo/id/{place_id}', **kwargs)

    @payload('place', list=True)
    def geo_search(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/geo/places-near-location/api-reference/get-geo-search
        """
        return self.request(
            'GET', 'geo/search', endpoint_parameters=(
                'lat', 'long', 'query', 'ip', 'granularity', 'max_results'
            ), **kwargs
        )

    @payload('json')
    def supported_languages(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/developer-utilities/supported-languages/api-reference/get-help-languages
        """
        return self.request('GET', 'help/languages', **kwargs)

    @payload('json')
    def configuration(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/developer-utilities/configuration/api-reference/get-help-configuration
        """
        return self.request('GET', 'help/configuration', **kwargs)
