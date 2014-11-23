# Tweepy
# Copyright 2009-2010 Joshua Roesslein
# Copyright 2014 Alexandru Stanciu (@ducu)
# See LICENSE for details.

# import time

from tweepy.api import API
from tweepy.auth import OAuthHandler
from tweepy.error import TweepError

from tweepy.utils import clean_path


class RateLimitHandler(OAuthHandler):
    """
    OAuth authentication handler
    containing a pool of access tokens that are used selectively
    based on requested resource and current rate limits. The
    access token with most remaining requests per window for the
    specified resource is being selected and used when applying 
    the authentication, before the actual request is performed.
    This pattern ensures the usage of available access tokens in
    a round robin fashion, exploiting to maximum the rate limits.
    """
    # tokens = {} # static
    nolimits = {u'limit': None, u'remaining': None, u'reset': None}

    def __init__(self, consumer_key, consumer_secret):
        "Init tokens for current instance."
        super(RateLimitHandler, self).__init__(consumer_key, consumer_secret)
        
        self.tokens = {} # instance
        # The pool of access tokens looks like this:
        # tokens = {
        #   access_token_key: {
        #     u'secret': access_token_secret,
        #     u'resources' : {
        #       resource: { u'limit': limit, 
        #         u'remaining': remaining, u'reset': reset }
        #     }
        #   }
        # }
        self.fixed_access_token = None # e.g. for home_timeline

    def _parse_limits(self, limits):
        return limits and (limits.get('limit'), 
            limits.get('remaining'), limits.get('reset')) or \
            (None, None, None) # no limits

    
    def _get_rate_limit_status(self, key, secret):
        """
        Get rate limit status for specified access token key.
        """
        auth = OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(key, secret)
        api = API(auth)
        return api.rate_limit_status()

    def _load_rate_limit_status(self, key, rate_limit_status):
        """
        Load resources rate limits into token pool structure.
        """
        self.tokens[key]['resources'] = dict(
            [(clean_path(r), rd[r]) \
            for c, rd in rate_limit_status['resources'].iteritems() \
            for r in rd.keys()]
        )


    def add_access_token(self, key, secret):
        """
        Add the access token key and secret to the pool, 
        and call the API to load its resources rate limits.
        Invalid or expired token error may be raised.
        """
        assert key not in self.tokens
        rls = self._get_rate_limit_status(key, secret) # may raise

        self.tokens[key] = {u'secret': secret, u'resources': {}}
        self._load_rate_limit_status(key, rls)

    def select_access_token(self, resource):
        """
        When the current token runs out of remaining calls, 
        cycle through all available tokens to find either
        the one with most remaining calls per specified
        resource, or if all of them ran out of calls, find
        the one with the first reset time. Don't forget to
        `set_access_token` to prepare for upcoming request.
        Make sure you `clean_path` the resource upfront.
        """
        assert len(self.tokens) # at least one token

        if not self.fixed_access_token: # autoselect
            key = self.access_token or self.tokens.keys()[0] # current

            limits = self.tokens[key]['resources'].get(resource)
            limit, remaining, reset = self._parse_limits(limits)

            if remaining == 0:
                key, limits = max(
                    [(k, sr['resources'].get(resource, self.nolimits)) \
                    for k, sr in self.tokens.iteritems()],
                    key=lambda t: t[1]['remaining']
                ) # most remaining calls per resource
                limit, remaining, reset = self._parse_limits(limits)

            if remaining == 0:
                key, limits = min(
                    [(k, sr['resources'].get(resource, self.nolimits)) \
                    for k, sr in self.tokens.iteritems()],
                    key=lambda t: t[1]['reset']
                ) # first reset time per resource
                limit, remaining, reset = self._parse_limits(limits)
        else: # fixed_access_token
            key = self.fixed_access_token

            limits = self.tokens[key]['resources'].get(resource)
            limit, remaining, reset = self._parse_limits(limits)

        if remaining == 0:
            self.refresh_rate_limits(key) # double check

        print key.split('-')[0], resource, limit, remaining, reset

        return key, limit, remaining, reset

    def set_access_token(self, key):
        """
        Overload without the `secret`.
        """
        assert key in self.tokens
        self.access_token = key
        self.access_token_secret = self.tokens[key]['secret']

    def update_rate_limits(self, key, 
        resource, limit=None, remaining=None, reset=None):
        """
        After performing a request for specified resource
        by using specified access token key, the rate limits
        have to be updated with the specific values from the
        X-Rate-Limit response headers.

        See https://dev.twitter.com/docs/rate-limiting/1.1
        """
        assert key in self.tokens
        limits = self.tokens[key]['resources'].get(resource)
        if not limits:
            limits = {u'limit': None, u'remaining': None, u'reset': None}
            self.tokens[key]['resources'][unicode(resource)] = limits
        if limit is not None:
            limits['limit'] = int(limit)
        if remaining is not None:
            limits['remaining'] = int(remaining)
        if reset is not None:
            limits['reset'] = int(reset)

    def refresh_rate_limits(self, key):
        """
        Reload rate limits for specified token key.
        """
        secret = self.tokens[key]['secret']
        rls = self._get_rate_limit_status(key, secret)
        self._load_rate_limit_status(key, rls)

