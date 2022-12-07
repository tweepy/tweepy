# Tweepy
# Copyright 2009-2022 Joshua Roesslein
# See LICENSE for details.

import contextlib
import functools
import imghdr
import logging
import mimetypes
from platform import python_version
import sys
import time
from urllib.parse import urlencode
import json

import aiohttp

import tweepy
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


class AsyncAPI:
    def __init__(
        self, auth=None, *, cache=None, host='api.twitter.com', parser=None,
        proxy=None, retry_count=0, retry_delay=0, retry_errors=None,
        timeout=60, upload_host='upload.twitter.com', user_agent=None,
        wait_on_rate_limit=False
    ):
        self.auth = auth
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

        if user_agent is None:
            user_agent = (
                f"Python/{python_version()} "
                f"aiohttp/{aiohttp.__version__} "
                f"Tweepy/{tweepy.__version__}"
            )
        self.user_agent = user_agent

        self.wait_on_rate_limit = wait_on_rate_limit

        # Attempt to explain more clearly the parser argument requirements
        # https://github.com/tweepy/tweepy/issues/421

        if not isinstance(self.parser, Parser):
            raise TypeError(
                "parser should be an instance of Parser, not " +
                str(type(self.parser))
            )

        self.session = aiohttp.ClientSession()

    async def request(
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

        if headers is None:
            headers = {}
        headers["User-Agent"] = self.user_agent

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
            if k not in endpoint_parameters + (
                "include_ext_edit_control", "tweet_mode"
            ):
                await log.warning(f'Unexpected parameter: {k}')
            params[k] = str(arg)
        #params = json.dumps(params)
        log.debug("PARAMS: %r", params)
        print("BBBBBBB", type(params))

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
                        await log.warning(f"Rate limit reached. Sleeping for: {sleep_time}")
                        await time.sleep(sleep_time + 1)  # Sleep for extra sec

                # Apply authentication
                auth = None
                if self.auth:
                    auth = self.auth.apply_auth()

                # Compile FormData object
                formdata = aiohttp.FormData()
                # Add files data
                if files:
                    for key, value in files.items():
                        formdata.add_field(key, value)
                # Add post_data data
                if post_data:
                    for key, value in post_data.items():
                        formdata.add_field(key, value)
                
                print("AAAAAAAAAAAAAAAAAAAAAA",urlencode(params))
                print("CCCC", type(urlencode(params)))

                # Execute async request
                try:
                    async with self.session.request(
                        method, url, params=params, headers=headers,
                        data=formdata, json=json_payload, auth=auth,
                        timeout=self.timeout, proxy=self.proxy
                    ) as resp:
                        await resp.read()
                except Exception as e:
                    raise TweepyException(f'Failed to send request: {e}').with_traceback(sys.exc_info()[2])

                        
                if 200 <= resp.status < 300:
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
                if resp.status in (420, 429) and self.wait_on_rate_limit:
                    if remaining_calls == 0:
                        # If ran out of calls before waiting switching retry last call
                        continue
                    if 'retry-after' in resp.headers:
                        retry_delay = float(resp.headers['retry-after'])
                elif self.retry_errors and resp.status not in self.retry_errors:
                    # Exit request loop if non-retry error code
                    break

                # Sleep before retrying request again
                await time.sleep(retry_delay)
                retries_performed += 1

                # If an error was returned, throw an exception
                self.last_response = resp
                if resp.status == 400:
                    raise BadRequest(resp)
                if resp.status == 401:
                    raise Unauthorized(resp)
                if resp.status == 403:
                    raise Forbidden(resp)
                if resp.status == 404:
                    raise NotFound(resp)
                if resp.status == 429:
                    raise TooManyRequests(resp)
                if resp.status >= 500:
                    raise TwitterServerError(resp)
                if resp.status and not 200 <= resp.status_code < 300:
                    raise HTTPException(resp)

                # Parse the response payload
                return_cursors = return_cursors or 'cursor' in params or 'next' in params
                response_text = await resp.text()
                result = parser.parse(
                    response_text, api=self, payload_list=payload_list,
                    payload_type=payload_type, return_cursors=return_cursors
                )

                # Store result into cache if one is available.
                if use_cache and self.cache and method == 'GET' and result:
                    self.cache.store(f'{path}?{urlencode(params)}', result)

                return result
                
        finally:
            self.session.close()

        
    @payload('status')
    async def get_status(self, id, **kwargs):
        """get_status(id, *, trim_user, include_my_retweet, include_entities, \
                      include_ext_alt_text, include_card_uri)

        Asynchonous function to return a single status specified by the ID parameter.

        Parameters
        ----------
        id:
            |sid|
        trim_user
            |trim_user|
        include_my_retweet:
            A boolean indicating if any Tweets returned that have been
            retweeted by the authenticating user should include an additional
            current_user_retweet node, containing the ID of the source status
            for the retweet.
        include_entities
            |include_entities|
        include_ext_alt_text
            |include_ext_alt_text|
        include_card_uri
            |include_card_uri|

        Returns
        -------
        :class:`~tweepy.models.Status`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-statuses-show-id
        """
        return await self.request(
            'GET', 'statuses/show', endpoint_parameters=(
                'id', 'trim_user', 'include_my_retweet', 'include_entities',
                'include_ext_alt_text', 'include_card_uri'
            ), id=id, **kwargs
        )
    