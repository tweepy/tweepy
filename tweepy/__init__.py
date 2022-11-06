# Tweepy
# Copyright 2009-2022 Joshua Roesslein
# See LICENSE for details.

"""
Tweepy Twitter API library
"""
__version__ = '4.12.1'
__author__ = 'Joshua Roesslein'
__license__ = 'MIT'

from tweepy.api import API
from tweepy.auth import (
    AppAuthHandler, OAuthHandler, OAuth1UserHandler, OAuth2AppHandler,
    OAuth2BearerHandler, OAuth2UserHandler
)
from tweepy.cache import Cache, FileCache, MemoryCache
from tweepy.client import Client, Response
from tweepy.cursor import Cursor
from tweepy.direct_message_event import DirectMessageEvent
from tweepy.errors import (
    BadRequest, Forbidden, HTTPException, NotFound, TooManyRequests,
    TweepyException, TwitterServerError, Unauthorized
)
from tweepy.list import List
from tweepy.media import Media
from tweepy.pagination import Paginator
from tweepy.place import Place
from tweepy.poll import Poll
from tweepy.space import Space
from tweepy.streaming import (
    Stream, StreamingClient, StreamResponse, StreamRule
)
from tweepy.tweet import ReferencedTweet, Tweet
from tweepy.user import User

# Global, unauthenticated instance of API
api = API()
