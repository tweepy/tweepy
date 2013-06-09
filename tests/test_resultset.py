import unittest

from tweepy.models import ResultSet

class NoIdItem(object): pass

class IdItem(object):
    def __init__(self, id):
        self.id = id

ids_fixture = [1, 10, 8, 50, 2, 100, 5]

class TweepyResultSetTests(unittest.TestCase):
    def setUp(self):
        self.results = ResultSet()
        for i in ids_fixture:
            self.results.append(IdItem(i))
            self.results.append(NoIdItem())

    def testids(self):
        ids = self.results.ids()
        self.assertListEqual(ids, ids_fixture)

    def testmaxid(self):
        self.assertEqual(self.results.max_id, 100)

    def testsinceid(self):
        self.assertEqual(self.results.since_id, 1)

