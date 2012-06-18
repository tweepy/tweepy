# Tweepy
# Copyright 2009-2010 Joshua Roesslein
# See LICENSE for details.
import sys
PY_MAJOR_VERSION = sys.version_info.major
class TweepError(Exception):
    """Tweepy exception"""

    def __init__(self, reason, response=None):
        if PY_MAJOR_VERSION == 3 :
            self.reason = reason
        else :
            self.reason = unicode(reason)
        self.response = response

    def __str__(self):
        return self.reason

