# Tweepy
# Copyright 2009-2010 Joshua Roesslein
# See LICENSE for details.

"""
Tweepy Twitter API library
"""
__version__ = '2.3'
__author__ = 'Joshua Roesslein'
__license__ = 'MIT'

from tweepy.api import API

# Global, unauthenticated instance of API
api = API()


def debug(enable=True, level=1):

    import httplib
    httplib.HTTPConnection.debuglevel = level
