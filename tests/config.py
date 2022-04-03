import os
import unittest

import vcr

from tweepy.api import API
from tweepy.auth import OAuth1UserHandler


user_id = os.environ.get('TWITTER_USER_ID', '1072250532645998596')
username = os.environ.get('TWITTER_USERNAME', 'TweepyDev')
bearer_token = os.environ.get('BEARER_TOKEN', '')
consumer_key = os.environ.get('CONSUMER_KEY', '')
consumer_secret = os.environ.get('CONSUMER_SECRET', '')
access_token = os.environ.get('ACCESS_KEY', '')
access_token_secret = os.environ.get('ACCESS_SECRET', '')
use_replay = os.environ.get('USE_REPLAY', True)


tape = vcr.VCR(
    cassette_library_dir='cassettes',
    filter_headers=['Authorization'],
    # Either use existing cassettes, or never use recordings:
    record_mode='none' if use_replay else 'all',
)


class TweepyTestCase(unittest.TestCase):
    def setUp(self):
        self.auth = create_auth()
        self.api = API(self.auth)
        self.api.retry_count = 2
        self.api.retry_delay = 0 if use_replay else 5


def create_auth():
    auth = OAuth1UserHandler(
        consumer_key, consumer_secret, access_token, access_token_secret
    )
    return auth
