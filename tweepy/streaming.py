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

from tweepy.error import TweepError
from tweepy.models import Status

log = logging.getLogger(__name__)


class Stream:

    def __init__(self, consumer_key, consumer_secret, access_token,
                 access_token_secret, *, chunk_size=512, daemon=False,
                 max_retries=inf, proxy=None, verify=True):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
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
        self.thread = None

    def _connect(self, endpoint, params=None, body=None):
        self.running = True

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
                            self.on_request_error(resp.status_code)
                            if not self.running:
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
                            self.on_connect()
                            if not self.running:
                                break

                            for line in resp.iter_lines(
                                chunk_size=self.chunk_size
                            ):
                                if line:
                                    self.on_data(line)
                                else:
                                    self.on_keep_alive()
                                if not self.running:
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
                    self.on_connection_error()
                    if not self.running:
                        break
                    sleep(network_error_wait)
                    network_error_wait = min(
                        network_error_wait + network_error_wait_step,
                        network_error_wait_max
                    )
        except Exception as exc:
            self.on_exception(exc)
        finally:
            self.session.close()
            self.running = False

    def _threaded_connect(self, *args, **kwargs):
        self.thread = Thread(target=self._connect, name="Tweepy Stream",
                             args=args, kwargs=kwargs, daemon=self.daemon)
        self.thread.start()
        return self.thread

    def filter(self, *, follow=None, track=None, locations=None,
               filter_level=None, languages=None, stall_warnings=False,
               threaded=False):
        if self.running:
            raise TweepError('Stream object already connected!')

        endpoint = 'statuses/filter'

        body = {}
        if follow:
            body['follow'] = ','.join(follow)
        if track:
            body['track'] = ','.join(track)
        if locations and len(locations) > 0:
            if len(locations) % 4:
                raise TweepError("Wrong number of locations points, "
                                 "it has to be a multiple of 4")
            body['locations'] = ','.join(f'{l:.4f}' for l in locations)
        if filter_level:
            body['filter_level'] = filter_level
        if languages:
            body['language'] = ','.join(map(str, languages))
        if stall_warnings:
            body['stall_warnings'] = stall_warnings

        if threaded:
            return self._threaded_connect(endpoint, body=body)
        else:
            self._connect(endpoint, body=body)

    def sample(self, *, languages=None, stall_warnings=False, threaded=False):
        if self.running:
            raise TweepError('Stream object already connected!')

        endpoint = 'statuses/sample'

        params = {}
        if languages:
            params['language'] = ','.join(map(str, languages))
        if stall_warnings:
            params['stall_warnings'] = 'true'

        if threaded:
            return self._threaded_connect(endpoint, params=params)
        else:
            self._connect(endpoint, params=params)

    def disconnect(self):
        self.running = False

    def on_closed(self, resp):
        """ Called when the response has been closed by Twitter """
        log.error("Stream connection closed by Twitter")

    def on_connect(self):
        """Called once connected to streaming server.

        This will be invoked once a successful response
        is received from the server.
        """
        log.info("Stream connected")

    def on_connection_error(self):
        """Called when stream connection errors or times out"""
        log.error("Stream connection has errored or timed out")

    def on_exception(self, exception):
        """Called when an unhandled exception occurs."""
        log.exception("Stream encountered an exception")

    def on_keep_alive(self):
        """Called when a keep-alive arrived"""
        log.debug("Received keep-alive signal")

    def on_request_error(self, status_code):
        """Called when a non-200 status code is returned"""
        log.error("Stream encountered HTTP error: %d", status_code)

    def on_data(self, raw_data):
        """Called when raw data is received from connection.

        Override this method if you wish to manually handle
        the stream data.
        """
        data = json.loads(raw_data)

        if 'in_reply_to_status_id' in data:
            status = Status.parse(None, data)
            return self.on_status(status)
        if 'delete' in data:
            delete = data['delete']['status']
            return self.on_delete(delete['id'], delete['user_id'])
        if 'disconnect' in data:
            return self.on_disconnect(data['disconnect'])
        if 'limit' in data:
            return self.on_limit(data['limit']['track'])
        if 'scrub_geo' in data:
            return self.on_scrub_geo(data['scrub_geo'])
        if 'status_withheld' in data:
            return self.on_status_withheld(data['status_withheld'])
        if 'user_withheld' in data:
            return self.on_user_withheld(data['user_withheld'])
        if 'warning' in data:
            return self.on_warning(data['warning'])

        log.error("Unknown message type: %s", raw_data)

    def on_status(self, status):
        """Called when a new status arrives"""
        log.debug("Received status: %d", status.id)

    def on_delete(self, status_id, user_id):
        """Called when a delete notice arrives for a status"""
        log.debug("Received status deletion notice: %d", status_id)

    def on_disconnect(self, notice):
        """Called when twitter sends a disconnect notice

        Disconnect codes are listed here:
        https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/streaming-message-types
        """
        log.warning("Received disconnect message: %s", notice)

    def on_limit(self, track):
        """Called when a limitation notice arrives"""
        log.debug("Received limit notice: %d", track)

    def on_scrub_geo(self, notice):
        """Called when a location deletion notice arrives"""
        log.debug("Received location deletion notice: %s", notice)

    def on_status_withheld(self, notice):
        """Called when a status withheld content notice arrives"""
        log.debug("Received status withheld content notice: %s", notice)

    def on_user_withheld(self, notice):
        """Called when a user withheld content notice arrives"""
        log.debug("Received user withheld content notice: %s", notice)

    def on_warning(self, notice):
        """Called when a disconnection warning message arrives"""
        log.warning("Received stall warning: %s", notice)
