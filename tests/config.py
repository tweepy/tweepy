import os
import sys
from unittest2 import TestCase

from httreplay import start_replay, stop_replay
from httreplay.utils import filter_headers_key

from tweepy.auth import OAuthHandler
from tweepy.api import API

username = os.environ.get('TWITTER_USERNAME', 'tweepytest')
oauth_consumer_key = os.environ.get('CONSUMER_KEY', '')
oauth_consumer_secret = os.environ.get('CONSUMER_SECRET', '')
oauth_token = os.environ.get('ACCESS_KEY', '')
oauth_token_secret = os.environ.get('ACCESS_SECRET', '')
use_replay = os.environ.get('USE_REPLAY', False)

class TweepyTestCase(TestCase):

    def setUp(self):
        self.auth = create_auth()
        self.api = API(self.auth)
        self.api.retry_count = 2
        self.api.retry_delay = 5

        if use_replay:
            def filter_body(data): return ''
            start_replay('tests/record.json',
                         headers_key=filter_headers_key(['Authorization']),
                         body_key=filter_body)

    def tearDown(self):
        if use_replay:
            stop_replay()

def create_auth():
    auth = OAuthHandler(oauth_consumer_key, oauth_consumer_secret)
    auth.set_access_token(oauth_token, oauth_token_secret)
    return auth

