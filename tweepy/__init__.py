# Tweepy
# Copyright 2009-2010 Joshua Roesslein
# See LICENSE for details.

"""
Tweepy Twitter API library
"""
__version__ = '3.5.0'
__author__ = 'Joshua Roesslein'
__license__ = 'MIT'

from tweepy.models import Status, User, DirectMessage, Friendship, SavedSearch, SearchResults, ModelFactory, Category
from tweepy.error import TweepError, RateLimitError
from tweepy.api import API
from tweepy.cache import Cache, MemoryCache, FileCache
from tweepy.auth import OAuthHandler, AppAuthHandler
from tweepy.streaming import Stream, StreamListener
from tweepy.cursor import Cursor

# Global, unauthenticated instance of API
api = API()

def debug(enable=True, level=1):
    from six.moves.http_client import HTTPConnection
    HTTPConnection.debuglevel = level
