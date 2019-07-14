from __future__ import absolute_import

import random
import unittest

from six.moves import input

from .config import *
from tweepy import API, OAuthHandler


class TweepyAuthTests(unittest.TestCase):

    def testoauth(self):
        auth = OAuthHandler(oauth_consumer_key, oauth_consumer_secret)

        # test getting access token
        auth_url = auth.get_authorization_url()
        print('Please authorize: ' + auth_url)
        verifier = input('PIN: ').strip()
        self.assertTrue(len(verifier) > 0)
        access_token = auth.get_access_token(verifier)
        self.assertTrue(access_token is not None)

        # build api object test using oauth
        api = API(auth)
        s = api.update_status('test %i' % random.randint(0, 1000))
        api.destroy_status(s.id)

    def testaccesstype(self):
        auth = OAuthHandler(oauth_consumer_key, oauth_consumer_secret)
        auth_url = auth.get_authorization_url(access_type='read')
        print('Please open: ' + auth_url)
        answer = input('Did Twitter only request read permissions? (y/n) ')
        self.assertEqual('y', answer.lower())
