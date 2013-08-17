import unittest

from tweepy import API, Cursor

from config import create_auth

class TweepyCursorTests(unittest.TestCase):

    def setUp(self):
        self.api = API(create_auth())

    def testidcursoritems(self):
        items = list(Cursor(self.api.user_timeline).items(25))
        self.assertEqual(len(items), 25)

    def testidcursorpages(self):
        pages = list(Cursor(self.api.user_timeline).pages(5))
        self.assertEqual(len(pages), 5)

    def testcursorcursoritems(self):
        items = list(Cursor(self.api.friends_ids).items(10))
        self.assertEqual(len(items), 10)

        items = list(Cursor(self.api.followers_ids, 'twitter').items(10))
        self.assertEqual(len(items), 10)

    def testcursorcursorpages(self):
        pages = list(Cursor(self.api.friends_ids).pages(1))
        self.assert_(len(pages) == 1)

        pages = list(Cursor(self.api.followers_ids, 'twitter').pages(1))
        self.assert_(len(pages) == 1)

