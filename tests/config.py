import os
import unittest

import vcr

from tweepy.api import API
from tweepy.auth import OAuthHandler


user_id = os.environ.get('TWITTER_USER_ID', '1072250532645998596')
username = os.environ.get('TWITTER_USERNAME', 'TweepyDev')
bearer_token = os.environ.get('BEARER_TOKEN', '')
client_id = os.environ.get('CLIENT_ID', '')
client_secret = os.environ.get('CLIENT_SECRET', '')
consumer_key = os.environ.get('CONSUMER_KEY', '')
consumer_secret = os.environ.get('CONSUMER_SECRET', '')
access_token = os.environ.get('ACCESS_KEY', '')
access_token_secret = os.environ.get('ACCESS_SECRET', '')
use_replay = os.environ.get('USE_REPLAY', True)
# Uncomment if using non-https redirect uris [in development]
# os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


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
        self.api.retry_delay = 0 if use_replay else 5


def create_auth():
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    return auth
