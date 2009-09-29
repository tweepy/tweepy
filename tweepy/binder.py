# Tweepy
# Copyright 2009 Joshua Roesslein
# See LICENSE

import httplib
import urllib

from . parsers import parse_error
from . error import TweepError

try:
    import json #Python >= 2.6
except ImportError:
    try:
        import simplejson as json #Python < 2.6
    except ImportError:
        try:
            from django.utils import simplejson as json #Google App Engine
        except ImportError:
            raise ImportError, "Can't load a json library"


def bind_api(path, parser, allowed_param=None, method='GET', require_auth=False,
              timeout=None, host=None):

    def _call(api, *args, **kargs):
        # If require auth, throw exception if credentials not provided
        if require_auth and not api.auth_handler:
            raise TweepError('Authentication required!')

        # Log some useful infomation
        api.logger.debug('Starting request...')
        api.logger.debug('  path: %s' % path)
        api.logger.debug('  method: %s' % method)

        # check for post_data parameter
        if 'post_data' in kargs:
            post_data = kargs['post_data']
            del kargs['post_data']
            api.logger.debug('  post data: %s' % post_data)
        else:
            post_data = None

        # check for headers
        if 'headers' in kargs:
            headers = dict(kargs['headers'])
            del kargs['headers']
        else:
            headers = {}
        api.logger.debug('  headers: %s' % headers)

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
        api.logger.debug('  parameters: %s' % parameters)

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
            api.auth_handler.apply_auth(
                    scheme + _host + url,
                    method, headers, parameters
            )

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
                api.logger.debug("Cache hit!")
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
        api.last_response = resp
        api.logger.debug('Received response...')
        api.logger.debug('  headers: %s' % resp.getheaders())
        api.logger.debug('  status code: %s' % resp.status)

        # If an error was returned, throw an exception
        if resp.status != 200:
            try:
                error_msg = parse_error(resp.read())
            except Exception:
                error_msg = "Twitter error response: status code = %s" % resp.status
            api.logger.error('  Error: %s' % error_msg)
            raise TweepError(error_msg)

        # Parse json respone body
        try:
            jobject = json.loads(resp.read())
        except Exception:
            raise TweepError("Failed to parse json response text")

        # Parse cursor infomation
        if isinstance(jobject, dict):
            next_cursor = jobject.get('next_cursor')
            prev_cursor = jobject.get('previous_cursor')
        else:
            next_cursor = None
            prev_cursor = None

        # Pass json object into parser
        try:
            if next_cursor is not None and prev_cursor is not None:
                out = parser(jobject, api), next_cursor, prev_cursor
            else:
                out = parser(jobject, api)
        except Exception:
            raise TweepError("Failed to parse json object")

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
            api.logger.debug("  caching result")

        api.logger.debug('request done.')

        return out

    # Expose extra data in callable object
    _call.allowed_param = allowed_param

    return _call

