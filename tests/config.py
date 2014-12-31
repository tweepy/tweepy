import os

import vcr

from tweepy.auth import OAuthHandler
from tweepy.api import API

import six
if six.PY3:
    import unittest
else:
    import unittest2 as unittest

username = os.environ.get('TWITTER_USERNAME', 'tweepytest')
oauth_consumer_key = os.environ.get('CONSUMER_KEY', '')
oauth_consumer_secret = os.environ.get('CONSUMER_SECRET', '')
oauth_token = os.environ.get('ACCESS_KEY', '')
oauth_token_secret = os.environ.get('ACCESS_SECRET', '')
use_replay = os.environ.get('USE_REPLAY', False)


tape = vcr.VCR(
    cassette_library_dir='cassettes',
    filter_headers=['Authorization'],
    serializer='json',
    # Either use existing cassettes, or never use recordings:
    record_mode='none' if use_replay else 'all',
)


class TweepyTestCase(unittest.TestCase):
    def setUp(self):
        self.auth = create_auth()
        self.api = API(self.auth)
        self.api.retry_count = 2
        self.api.retry_delay = 5


def create_auth():
    auth = OAuthHandler(oauth_consumer_key, oauth_consumer_secret)
    auth.set_access_token(oauth_token, oauth_token_secret)
    return auth
