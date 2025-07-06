import pickle
import unittest

from tweepy.tweet import Tweet


class TweepyTweetTests(unittest.TestCase):
    def test_tweet(self):
        t = Tweet(
            data={
                "edit_history_tweet_ids": ["16213149247090909"],
                "id": "16213149247090909",
                "text": "We're super excited to not only welcome the Flamingo Janes in...",
            }
        )

        pickled_tweet = pickle.dumps(t)
        t2 = pickle.loads(pickled_tweet)

        self.assertDictEqual(t.data, t2.data)