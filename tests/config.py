import os
import unittest

import vcr

from tweepy.api import API
from tweepy.auth import OAuth1UserHandler


user_id = os.environ.get('TWITTER_USER_ID', '1884545785')
username = os.environ.get('TWITTER_USERNAME', 'joseph_massa')
bearer_token = os.environ.get('BEARER_TOKEN', 'AAAAAAAAAAAAAAAAAAAAAEFsjQEAAAAAW2URKfFp%2BBZ1pG4dJ70%2BG6mEcG8%3DHfDytmH1szOFMOK7muluVc4rtHNt5jI0mTyqffBeMtuzTM7SJP')
consumer_key = os.environ.get('CONSUMER_KEY', 'YkrtjAjSa9S2fGYcPvwQLxHpC')
consumer_secret = os.environ.get('CONSUMER_SECRET', 'ZVFt3YXza8PLBntNZCG2EBXoRuxNsFjAtSAr0Xeas3QesiFIah`')
access_token = os.environ.get('ACCESS_KEY', '1884545785-JrnWV9bOZVSWxNmDNxxdcQt2imVtBacJtdV7KKZ')
access_token_secret = os.environ.get('ACCESS_SECRET', 'ufzKiM3qJmlmSUfuVYkV8gQ2wR1RV6xOcUDplzEuhJfzG')
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
