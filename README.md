Tweepy with multiple access tokens
==================================

This is a fork of the well-known Tweepy library (https://github.com/tweepy/tweepy).

Changes
-------

* Multiple access tokens with RateLimitHandler (https://github.com/svven/tweepy/blob/master/tweepy/limit.py)

```python
from tweepy import RateLimitHandler

from config import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKENS

def get_api():
	auth = RateLimitHandler(CONSUMER_KEY, CONSUMER_SECRET)
	for key, secret in ACCESS_TOKENS:
		try:
			auth.add_access_token(key, secret)
		except Exception, e:
			print key, e
	print 'Token pool size: %d' % len(auth.tokens)
	api = API(auth, 
		wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
	return api

api = get_api()
```

> Provided access tokens are used selectively based on requested resource (https://dev.twitter.com/docs/rate-limiting/1.1/limits) and current rate limits. The access token with most remaining requests per window for the specified resource is being selected and used when applying the authentication, before the actual request is performed. This pattern ensures the usage of available access tokens in a round robin fashion, exploiting to maximum the rate limits.
> 
> Here's a good use case for it: https://github.com/ducu/twitter-most-followed#requirements

* Various fixes: IdIterator, response status code, API DELETE methods.

Installation
------------

    pip install git+https://github.com/svven/tweepy.git#egg=tweepy

Pull Request
------------

If you think this functionality is a good addition to Tweepy, please consider the pull request I created.

* https://github.com/tweepy/tweepy/pull/484
* http://discuss.tweepy.org/t/ratelimithandler-pull-request/87

Cheers, [@ducu](http://twitter.com/ducu)


