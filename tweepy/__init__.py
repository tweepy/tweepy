# Tweepy
# Copyright 2009-2021 Joshua Roesslein
# See LICENSE for details.

"""
Tweepy Twitter API library
"""
__version__ = '4.0.1'
__author__ = 'Joshua Roesslein'
__license__ = 'MIT'

from tweepy.api import API
from tweepy.auth import AppAuthHandler, OAuthHandler
from tweepy.cache import Cache, FileCache, MemoryCache
from tweepy.client import Client, Response
from tweepy.cursor import Cursor
from tweepy.errors import (
    BadRequest, Forbidden, HTTPException, NotFound, TooManyRequests,
    TweepyException, TwitterServerError, Unauthorized
)
from tweepy.media import Media
from tweepy.pagination import Paginator
from tweepy.place import Place
from tweepy.poll import Poll
from tweepy.streaming import Stream
from tweepy.tweet import ReferencedTweet, Tweet
from tweepy.user import User

# Global, unauthenticated instance of API
api = API()

def debug(enable=True, level=1):
    from http.client import HTTPConnection
    HTTPConnection.debuglevel = level
