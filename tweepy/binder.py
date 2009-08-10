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
    if require_auth and not api.auth_handler:
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
        if k not in allowed_param:
          raise TweepError('Invalid parameter %s supplied!' % k)
        parameters[k] = arg
    else:
      if len(args) > 0 or len(kargs) > 0:
        raise TweepError('This method takes no parameters!')
      parameters = None

    # Assemble headers
    headers = {
      'User-Agent': 'tweepy'
    }

    # Build url with parameters
    if parameters:
      url = '%s?%s' % (api.api_root + path, urllib.urlencode(parameters))
    else:
      url = api.api_root + path

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
      conn = httplib.HTTPSConnection(_host)
    else:
      conn = httplib.HTTPConnection(_host)

    # Build request
    conn.request(method, url, headers=headers)

    # Get response
    resp = conn.getresponse()

    # If an error was returned, throw an exception
    if resp.status != 200:
      raise TweepError(parse_error(resp.read()))

    # Pass returned body into parser and return parser output
    out =  parser(resp.read(), api)
    conn.close()

    # validate result
    if api.validate:
      # list of results
      if isinstance(out, list) and len(out) > 0:
        if hasattr(out[0], 'validate'):
          for result in out:
            result.validate()
      # single result
      else:
        if hasattr(out, 'validate'):
          out.validate()

    # store result in cache
    if api.cache and method == 'GET':
      api.cache.store(url, out)

    return out

  return _call
