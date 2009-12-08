# Tweepy
# Copyright 2009 Joshua Roesslein
# See LICENSE

import httplib
import urllib
import time
import re

from tweepy.parsers import parse_error
from tweepy.error import TweepError

try:
    import simplejson as json
except ImportError:
    try:
        import json  # Python 2.6+
    except ImportError:
        try:
            from django.utils import simplejson as json  # Google App Engine
        except ImportError:
            raise ImportError, "Can't load a json library"

re_path_template = re.compile('{\w+}')


def bind_api(path, parser, allowed_param=[], method='GET', require_auth=False,
              timeout=None, search_api = False):

    def _call(api, *args, **kargs):
        # If require auth, throw exception if credentials not provided
        if require_auth and not api.auth:
            raise TweepError('Authentication required!')

        # check for post data
        post_data = kargs.pop('post_data', None)

        # check for retry request parameters
        retry_count = kargs.pop('retry_count', api.retry_count)
        retry_delay = kargs.pop('retry_delay', api.retry_delay)
        retry_errors = kargs.pop('retry_errors', api.retry_errors)

        # check for headers
        headers = kargs.pop('headers', {})

        # build parameter dict
        if allowed_param:
            parameters = {}
            for idx, arg in enumerate(args):
                if isinstance(arg, unicode):
                    arg = arg.encode('utf-8')
                elif not isinstance(arg, str):
                    arg = str(arg)

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

                if isinstance(arg, unicode):
                    arg = arg.encode('utf-8')
                elif not isinstance(arg, str):
                    arg = str(arg)
                parameters[k] = arg
        else:
            if len(args) > 0 or len(kargs) > 0:
                raise TweepError('This method takes no parameters!')
            parameters = None

        # Pick correct URL root to use
        if search_api is False:
            api_root = api.api_root
        else:
            api_root = api.search_root

        # Build the request URL
        if parameters:
            # Replace any template variables in path
            tpath = str(path)
            for template in re_path_template.findall(tpath):
                name = template.strip('{}')
                try:
                    value = urllib.quote(parameters[name])
                    tpath = tpath.replace(template, value)
                except KeyError:
                    raise TweepError('Invalid path key: %s' % name)
                del parameters[name]

            url = '%s?%s' % (api_root + tpath, urllib.urlencode(parameters))
        else:
            url = api_root + path

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

        # get scheme and host
        if api.secure:
            scheme = 'https://'
        else:
            scheme = 'http://'
        if search_api is False:
            host = api.host
        else:
            host = api.search_host

        # Continue attempting request until successful
        # or maximum number of retries is reached.
        retries_performed = 0
        while retries_performed < retry_count + 1:
            # Open connection
            # FIXME: add timeout
            if api.secure:
                conn = httplib.HTTPSConnection(host)
            else:
                conn = httplib.HTTPConnection(host)

            # Apply authentication
            if api.auth:
                api.auth.apply_auth(
                        scheme + host + url,
                        method, headers, parameters
                )

            # Build request
            try:
                conn.request(method, url, headers=headers, body=post_data)
            except Exception, e:
                raise TweepError('Failed to send request: %s' % e)

            # Get response
            resp = conn.getresponse()

            # Exit request loop if non-retry error code
            if retry_errors is None:
                if resp.status == 200: break
            else:
                if resp.status not in retry_errors: break

            # Sleep before retrying request again
            time.sleep(retry_delay)
            retries_performed += 1

        # If an error was returned, throw an exception
        api.last_response = resp
        if resp.status != 200:
            try:
                error_msg = parse_error(json.loads(resp.read()))
            except Exception:
                error_msg = "Twitter error response: status code = %s" % resp.status
            raise TweepError(error_msg)

        # Parse json respone body
        try:
            jobject = json.loads(resp.read())
        except Exception, e:
            raise TweepError("Failed to parse json: %s" % e)

        # Parse cursor infomation
        if isinstance(jobject, dict):
            next_cursor = jobject.get('next_cursor')
            prev_cursor = jobject.get('previous_cursor')
        else:
            next_cursor = None
            prev_cursor = None

        # Pass json object into parser
        try:
            if parameters and 'cursor' in parameters:
                out = parser(jobject, api), next_cursor, prev_cursor
            else:
                out = parser(jobject, api)
        except Exception, e:
            raise TweepError("Failed to parse response: %s" % e)

        conn.close()

        # store result in cache
        if api.cache and method == 'GET':
            api.cache.store(url, out)

        return out


    # Set pagination mode
    if 'cursor' in allowed_param:
        _call.pagination_mode = 'cursor'
    elif 'page' in allowed_param:
        _call.pagination_mode = 'page'

    return _call

