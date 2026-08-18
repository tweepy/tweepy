import unittest

from config import tape, TweepyTestCase, username
from tweepy import Cursor
from tweepy.cursor import CursorIterator


class TweepyCursorTests(TweepyTestCase):
    @tape.use_cassette('testidcursoritems.json', serializer='json')
    def testidcursoritems(self):
        items = list(Cursor(self.api.user_timeline).items(2))
        self.assertEqual(len(items), 2)

    @tape.use_cassette('testidcursorpages.json', serializer='json')
    def testidcursorpages(self):
        pages = list(Cursor(self.api.user_timeline, count=1).pages(2))
        self.assertEqual(len(pages), 2)

    @tape.use_cassette('testcursorcursoritems.yaml')
    def testcursorcursoritems(self):
        items = list(Cursor(self.api.get_friend_ids).items(2))
        self.assertEqual(len(items), 2)

        items = list(Cursor(self.api.get_follower_ids, screen_name=username).items(1))
        self.assertEqual(len(items), 1)

    @tape.use_cassette('testcursorcursorpages.yaml')
    def testcursorcursorpages(self):
        pages = list(Cursor(self.api.get_friend_ids).pages(1))
        self.assertTrue(len(pages) == 1)

        pages = list(Cursor(self.api.get_follower_ids, screen_name=username).pages(1))
        self.assertTrue(len(pages) == 1)

    @tape.use_cassette('testcursorsetstartcursor.json')
    def testcursorsetstartcursor(self):
        c = Cursor(self.api.get_friend_ids, cursor=123456)
        self.assertEqual(c.iterator.next_cursor, 123456)
        self.assertFalse('cursor' in c.iterator.kwargs)

    @tape.use_cassette('testcursornext.yaml')
    def testcursornext(self):
        """
        Test next(cursor) behavior, screen name being passed correctly.
        Regression test for issue #518
        """
        cursor = Cursor(self.api.user_timeline, screen_name='Twitter').items(5)
        status = next(cursor)

        self.assertEqual(status.user.screen_name, 'Twitter')


class CursorIteratorTests(unittest.TestCase):
    def test_prev_and_next_unpack_cursors(self):
        # Cursor-mode methods return (data, (prev_cursor, next_cursor)).
        # prev() used to unpack that 2-tuple into three targets and raise
        # ValueError; it now mirrors next().
        def method(cursor=None, *args, **kwargs):
            return (["data"], (5, 10))

        it = CursorIterator(method)
        self.assertEqual(it.next(), ["data"])
        self.assertEqual((it.prev_cursor, it.next_cursor), (5, 10))

        it.prev_cursor = 7
        self.assertEqual(it.prev(), ["data"])
        self.assertEqual((it.prev_cursor, it.next_cursor), (5, 10))
