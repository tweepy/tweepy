# Tweepy
# Copyright 2009-2021 Joshua Roesslein
# See LICENSE for details.

"""
Tweepy Twitter API library
"""
__version__ = '3.10.0'
__author__ = 'Joshua Roesslein'
__license__ = 'MIT'

from tweepy.api import API
from tweepy.auth import AppAuthHandler, OAuthHandler
from tweepy.cache import Cache, FileCache, MemoryCache
from tweepy.cursor import Cursor
from tweepy.errors import (
    Forbidden, HTTPException, NotFound, TooManyRequests, TweepyException,
    Unauthorized
)
from tweepy.models import (
    DirectMessage, Friendship, ModelFactory, SavedSearch, SearchResults,
    Status, User
)
from tweepy.streaming import Stream

# Global, unauthenticated instance of API
api = API()

def debug(enable=True, level=1):
    from http.client import HTTPConnection
    HTTPConnection.debuglevel = level
