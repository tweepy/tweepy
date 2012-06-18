# Tweepy
# Copyright 2009-2010 Joshua Roesslein
# See LICENSE for details.

"""
Tweepy Twitter API library
"""
__version__ = '1.9'
__author__ = 'Joshua Roesslein'
__license__ = 'MIT'

from .models import Status, User, DirectMessage, Friendship, SavedSearch, SearchResult, ModelFactory
from .error import TweepError
from .api import API
from .cache import Cache, MemoryCache, FileCache
from .auth import BasicAuthHandler, OAuthHandler
from .streaming import Stream, StreamListener
from .cursor import Cursor

# Global, unauthenticated instance of API
api = API()

def debug(enable=True, level=1):

    try: #python3
        import http
        http.client.HTTPConnection.debuglevel = level
    except:
        import httplib
        httplib.HTTPConnection.debuglevel = level

