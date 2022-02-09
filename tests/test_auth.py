import random
import unittest

from config import *
from tweepy import API, Client, OAuthHandler, OAuth2UserHandler


class TweepyAuthTests(unittest.TestCase):

    def testoauth(self):
        if not consumer_key or not consumer_secret:
            self.skipTest("Missing consumer key and/or secret")

        auth = OAuthHandler(consumer_key, consumer_secret)

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

        auth = OAuthHandler(consumer_key, consumer_secret)
        auth_url = auth.get_authorization_url(access_type='read')
        print('Please open: ' + auth_url)
        answer = input('Did Twitter only request read permissions? (y/n) ')
        self.assertEqual('y', answer.lower())

    def testoauth2(self):
        if not client_id or not client_secret:
            self.skipTest("Missing client id and/or secret")

        auth = OAuth2UserHandler(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri='http://localhost',
            scope=["offline.access", "tweet.read", "users.read"]
        )

        # test getting access token
        auth_url = auth.get_authorization_url()
        print('Please authorize: ' + auth_url)
        verifier = input('Redirected auth url: ').strip()
        self.assertTrue(len(verifier) > 0)
        tokens = auth.fetch_token(verifier)
        self.assertTrue('access_token' in tokens and tokens['access_token'])
        self.assertTrue('refresh_token' in tokens and tokens['refresh_token'])

        # build client object with bearer type OAuth2 access token
        client = Client(bearer_token=tokens['access_token'])
        me = client.get_me()
        self.assertTrue(me is not None)

        # build client object with refreshed access token
        tokens = auth.refresh_token(tokens['refresh_token'])
        client = Client(bearer_token=tokens['access_token'])
        me = client.get_me()
        self.assertTrue(me is not None)
