# Tweepy
# Copyright 2009-2010 Joshua Roesslein
# See LICENSE for details.

import httplib
import urllib
import time
import re
from StringIO import StringIO
import gzip

from tweepy.error import TweepError
from tweepy.utils import convert_to_utf8_str
from tweepy.models import Model

re_path_template = re.compile('{\w+}')


def bind_api(**config):

    class APIMethod(object):

        path = config['path']
        payload_type = config.get('payload_type', None)
        payload_list = config.get('payload_list', False)
        allowed_param = config.get('allowed_param', [])
        method = config.get('method', 'GET')
        require_auth = config.get('require_auth', False)
        search_api = config.get('search_api', False)
        use_cache = config.get('use_cache', True)

        def __init__(self, api, args, kargs):
            # If authentication is required and no credentials
            # are provided, throw an error.
            if self.require_auth and not api.auth:
                raise TweepError('Authentication required!')

            self.api = api
            self.post_data = kargs.pop('post_data', None)
            self.retry_count = kargs.pop('retry_count', api.retry_count)
            self.retry_delay = kargs.pop('retry_delay', api.retry_delay)
            self.retry_errors = kargs.pop('retry_errors', api.retry_errors)
            self.wait_on_rate_limit = kargs.pop('wait_on_rate_limit', api.wait_on_rate_limit)
            self.wait_on_rate_limit_notify = kargs.pop('wait_on_rate_limit_notify', api.wait_on_rate_limit_notify)
            self.parser = kargs.pop('parser', api.parser)
            self.headers = kargs.pop('headers', {})
            self.build_parameters(args, kargs)

            # Pick correct URL root to use
            if self.search_api:
                self.api_root = api.search_root
            else:
                self.api_root = api.api_root

            # Perform any path variable substitution
            self.build_path()

            if api.secure:
                self.scheme = 'https://'
            else:
                self.scheme = 'http://'

            if self.search_api:
                self.host = api.search_host
            else:
                self.host = api.host

            # Manually set Host header to fix an issue in python 2.5
            # or older where Host is set including the 443 port.
            # This causes Twitter to issue 301 redirect.
            # See Issue https://github.com/tweepy/tweepy/issues/12
            self.headers['Host'] = self.host
            # Monitoring rate limits
            self._remaining_calls = None
            self._reset_time = None

        def build_parameters(self, args, kargs):
            self.parameters = {}
            for idx, arg in enumerate(args):
                if arg is None:
                    continue
                try:
                    self.parameters[self.allowed_param[idx]] = convert_to_utf8_str(arg)
                except IndexError:
                    raise TweepError('Too many parameters supplied!')

            for k, arg in kargs.items():
                if arg is None:
                    continue
                if k in self.parameters:
                    raise TweepError('Multiple values for parameter %s supplied!' % k)

                self.parameters[k] = convert_to_utf8_str(arg)

        def build_path(self):
            for variable in re_path_template.findall(self.path):
                name = variable.strip('{}')

                if name == 'user' and 'user' not in self.parameters and self.api.auth:
                    # No 'user' parameter provided, fetch it from Auth instead.
                    value = self.api.auth.get_username()
                else:
                    try:
                        value = urllib.quote(self.parameters[name])
                    except KeyError:
                        raise TweepError('No parameter value found for path variable: %s' % name)
                    del self.parameters[name]

                self.path = self.path.replace(variable, value)

        def execute(self):
            self.api.cached_result = False

            # Build the request URL
            url = self.api_root + self.path
            if len(self.parameters):
                url = '%s?%s' % (url, urllib.urlencode(self.parameters))

            # Query the cache if one is available
            # and this request uses a GET method.
            if self.use_cache and self.api.cache and self.method == 'GET':
                cache_result = self.api.cache.get(url)
                # if cache result found and not expired, return it
                if cache_result:
                    # must restore api reference
                    if isinstance(cache_result, list):
                        for result in cache_result:
                            if isinstance(result, Model):
                                result._api = self.api
                    else:
                        if isinstance(cache_result, Model):
                            cache_result._api = self.api
                    self.api.cached_result = True
                    return cache_result

            # Continue attempting request until successful
            # or maximum number of retries is reached.
            retries_performed = 0
            while retries_performed < self.retry_count + 1:
                # handle running out of api calls
                if self.wait_on_rate_limit and self._reset_time is not None and \
                   self._remaining_calls is not None and self._remaining_calls < 1:
                    sleep_time = self._reset_time - int(time.time())
                    if sleep_time > 0:
                        if self.wait_on_rate_limit_notify:
                            print "Max retries reached. Sleeping for: " + str(sleep_time)
                        time.sleep(sleep_time + 5) # sleep for few extra sec

                # Open connection
                if self.api.secure:
                    conn = httplib.HTTPSConnection(self.host, timeout=self.api.timeout)
                else:
                    conn = httplib.HTTPConnection(self.host, timeout=self.api.timeout)

                # Apply authentication
                if self.api.auth:
                    self.api.auth.apply_auth(
                            self.scheme + self.host + url,
                            self.method, self.headers, self.parameters
                    )

                # Request compression if configured
                if self.api.compression:
                    self.headers['Accept-encoding'] = 'gzip'

                # Execute request
                try:
                    conn.request(self.method, url, headers=self.headers, body=self.post_data)
                    resp = conn.getresponse()
                except Exception as e:
                    raise TweepError('Failed to send request: %s' % e)
                rem_calls = resp.getheader('x-rate-limit-remaining')
                if rem_calls is not None:
                    self._remaining_calls = int(rem_calls)
                elif isinstance(self._remaining_calls, int):
                    self._remaining_calls -= 1
                reset_time = resp.getheader('x-rate-limit-reset')
                if reset_time is not None:
                    self._reset_time = int(reset_time)
                if self.wait_on_rate_limit and self._remaining_calls == 0 and (resp.status == 429 or resp.status == 420): # if ran out of calls before waiting switching retry last call
                    continue
                retry_delay = self.retry_delay
                # Exit request loop if non-retry error code
                if resp.status == 200:
                    break
                elif (resp.status == 429 or resp.status == 420) and self.wait_on_rate_limit:
                    if 'retry-after' in resp.msg:
                        retry_delay = float(resp.msg['retry-after'])
                elif self.retry_errors and resp.status not in self.retry_errors:
                    break

                # Sleep before retrying request again
                time.sleep(retry_delay)
                retries_performed += 1

            # If an error was returned, throw an exception
            self.api.last_response = resp
            if resp.status and not 200 <= resp.status < 300:
                try:
                    error_msg = self.parser.parse_error(resp.read())
                except Exception:
                    error_msg = "Twitter error response: status code = %s" % resp.status
                raise TweepError(error_msg, resp)

            # Parse the response payload
            body = resp.read()
            if resp.getheader('Content-Encoding', '') == 'gzip':
                try:
                    zipper = gzip.GzipFile(fileobj=StringIO(body))
                    body = zipper.read()
                except Exception as e:
                    raise TweepError('Failed to decompress data: %s' % e)
            
            result = self.parser.parse(self, body)

            conn.close()

            # Store result into cache if one is available.
            if self.use_cache and self.api.cache and self.method == 'GET' and result:
                self.api.cache.store(url, result)

            return result

    def _call(api, *args, **kargs):

        method = APIMethod(api, args, kargs)
        if kargs.get('create'):
            return method
        else:
            return method.execute()

    # Set pagination mode
    if 'cursor' in APIMethod.allowed_param:
        _call.pagination_mode = 'cursor'
    elif 'max_id' in APIMethod.allowed_param and \
         'since_id' in APIMethod.allowed_param:
        _call.pagination_mode = 'id'
    elif 'page' in APIMethod.allowed_param:
        _call.pagination_mode = 'page'

    return _call
