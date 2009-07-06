"""
Tweepy exception
"""
class TweepError(Exception):

  def __init__(self, reason):
    self.reason = reason

  def __str__(self):
    return self.reason
