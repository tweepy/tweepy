# Tweepy
# Copyright 2009-2021 Joshua Roesslein
# See LICENSE for details.

import logging
import sys
import time

import requests
from urllib.parse import quote, urlencode

from tweepy.error import is_rate_limit_error_message, RateLimitError, TweepError
from tweepy.models import Model

log = logging.getLogger(__name__)


def execute(api, method, path, *args, allowed_param=[], params=None,
            headers=None, json_payload=None, parser=None, payload_list=False,
            payload_type=None, post_data=None, require_auth=False,
            return_cursors=False, upload_api=False, use_cache=True, **kwargs):
    # If authentication is required and no credentials
    # are provided, throw an error.
    if require_auth and not api.auth:
        raise TweepError('Authentication required!')

    api.cached_result = False

    # Build the request URL
    if upload_api:
        url = api.upload_root + path
        full_url = 'https://' + api.upload_host + url
    else:
        url = api.api_root + path
        full_url = 'https://' + api.host + url

    if params is None:
        params = {}

    for idx, arg in enumerate(args):
        if arg is None:
            continue
        try:
            params[allowed_param[idx]] = str(arg)
        except IndexError:
            raise TweepError('Too many parameters supplied!')

    for k, arg in kwargs.items():
        if arg is None:
            continue
        if k in params:
            raise TweepError(f'Multiple values for parameter {k} supplied!')
        params[k] = str(arg)

    log.debug("PARAMS: %r", params)

    # Query the cache if one is available
    # and this request uses a GET method.
    if use_cache and api.cache and method == 'GET':
        cache_result = api.cache.get(f'{url}?{urlencode(params)}')
        # if cache result found and not expired, return it
        if cache_result:
            # must restore api reference
            if isinstance(cache_result, list):
                for result in cache_result:
                    if isinstance(result, Model):
                        result._api = api
            else:
                if isinstance(cache_result, Model):
                    cache_result._api = api
            api.cached_result = True
            return cache_result

    # Monitoring rate limits
    remaining_calls = None
    reset_time = None

    session = requests.Session()

    if parser is None:
        parser = api.parser

    try:
        # Continue attempting request until successful
        # or maximum number of retries is reached.
        retries_performed = 0
        while retries_performed <= api.retry_count:
            if (api.wait_on_rate_limit and reset_time is not None
                and remaining_calls is not None
                and remaining_calls < 1):
                # Handle running out of API calls
                sleep_time = reset_time - int(time.time())
                if sleep_time > 0:
                    log.warning(f"Rate limit reached. Sleeping for: {sleep_time}")
                    time.sleep(sleep_time + 1)  # Sleep for extra sec

            # Apply authentication
            auth = None
            if api.auth:
                auth = api.auth.apply_auth()

            # Execute request
            try:
                resp = session.request(
                    method, full_url, params=params, headers=headers,
                    data=post_data, json=json_payload, timeout=api.timeout,
                    auth=auth, proxies=api.proxy
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

            retry_delay = api.retry_delay
            if resp.status_code in (420, 429) and api.wait_on_rate_limit:
                if remaining_calls == 0:
                    # If ran out of calls before waiting switching retry last call
                    continue
                if 'retry-after' in resp.headers:
                    retry_delay = float(resp.headers['retry-after'])
            elif api.retry_errors and resp.status_code not in api.retry_errors:
                # Exit request loop if non-retry error code
                break

            # Sleep before retrying request again
            time.sleep(retry_delay)
            retries_performed += 1

        # If an error was returned, throw an exception
        api.last_response = resp
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
            resp.text, api=api, payload_list=payload_list,
            payload_type=payload_type, return_cursors=return_cursors
        )

        # Store result into cache if one is available.
        if use_cache and api.cache and method == 'GET' and result:
            api.cache.store(f'{url}?{urlencode(params)}', result)

        return result
    finally:
        session.close()


def bind_api(api, method, *args, **kwargs):
    path = kwargs.pop('path')
    return execute(api, method, path, *args, **kwargs)


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
