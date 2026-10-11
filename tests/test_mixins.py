import unittest

from tweepy import DirectMessageEvent, List, Place, Poll, Space, Tweet, User
from tweepy.tweet import ReferencedTweet


class TweepyHashableIDTests(unittest.TestCase):
    objects = (
        (List, {"id": "123", "name": "Test list"}),
        (Place, {"id": "01a9a39529b27f36", "full_name": "Test place"}),
        (Poll, {"id": "123", "options": []}),
        (Space, {"id": "1YpKkzBgBlVxj", "state": "live"}),
        (DirectMessageEvent, {"id": "123", "event_type": "MessageCreate"}),
        (ReferencedTweet, {"id": "123", "type": "replied_to"}),
        (Tweet, {"id": "123", "text": "Test tweet",
                 "edit_history_tweet_ids": ["123"]}),
        (User, {"id": "123", "name": "Test user", "username": "testuser"}),
    )

    def test_hash_matches_identifier(self):
        for cls, data in self.objects:
            with self.subTest(cls=cls.__name__):
                obj = cls(data.copy())
                self.assertEqual(hash(obj), hash(obj.id))

    def test_equal_objects_deduplicate_in_sets(self):
        for cls, data in self.objects:
            with self.subTest(cls=cls.__name__):
                first = cls(data.copy())
                second = cls(data.copy())
                self.assertEqual(first, second)
                self.assertEqual(len({first, second}), 1)

    def test_equal_objects_retrieve_dictionary_values(self):
        for cls, data in self.objects:
            with self.subTest(cls=cls.__name__):
                first = cls(data.copy())
                second = cls(data.copy())
                values = {first: "stored value"}
                self.assertEqual(values[second], "stored value")

    def test_different_ids_remain_distinct(self):
        for cls, data in self.objects:
            with self.subTest(cls=cls.__name__):
                first = cls(data.copy())
                second = cls(dict(data, id=data["id"] + "1"))
                self.assertNotEqual(first, second)
                self.assertEqual(len({first, second}), 2)
