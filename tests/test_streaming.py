from __future__ import absolute_import, print_function

from .config import tape

import six
if six.PY3:
    import unittest
    from unittest.case import skip
else:
    import unittest2 as unittest
    from unittest2.case import skip

from tweepy.api import API
from tweepy.auth import OAuthHandler
from tweepy.models import Status
from tweepy.streaming import Stream, StreamListener, ReadBuffer

from .config import create_auth
from .test_utils import mock_tweet
from mock import MagicMock, patch


if six.PY3:
    getresponse_location = 'http.client.HTTPConnection.getresponse'
else:
    getresponse_location = 'httplib.HTTPConnection.getresponse'


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

    def on_error(self, code):
        print("response: %s" % code)
        return True

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

    def on_connect(self):
        API(self.auth).update_status(mock_tweet())

    def test_userstream(self):
        # Generate random tweet which should show up in the stream.

        self.listener.connect_cb = self.on_connect
        self.listener.status_stop_count = 1
        self.stream.userstream()
        self.assertEqual(self.listener.status_count, 1)

    @skip("Sitestream only available to whitelisted accounts.")
    def test_sitestream(self):
        self.listener.connect_cb = self.on_connect
        self.listener.status_stop_count = 1
        self.stream.sitestream(follow=[self.auth.get_username()])
        self.assertEqual(self.listener.status_count, 1)

    def test_userstream_with_params(self):
        # Generate random tweet which should show up in the stream.
        def on_connect():
            API(self.auth).update_status(mock_tweet())

        self.listener.connect_cb = on_connect
        self.listener.status_stop_count = 1
        self.stream.userstream(_with='user', replies='all', stall_warnings=True)
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

    def test_track_encoding(self):
        s = Stream(None, None)
        s._start = lambda async: None
        s.filter(track=[u'Caf\xe9'])

        # Should be UTF-8 encoded
        self.assertEqual(u'Caf\xe9'.encode('utf8'), s.session.params['track'])

    def test_follow_encoding(self):
        s = Stream(None, None)
        s._start = lambda async: None
        s.filter(follow=[u'Caf\xe9'])

        # Should be UTF-8 encoded
        self.assertEqual(u'Caf\xe9'.encode('utf8'), s.session.params['follow'])


class TweepyStreamReadBufferTests(unittest.TestCase):

    stream = six.b("""11\n{id:12345}\n\n24\n{id:23456, test:"blah"}\n""")

    def test_read_tweet(self):
        for length in [1, 2, 5, 10, 20, 50]:
            buf = ReadBuffer(six.BytesIO(self.stream), length)
            self.assertEqual('11\n', buf.read_line())
            self.assertEqual('{id:12345}\n', buf.read_len(11))
            self.assertEqual('\n', buf.read_line())
            self.assertEqual('24\n', buf.read_line())
            self.assertEqual('{id:23456, test:"blah"}\n', buf.read_len(24))

    def test_read_empty_buffer(self):
        """
        Requests can be closed by twitter.
        The ReadBuffer should not loop infinitely when this happens.
        Instead it should return and let the outer _read_loop handle it.
        """

        # If the test fails, we are in danger of an infinite loop
        # so we need to do some work to block that from happening
        class InfiniteLoopException(Exception):
            pass

        self.called_count = 0
        call_limit = 5
        def on_read(chunk_size):
            self.called_count += 1

            if self.called_count > call_limit:
                # we have failed
                raise InfiniteLoopException("Oops, read() was called a bunch of times")

            return ""

        # Create a fake stream
        stream = six.BytesIO(six.b(''))

        # Mock it's read function so it can't be called too many times
        mock_read = MagicMock(side_effect=on_read)

        try:
            stream.close()
            with patch.multiple(stream, create=True, read=mock_read):
                # Now the stream can't call 'read' more than call_limit times
                # and it looks like a requests stream that is closed
                buf = ReadBuffer(stream, 50)
                buf.read_line("\n")
        except InfiniteLoopException:
            self.fail("ReadBuffer.read_line tried to loop infinitely.")

        # The mocked function not have been called at all since the stream looks closed
        self.assertEqual(mock_read.call_count, 0)

    def test_read_unicode_tweet(self):
        stream = six.b('11\n{id:12345}\n\n23\n{id:23456, test:"\xe3\x81\x93"}\n\n')
        for length in [1, 2, 5, 10, 20, 50]:
            buf = ReadBuffer(six.BytesIO(stream), length)
            self.assertEqual('11\n', buf.read_line())
            self.assertEqual('{id:12345}\n', buf.read_len(11))
            self.assertEqual('\n', buf.read_line())
            self.assertEqual('23\n', buf.read_line())
            self.assertEqual(u'{id:23456, test:"\u3053"}\n', buf.read_len(23))


class TweepyStreamBackoffTests(unittest.TestCase):
    def setUp(self):
        #bad auth causes twitter to return 401 errors
        self.auth = OAuthHandler("bad-key", "bad-secret")
        self.auth.set_access_token("bad-token", "bad-token-secret")
        self.listener = MockStreamListener(self)
        self.stream = Stream(self.auth, self.listener)

    def tearDown(self):
        self.stream.disconnect()

    def test_exp_backoff(self):
        self.stream = Stream(self.auth, self.listener, timeout=3.0,
                             retry_count=1, retry_time=1.0, retry_time_cap=100.0)
        self.stream.sample()
        # 1 retry, should be 4x the retry_time
        self.assertEqual(self.stream.retry_time, 4.0)

    def test_exp_backoff_cap(self):
        self.stream = Stream(self.auth, self.listener, timeout=3.0,
                             retry_count=1, retry_time=1.0, retry_time_cap=3.0)
        self.stream.sample()
        # 1 retry, but 4x the retry_time exceeds the cap, so should be capped
        self.assertEqual(self.stream.retry_time, 3.0)

    mock_resp = MagicMock()
    mock_resp.return_value.status = 420

    @patch(getresponse_location, mock_resp)
    def test_420(self):
        self.stream = Stream(self.auth, self.listener, timeout=3.0, retry_count=0,
                             retry_time=1.0, retry_420=1.5, retry_time_cap=20.0)
        self.stream.sample()
        # no retries, but error 420, should be double the retry_420, not double the retry_time
        self.assertEqual(self.stream.retry_time, 3.0)
