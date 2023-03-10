import os
import shutil
import time
import unittest
from ast import literal_eval

from config import tape, username, create_auth, use_replay
from tweepy import API, FileCache, MemoryCache
from tweepy.models import Friendship
from tweepy.parsers import Parser
from tweepy.asynchronous import AsyncAPI

try:
    from unittest import IsolatedAsyncioTestCase
except ImportError:
    from unittest import SkipTest
    raise SkipTest("Skipping AsyncClient tests for Python 3.7")

test_tweet_id = '1599814673506963457'
tweet_text = 'testing 1000'

"""Unit tests"""


class TweepyAsyncAPITests(IsolatedAsyncioTestCase):

    def setUp(self):
        self.auth = create_auth()
        self.api = AsyncAPI(self.auth)
        self.api.retry_count = 2
        self.api.retry_delay = 0 if use_replay else 5

    #@tape.use_cassette('testasyncgetstatus.json', serializer='json')
    async def testasyncgetstatus(self):
        tweet = await self.api.get_status(id=test_tweet_id)
        self.assertEqual(tweet.text, "We've completed our return powered flyby burn and are heading home! https://t.co/awelzovlRP")
    

if __name__ == '__main__':
    unittest.main()
