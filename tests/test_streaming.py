from time import sleep
import unittest2 as unittest

from tweepy.api import API
from tweepy.models import Status
from tweepy.streaming import Stream, StreamListener

from config import create_auth
from mock import mock_tweet

class MockStreamListener(StreamListener):
    def __init__(self, test_case):
        super(MockStreamListener, self).__init__()
        self.test_case = test_case
        self.status_count = 0
        self.status_stop_count = 0
        self.connect_cb = None

    def on_connect(self):
        if self.connect_cb:
            self.connect_cb()

    def on_timeout(self):
        self.test_case.fail('timeout')
        return False

    def on_status(self, status):
        self.status_count += 1
        self.test_case.assertIsInstance(status, Status)
        if self.status_stop_count == self.status_count:
            return False

class TweepyStreamTests(unittest.TestCase):
    def setUp(self):
        self.auth = create_auth()
        self.listener = MockStreamListener(self)
        self.stream = Stream(self.auth, self.listener, timeout=3.0)

    def tearDown(self):
        self.stream.disconnect()

    def test_userstream(self):
        # Generate random tweet which should show up in the stream.
        def on_connect():
            API(self.auth).update_status(mock_tweet())

        self.listener.connect_cb = on_connect
        self.listener.status_stop_count = 1
        self.stream.userstream()
        self.assertEqual(self.listener.status_count, 1)

    def test_sample(self):
        self.listener.status_stop_count = 10
        self.stream.sample()
        self.assertEquals(self.listener.status_count,
                          self.listener.status_stop_count)

    def test_filter_track(self):
        self.listener.status_stop_count = 5
        phrases = ['twitter']
        self.stream.filter(track=phrases)
        self.assertEquals(self.listener.status_count,
                          self.listener.status_stop_count)

    def test_on_data(self):        
        test_wrong_data = [
            '{"disc', # this is actual data read from twitter
            '600',    # this is actual data read from twitter
            '41\n',   # this is actual data read from twitter
            'obviously non-json',
            '"json but not dict"',
			'{"json dict":"but not a twitter message"}'
        ]        
        for raw_data in test_wrong_data: 
            # should log errors but not raise / not return False
            self.assertEquals(self.listener.on_data(raw_data), None)
            self.assertEquals(self.listener.status_count, 0)
