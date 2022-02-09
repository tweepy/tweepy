import random
import unittest

from config import *
from tweepy import API, OAuth1UserHandler


class TweepyAuthTests(unittest.TestCase):

    def testoauth(self):
        if not consumer_key or not consumer_secret:
            self.skipTest("Missing consumer key and/or secret")

        auth = OAuth1UserHandler(consumer_key, consumer_secret)

        # test getting access token
        auth_url = auth.get_authorization_url()
        print('Please authorize: ' + auth_url)
        verifier = input('PIN: ').strip()
        self.assertTrue(len(verifier) > 0)
        access_token = auth.get_access_token(verifier)
        self.assertTrue(access_token is not None)

        # build api object test using oauth
        api = API(auth)
        s = api.update_status(f'test {random.randint(0, 1000)}')
        api.destroy_status(s.id)

    def testaccesstype(self):
        if not consumer_key or not consumer_secret:
            self.skipTest("Missing consumer key and/or secret")

        auth = OAuth1UserHandler(consumer_key, consumer_secret)
        auth_url = auth.get_authorization_url(access_type='read')
        print('Please open: ' + auth_url)
        answer = input('Did Twitter only request read permissions? (y/n) ')
        self.assertEqual('y', answer.lower())
