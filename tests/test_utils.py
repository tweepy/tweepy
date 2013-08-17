from unittest import TestCase

from tweepy.utils import *

class TweepyUtilsTests(TestCase):

    def testparse_datetime(self):
        result = parse_datetime("Wed Aug 27 13:08:45 +0000 2008")
        self.assertEqual(datetime(2008, 8, 27, 13, 8, 45), result)

