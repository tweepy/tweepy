from .config import tape, TweepyTestCase, username
from tweepy import Cursor


class TweepyCursorTests(TweepyTestCase):
    @tape.use_cassette('testidcursoritems.json')
    def testidcursoritems(self):
        items = list(Cursor(self.api.user_timeline).items(2))
        self.assertEqual(len(items), 2)

    @tape.use_cassette('testidcursorpages.json')
    def testidcursorpages(self):
        pages = list(Cursor(self.api.user_timeline, count=1).pages(2))
        self.assertEqual(len(pages), 2)

    @tape.use_cassette('testcursorcursoritems.json')
    def testcursorcursoritems(self):
        items = list(Cursor(self.api.friends_ids).items(2))
        self.assertEqual(len(items), 2)

        items = list(Cursor(self.api.followers_ids, username).items(1))
        self.assertEqual(len(items), 1)

    @tape.use_cassette('testcursorcursorpages.json')
    def testcursorcursorpages(self):
        pages = list(Cursor(self.api.friends_ids).pages(1))
        self.assertTrue(len(pages) == 1)

        pages = list(Cursor(self.api.followers_ids, username).pages(1))
        self.assertTrue(len(pages) == 1)

    @tape.use_cassette('testcursorsetstartcursor.json')
    def testcursorsetstartcursor(self):
        c = Cursor(self.api.friends_ids, cursor=123456)
        self.assertEqual(c.iterator.next_cursor, 123456)
        self.assertFalse('cursor' in c.iterator.kargs)

    @tape.use_cassette('testcursornext.json')
    def testcursornext(self):
        """
        Test cursor.next() behavior, id being passed correctly.
        Regression test for issue #518
        """
        cursor = Cursor(self.api.user_timeline, id='Twitter').items(5)
        status = cursor.next()

        self.assertEqual(status.user.screen_name, 'Twitter')
