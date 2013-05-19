from time import sleep
import unittest

from tweepy.api import API
from tweepy.streaming import Stream, StreamListener

from config import create_auth
from mock import mock_tweet

class MockStreamListener(StreamListener):
    def __init__(self):
        super(MockStreamListener, self).__init__()
        self.status_count = 0

    def on_status(self, status):
        self.status_count += 1
        return False

class TweepyStreamTests(unittest.TestCase):
    def setUp(self):
        self.auth = create_auth()
        self.listener = MockStreamListener()
        self.stream = Stream(self.auth, self.listener)

    def tearDown(self):
        self.stream.disconnect()

    def test_userstream(self):
        self.stream.userstream(async=True)

        # Generate random tweet which should show up in the stream.
        # Wait a bit of time for it to arrive before asserting.
        API(self.auth).update_status(mock_tweet())
        sleep(1)

        self.assertEqual(self.listener.status_count, 1)

