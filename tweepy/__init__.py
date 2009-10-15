# Tweepy
# Copyright 2009 Joshua Roesslein
# See LICENSE

"""
Tweepy Twitter API library
"""
__version__ = '1.2'

from tweepy.models import Status, User, DirectMessage, Friendship, SavedSearch, SearchResult, models
from tweepy.error import TweepError
from tweepy.api import API
from tweepy.cache import Cache, MemoryCache, FileCache, MemCache
from tweepy.auth import BasicAuthHandler, OAuthHandler
from tweepy.streaming import Stream, StreamListener
from tweepy.cursor import Cursor

# Global, unauthenticated instance of API
api = API()

