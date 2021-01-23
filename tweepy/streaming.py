# Tweepy
# Copyright 2009-2021 Joshua Roesslein
# See LICENSE for details.

# Appengine users: https://developers.google.com/appengine/docs/python/sockets/#making_httplib_use_sockets

import json
import logging
from math import inf
import ssl
from threading import Thread
from time import sleep

import requests
from requests_oauthlib import OAuth1
import urllib3

from tweepy.api import API
from tweepy.error import TweepError
from tweepy.models import Status

log = logging.getLogger(__name__)


class StreamListener:

    def __init__(self, api=None):
        self.api = api or API()

    def on_connect(self):
        """Called once connected to streaming server.

        This will be invoked once a successful response
        is received from the server. Allows the listener
        to perform some work prior to entering the read loop.
        """
        pass

    def on_data(self, raw_data):
        """Called when raw data is received from connection.

        Override this method if you wish to manually handle
        the stream data. Return False to stop stream and close connection.
        """
        data = json.loads(raw_data)

        if 'in_reply_to_status_id' in data:
            status = Status.parse(self.api, data)
            return self.on_status(status)
        if 'delete' in data:
            delete = data['delete']['status']
            return self.on_delete(delete['id'], delete['user_id'])
        if 'limit' in data:
            return self.on_limit(data['limit']['track'])
        if 'disconnect' in data:
            return self.on_disconnect(data['disconnect'])
        if 'warning' in data:
            return self.on_warning(data['warning'])
        if 'scrub_geo' in data:
            return self.on_scrub_geo(data['scrub_geo'])
        if 'status_withheld' in data:
            return self.on_status_withheld(data['status_withheld'])
        if 'user_withheld' in data:
            return self.on_user_withheld(data['user_withheld'])

        log.error("Unknown message type: %s", raw_data)

    def on_keep_alive(self):
        """Called when a keep-alive arrived"""
        return

    def on_status(self, status):
        """Called when a new status arrives"""
        return

    def on_exception(self, exception):
        """Called when an unhandled exception occurs."""
        return

    def on_delete(self, status_id, user_id):
        """Called when a delete notice arrives for a status"""
        return

    def on_limit(self, track):
        """Called when a limitation notice arrives"""
        return

    def on_request_error(self, status_code):
        """Called when a non-200 status code is returned"""
        return False

    def on_connection_error(self):
        """Called when stream connection errors or times out"""
        return

    def on_disconnect(self, notice):
        """Called when twitter sends a disconnect notice

        Disconnect codes are listed here:
        https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/streaming-message-types
        """
        return

    def on_warning(self, notice):
        """Called when a disconnection warning message arrives"""
        return

    def on_scrub_geo(self, notice):
        """Called when a location deletion notice arrives"""
        return

    def on_status_withheld(self, notice):
        """Called when a status withheld content notice arrives"""
        return

    def on_user_withheld(self, notice):
        """Called when a user withheld content notice arrives"""
        return


