# Tweepy
# Copyright 2009-2021 Joshua Roesslein
# See LICENSE for details.

# Appengine users: https://developers.google.com/appengine/docs/python/sockets/#making_httplib_use_sockets

import json
import logging
import ssl
from threading import Thread
from time import sleep

import requests
import urllib3

from tweepy.api import API
from tweepy.error import TweepError
from tweepy.models import Status

STREAM_VERSION = '1.1'

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

    def __init__(self, auth, listener, **options):
        self.auth = auth
        self.listener = listener
        self.running = False
        self.daemon = options.get("daemon", False)
        self.timeout = options.get("timeout", 300.0)
        self.retry_count = options.get("retry_count")
        # values according to
        # https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/connecting#reconnecting
        self.retry_time_start = options.get("retry_time", 5.0)
        self.retry_420_start = options.get("retry_420", 60.0)
        self.retry_time_cap = options.get("retry_time_cap", 320.0)
        self.snooze_time_step = options.get("snooze_time", 0.25)
        self.snooze_time_cap = options.get("snooze_time_cap", 16)

        # The default socket.read size. Default to less than half the size of
        # a tweet so that it reads tweets with the minimal latency of 2 reads
        # per tweet. Values higher than ~1kb will increase latency by waiting
        # for more data to arrive but may also increase throughput by doing
        # fewer socket read calls.
        self.chunk_size = options.get("chunk_size", 512)

        self.verify = options.get("verify", True)

        self.headers = options.get("headers") or {}
        self.new_session()
        self.retry_time = self.retry_time_start
        self.snooze_time = self.snooze_time_step

        # Example: proxies = {'http': 'http://localhost:1080', 'https': 'http://localhost:1080'}
        self.proxies = options.get("proxies")
        self.host = options.get('host', 'stream.twitter.com')

    def new_session(self):
        self.session = requests.Session()
        self.session.headers = self.headers
        self.session.params = None

    def _run(self, body=None):
        # Authenticate
        url = f"https://{self.host}{self.url}"

        # Connect and process the stream
        error_counter = 0
        resp = None
        try:
            while self.running:
                if self.retry_count is not None:
                    if error_counter > self.retry_count:
                        # quit if error count greater than retry count
                        break
                try:
                    auth = self.auth.apply_auth()
                    resp = self.session.request('POST',
                                                url,
                                                data=body,
                                                timeout=self.timeout,
                                                stream=True,
                                                auth=auth,
                                                verify=self.verify,
                                                proxies=self.proxies)
                    if resp.status_code != 200:
                        if self.listener.on_request_error(resp.status_code) is False:
                            break
                        error_counter += 1
                        if resp.status_code == 420:
                            self.retry_time = max(self.retry_420_start,
                                                  self.retry_time)
                        sleep(self.retry_time)
                        self.retry_time = min(self.retry_time * 2,
                                              self.retry_time_cap)
                    else:
                        error_counter = 0
                        self.retry_time = self.retry_time_start
                        self.snooze_time = self.snooze_time_step
                        self.listener.on_connect()
                        self._read_loop(resp)
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
                    sleep(self.snooze_time)
                    self.snooze_time = min(
                        self.snooze_time + self.snooze_time_step,
                        self.snooze_time_cap
                    )
        except Exception as exc:
            self.listener.on_exception(exc)
            raise
        finally:
            self.running = False
            if resp:
                resp.close()
            self.new_session()

    def _read_loop(self, resp):
        for line in resp.iter_lines(chunk_size=self.chunk_size):
            if not self.running:
                break
            if not line:
                self.listener.on_keep_alive()
            elif self.listener.on_data(line) is False:
                self.running = False
                break

        if resp.raw.closed:
            self.on_closed(resp)

    def _start(self, threaded=False, *args, **kwargs):
        self.running = True
        if threaded:
            self._thread = Thread(target=self._run, args=args, kwargs=kwargs)
            self._thread.daemon = self.daemon
            self._thread.start()
        else:
            self._run(*args, **kwargs)

    def on_closed(self, resp):
        """ Called when the response has been closed by Twitter """
        pass

    def sample(self, threaded=False, languages=None, stall_warnings=False):
        self.session.params = {}
        if self.running:
            raise TweepError('Stream object already connected!')
        self.url = f'/{STREAM_VERSION}/statuses/sample.json'
        if languages:
            self.session.params['language'] = ','.join(map(str, languages))
        if stall_warnings:
            self.session.params['stall_warnings'] = 'true'
        self._start(threaded=threaded)

    def filter(self, follow=None, track=None, threaded=False, locations=None,
               stall_warnings=False, languages=None, encoding='utf8', filter_level=None):
        body = {}
        self.session.headers['Content-type'] = "application/x-www-form-urlencoded"
        if self.running:
            raise TweepError('Stream object already connected!')
        self.url = f'/{STREAM_VERSION}/statuses/filter.json'
        if follow:
            body['follow'] = ','.join(follow).encode(encoding)
        if track:
            body['track'] = ','.join(track).encode(encoding)
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
            body['filter_level'] = filter_level.encode(encoding)
        self.session.params = {}
        self._start(body=body, threaded=threaded)

    def disconnect(self):
        self.running = False
