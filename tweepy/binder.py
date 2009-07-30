# Tweepy
# Copyright 2009 Joshua Roesslein
# See LICENSE

import httplib
import urllib

from parsers import parse_error
from error import TweepError

def bind_api(path, parser, allowed_param=None, method='GET', require_auth=False,
              timeout=None, host=None):

  def _call(api, *args, **kargs):
    # If require auth, throw exception if credentials not provided
    if require_auth and not api._b64up:
      raise TweepError('Authentication required!')

    # Filter out unallowed parameters
    if allowed_param:
      parameters = dict((k,v) for k,v in kargs.items() if k in allowed_param)
    else:
      parameters = None

    # Build url with parameters
    if parameters:
      url = '%s?%s' % (path, urllib.urlencode(parameters))
    else:
      url = path

    # Check cache if caching enabled and method is GET
    if api.cache and method == 'GET':
      cache_result = api.cache.get(url, timeout)
      if cache_result:
        # if cache result found and not expired, return it
        cache_result._api = api  # restore api reference to this api instance
        return cache_result

    # Open connection
    if host:
      _host = host
    else:
      _host = api.host
    if api.secure:
      conn = httplib.HTTPSConnection(_host)
    else:
      conn = httplib.HTTPConnection(_host)

    # Assemble headers
    headers = {
      'User-Agent': 'tweepy'
    }
    if api._b64up:
      headers['Authorization'] = 'Basic %s' % api._b64up

    # Build request
    conn.request(method, url, headers=headers)

    # Get response
    resp = conn.getresponse()

    # If an error was returned, throw an exception
    if resp.status != 200:
      raise TweepError(parse_error(resp.read()))

    # Pass returned body into parser and return parser output
    out =  parser(resp.read(), api)

    # store result in cache
    if api.cache and method == 'GET':
      api.cache.store(url, out)

    # close connection and return data
    conn.close()
    return out

  return _call
