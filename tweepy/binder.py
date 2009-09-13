# Tweepy
# Copyright 2009 Joshua Roesslein
# See LICENSE

import httplib
import urllib

from . parsers import parse_error
from . error import TweepError


def bind_api(path, parser, allowed_param=None, method='GET', require_auth=False,
              timeout=None, host=None):

    def _call(api, *args, **kargs):
        # If require auth, throw exception if credentials not provided
        if require_auth and not api.auth_handler:
            raise TweepError('Authentication required!')

        # check for post_data parameter
        if 'post_data' in kargs:
            post_data = kargs['post_data']
            del kargs['post_data']
        else:
            post_data = None

        # check for headers
        if 'headers' in kargs:
            headers = dict(kargs['headers'])
            del kargs['headers']
        else:
            headers = {}

        # build parameter dict
        if allowed_param:
            parameters = {}
            for idx, arg in enumerate(args):
                try:
                    parameters[allowed_param[idx]] = arg
                except IndexError:
                    raise TweepError('Too many parameters supplied!')
            for k, arg in kargs.items():
                if arg is None:
                    continue
                if k in parameters:
                    raise TweepError('Multiple values for parameter %s supplied!' % k)
                if k not in allowed_param:
                    raise TweepError('Invalid parameter %s supplied!' % k)
                parameters[k] = arg
        else:
            if len(args) > 0 or len(kargs) > 0:
                raise TweepError('This method takes no parameters!')
            parameters = None

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
            # if cache result found and not expired, return it
            if cache_result:
                # must restore api reference
                if isinstance(cache_result, list):
                    for result in cache_result:
                        result._api = api
                else:
                    cache_result._api = api
                return cache_result

        # Open connection
        # FIXME: add timeout
        if api.secure:
            conn = httplib.HTTPSConnection(_host)
        else:
            conn = httplib.HTTPConnection(_host)

        # Build request
        conn.request(method, url, headers=headers, body=post_data)

        # Get response
        resp = conn.getresponse()

        # If an error was returned, throw an exception
        if resp.status != 200:
            try:
                error_msg = parse_error(resp.read())
            except Exception:
                error_msg = "Twitter error response: status code = %s" % resp.status
            raise TweepError(error_msg)

        # Pass returned body into parser and return parser output
        try:
            out = parser(resp.read(), api)
        except Exception:
            raise TweepError("Failed to parse returned data")

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

