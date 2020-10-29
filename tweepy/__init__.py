# Tweepy
# Copyright 2009-2020 Joshua Roesslein
# See LICENSE for details.

"""
Tweepy Twitter API library
"""
__version__ = '3.9.0'
__author__ = 'Joshua Roesslein'
__license__ = 'MIT'

from tweepy.api import API
from tweepy.auth import AppAuthHandler, OAuthHandler
from tweepy.cache import Cache, FileCache, MemoryCache
from tweepy.cursor import Cursor
from tweepy.error import RateLimitError, TweepError
from tweepy.models import DirectMessage, Friendship, ModelFactory, SavedSearch, SearchResults, Status, User
from tweepy.streaming import Stream, StreamListener

# Global, unauthenticated instance of API
api = API()

def debug(enable=True, level=1):
    from six.moves.http_client import HTTPConnection
    HTTPConnection.debuglevel = level
