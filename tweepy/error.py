# Tweepy
# Copyright 2009-2020 Joshua Roesslein
# See LICENSE for details.

import six


class TweepError(Exception):
    """Tweepy exception"""

    def __init__(self, reason, response=None, api_code=None):
        self.reason = six.text_type(reason)
        self.response = response
        self.api_code = api_code
        super(TweepError, self).__init__(reason)

    def __str__(self):
        return self.reason


def is_rate_limit_error_message(api_error_code):
    """Check if the supplied error code belongs to a rate limit error."""
    return api_error_code == 88


class RateLimitError(TweepError):
    """Exception for Tweepy hitting the rate limit."""
    # RateLimitError has the exact same properties and inner workings
    # as TweepError for backwards compatibility reasons.
    pass
