import unittest

from tweepy import API, Cursor

from config import create_auth

class TweepyCursorTests(unittest.TestCase):

    def setUp(self):
        self.api = API(create_auth())
        self.api.retry_count = 2
        self.api.retry_delay = 5

    def testidcursoritems(self):
        items = list(Cursor(self.api.user_timeline).items(25))
        self.assertEqual(len(items), 25)

    def testidcursorpages(self):
        pages = list(Cursor(self.api.user_timeline).pages(5))
        self.assertEqual(len(pages), 5)

    def testcursorcursoritems(self):
        items = list(Cursor(self.api.friends_ids).items())
        self.assert_(len(items) > 0)

        items = list(Cursor(self.api.followers_ids, 'twitter').items(30))
        self.assert_(len(items) == 30)

    def testcursorcursorpages(self):
        pages = list(Cursor(self.api.friends_ids).pages())
        self.assert_(len(pages) > 0)

        pages = list(Cursor(self.api.followers_ids, 'twitter').pages(5))
        self.assert_(len(pages) == 5)

