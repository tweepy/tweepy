# Tweepy
# Copyright 2009 Joshua Roesslein
# See LICENSE

class TweepError(Exception):
    """Tweepy exception"""

    def __init__(self, reason):
        self.reason = str(reason)

    def __str__(self):
        return self.reason

