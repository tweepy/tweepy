# Tweepy
# Copyright 2009-2010 Joshua Roesslein
# See LICENSE for details.

class TweepError(Exception):
    """Tweepy exception"""

    def __init__(self, reason, response=None, code=None):
        self.reason = unicode(reason)
        self.response = response
        if code is None and response is not None:
            self.code = response.status
        else:
            self.code = code

    def __str__(self):
        return self.reason

