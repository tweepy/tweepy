import random
import string
import unittest

from tweepy.utils import *


def mock_tweet():
    """Generate some random tweet text."""
    count = random.randint(70, 140)
    return ''.join([random.choice(string.ascii_letters) for _ in range(count)])


class TweepyUtilsTests(unittest.TestCase):

    def testlist_to_csv(self):
        self.assertEqual("1,2,3", list_to_csv([1,2,3]))
        self.assertEqual("bird,tweet,nest,egg",
                         list_to_csv(["bird", "tweet", "nest", "egg"]))
