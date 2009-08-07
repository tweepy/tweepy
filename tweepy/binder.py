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
    if not api.auth_handler:
      raise TweepError('Authentication required!')

    # build parameter dict
    if allowed_param:
      parameters = {}
      for idx, arg in enumerate(args):
        try:
          parameters[allowed_param[idx]] = arg
        except IndexError:
          raise TweepError('Too many parameters supplied!')
      for k, arg in kargs.items():
        if k in parameters:
          raise TweepError('Multiple values for parameter %s supplied!' % k)
        parameters[k] = arg
    else:
      parameters = None

    # Assemble headers
    headers = {
      'User-Agent': 'tweepy'
    }

    # Build url with parameters
    if parameters:
      url = '%s?%s' % (path, urllib.urlencode(parameters))
    else:
      url = path

    # get scheme and host
    if api.secure:
      scheme = 'https://'
    else:
      scheme = 'http://'
    _host = host or api.host

    # Apply authentication
    if api.auth_handler:
      api.auth_handler.apply_auth(scheme + _host + url, method, headers, parameters)

    # Check cache if caching enabled and method is GET
    if api.cache and method == 'GET':
      cache_result = api.cache.get(url, timeout)
      if cache_result:
        # if cache result found and not expired, return it
        cache_result._api = api  # restore api reference to this api instance
        return cache_result

    # Open connection
    if api.secure:
      conn = httplib.HTTPSConnection(_host, timeout=10)
    else:
      conn = httplib.HTTPConnection(_host, timeout=10)

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