class Stream:

    def __init__(self, consumer_key, consumer_secret, access_token,
                 access_token_secret, listener, *, chunk_size=512,
                 daemon=False, max_retries=inf, proxy=None, verify=True):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.listener = listener
        # The default socket.read size. Default to less than half the size of
        # a tweet so that it reads tweets with the minimal latency of 2 reads
        # per tweet. Values higher than ~1kb will increase latency by waiting
        # for more data to arrive but may also increase throughput by doing
        # fewer socket read calls.
        self.chunk_size = chunk_size
        self.daemon = daemon
        self.max_retries = max_retries
        self.proxies = {"https": proxy} if proxy else {}
        self.verify = verify

        self.running = False
        self.session = None

    def _run(self, endpoint, params=None, body=None):
        if self.session is None:
            self.session = requests.Session()

        url = f"https://stream.twitter.com/1.1/{endpoint}.json"

        auth = OAuth1(self.consumer_key, self.consumer_secret,
                      self.access_token, self.access_token_secret)

        error_count = 0
        # https://developer.twitter.com/en/docs/twitter-api/v1/tweets/filter-realtime/guides/connecting
        stall_timeout = 90
        network_error_wait = network_error_wait_step = 0.25
        network_error_wait_max = 16
        http_error_wait = http_error_wait_start = 5
        http_error_wait_max = 320
        http_420_error_wait_start = 60

        try:
            while self.running and error_count <= self.max_retries:
                try:
                    with self.session.request(
                        'POST', url, params=params, data=body,
                        timeout=stall_timeout, stream=True, auth=auth,
                        verify=self.verify, proxies=self.proxies
                    ) as resp:
                        if resp.status_code != 200:
                            if self.listener.on_request_error(resp.status_code) is False:
                                break
                            error_count += 1
                            if resp.status_code == 420:
                                http_error_wait = max(
                                    http_420_error_wait_start, http_error_wait
                                )
                            sleep(http_error_wait)
                            http_error_wait = min(http_error_wait * 2,
                                                  http_error_wait_max)
                        else:
                            error_count = 0
                            http_error_wait = http_error_wait_start
                            network_error_wait = network_error_wait_step
                            self.listener.on_connect()

                            for line in resp.iter_lines(
                                chunk_size=self.chunk_size
                            ):
                                if not self.running:
                                    break
                                if not line:
                                    self.listener.on_keep_alive()
                                elif self.listener.on_data(line) is False:
                                    self.running = False
                                    break

                            if resp.raw.closed:
                                self.on_closed(resp)
                except (requests.ConnectionError, requests.Timeout,
                        ssl.SSLError, urllib3.exceptions.ReadTimeoutError,
                        urllib3.exceptions.ProtocolError) as exc:
                    # This is still necessary, as a SSLError can actually be
                    # thrown when using Requests
                    # If it's not time out treat it like any other exception
                    if isinstance(exc, ssl.SSLError):
                        if not (exc.args and 'timed out' in str(exc.args[0])):
                            raise
                    if self.listener.on_connection_error() is False:
                        break
                    if self.running is False:
                        break
                    sleep(network_error_wait)
                    network_error_wait = min(
                        network_error_wait + network_error_wait_step,
                        network_error_wait_max
                    )
        except Exception as exc:
            self.listener.on_exception(exc)
            raise
        finally:
            self.session.close()
            self.running = False

    def _start(self, *args, threaded=False, **kwargs):
        self.running = True
        if threaded:
            self._thread = Thread(target=self._run, name="Tweepy Stream",
                                  args=args, kwargs=kwargs, daemon=self.daemon)
            self._thread.start()
        else:
            self._run(*args, **kwargs)

    def filter(self, follow=None, track=None, threaded=False, locations=None,
               stall_warnings=False, languages=None, filter_level=None):
        body = {}
        if self.running:
            raise TweepError('Stream object already connected!')
        endpoint = 'statuses/filter'
        if follow:
            body['follow'] = ','.join(follow)
        if track:
            body['track'] = ','.join(track)
        if locations and len(locations) > 0:
            if len(locations) % 4 != 0:
                raise TweepError("Wrong number of locations points, "
                                 "it has to be a multiple of 4")
            body['locations'] = ','.join([f'{l:.4f}' for l in locations])
        if stall_warnings:
            body['stall_warnings'] = stall_warnings
        if languages:
            body['language'] = ','.join(map(str, languages))
        if filter_level:
            body['filter_level'] = filter_level
        self._start(endpoint, body=body, threaded=threaded)

    def sample(self, threaded=False, languages=None, stall_warnings=False):
        params = {}
        if self.running:
            raise TweepError('Stream object already connected!')
        endpoint = 'statuses/sample'
        if languages:
            params['language'] = ','.join(map(str, languages))
        if stall_warnings:
            params['stall_warnings'] = 'true'
        self._start(endpoint, params=params, threaded=threaded)

    def disconnect(self):
        self.running = False

    def on_closed(self, resp):
        """ Called when the response has been closed by Twitter """
        pass
