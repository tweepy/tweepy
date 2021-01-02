# Tweepy
# Copyright 2009-2021 Joshua Roesslein
# See LICENSE for details.

"""
Tweepy.asynchronoous

Asynchronous interfaces with the Twitter API
"""

try:
    import aiohttp
except ModuleNotFoundError:
    from tweepy.error import TweepError
    raise TweepError("tweepy.asynchronous requires aiohttp to be installed")

from tweepy.asynchronous.streaming import AsyncStream
