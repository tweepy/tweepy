# Tweepy
# Copyright 2009 Joshua Roesslein
# See LICENSE

"""
Tweepy exception
"""
class TweepError(Exception):

  def __init__(self, reason):
    self.reason = reason

  def __str__(self):
    return self.reason
