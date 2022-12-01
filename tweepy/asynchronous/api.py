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

import requests

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
                f"Requests/{requests.__version__} "
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

        self.session = requests.Session()

    
    