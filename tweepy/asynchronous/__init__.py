# Tweepy
# Copyright 2009-2023 Joshua Roesslein
# See LICENSE for details.

"""
Tweepy.asynchronoous

Asynchronous interfaces with the Twitter API
"""

try:
    import aiohttp
    import async_lru
    import oauthlib
except ModuleNotFoundError:
    from tweepy.errors import TweepyException
    raise TweepyException(
        "tweepy.asynchronous requires aiohttp, async_lru, and oauthlib to be "
        "installed"
    )

from tweepy.asynchronous.client import AsyncClient
from tweepy.asynchronous.pagination import AsyncPaginator
from tweepy.asynchronous.streaming import AsyncStreamingClient
