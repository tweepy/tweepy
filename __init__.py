"""
Tweepy Twitter API library
"""
__version__ = '1.0'

from models import *
from error import TweepError
from api import API

# Global, unauthenticated instance of API
api = API()
