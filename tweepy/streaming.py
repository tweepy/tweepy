# Tweepy
# Copyright 2009-2021 Joshua Roesslein
# See LICENSE for details.

# Appengine users: https://developers.google.com/appengine/docs/python/sockets/#making_httplib_use_sockets

import json
import logging
import re
import ssl
from threading import Thread
from time import sleep

import requests

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

    def on_error(self, status_code):
        """Called when a non-200 status code is returned"""
        return False

    def on_timeout(self):
        """Called when stream connection times out"""
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


class ReadBuffer:
    """Buffer data from the response in a smarter way than httplib/requests can.

    Tweets are roughly in the 2-12kb range, averaging around 3kb.
    Requests/urllib3/httplib/socket all use socket.read, which blocks
    until enough data is returned. On some systems (eg google appengine), socket
    reads are quite slow. To combat this latency we can read big chunks,
    but the blocking part means we won't get results until enough tweets
    have arrived. That may not be a big deal for high throughput systems.
    For low throughput systems we don't want to sacrifice latency, so we
    use small chunks so it can read the length and the tweet in 2 read calls.
    """

    def __init__(self, stream, chunk_size, encoding='utf-8'):
        self._stream = stream
        self._buffer = b''
        self._chunk_size = chunk_size
        self._encoding = encoding

    def read_len(self, length):
        while not self._stream.closed:
            if len(self._buffer) >= length:
                return self._pop(length)
            read_len = max(self._chunk_size, length - len(self._buffer))
            self._buffer += self._stream.read(read_len)
        return b''

    def read_line(self, sep=b'\n'):
        """Read the data stream until a given separator is found (default \n)

        :param sep: Separator to read until. Must by of the bytes type
        :return: The str of the data read until sep
        """
        start = 0
        while not self._stream.closed:
            loc = self._buffer.find(sep, start)
            if loc >= 0:
                return self._pop(loc + len(sep))
            else:
                start = len(self._buffer)
            self._buffer += self._stream.read(self._chunk_size)
        return b''

    def _pop(self, length):
        r = self._buffer[:length]
        self._buffer = self._buffer[length:]
        return r.decode(self._encoding)


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
        self.body = None
        self.retry_time = self.retry_time_start
        self.snooze_time = self.snooze_time_step

        # Example: proxies = {'http': 'http://localhost:1080', 'https': 'http://localhost:1080'}
        self.proxies = options.get("proxies")
        self.host = options.get('host', 'stream.twitter.com')

    def new_session(self):
        self.session = requests.Session()
        self.session.headers = self.headers
        self.session.params = None

    def _run(self):
        # Authenticate
        url = "https://%s%s" % (self.host, self.url)

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
                                                data=self.body,
                                                timeout=self.timeout,
                                                stream=True,
                                                auth=auth,
                                                verify=self.verify,
                                                proxies=self.proxies)
                    if resp.status_code != 200:
                        if self.listener.on_error(resp.status_code) is False:
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
                except (requests.Timeout, ssl.SSLError) as exc:
                    # This is still necessary, as a SSLError can actually be
                    # thrown when using Requests
                    # If it's not time out treat it like any other exception
                    if isinstance(exc, ssl.SSLError):
                        if not (exc.args and 'timed out' in str(exc.args[0])):
                            raise
                    if self.listener.on_timeout() is False:
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
        charset = resp.headers.get('content-type', default='')
        enc_search = re.search(r'charset=(?P<enc>\S*)', charset)
        if enc_search is not None:
            encoding = enc_search.group('enc')
        else:
            encoding = 'utf-8'

        buf = ReadBuffer(resp.raw, self.chunk_size, encoding=encoding)

        while self.running and not resp.raw.closed:
            length = 0
            while not resp.raw.closed:
                line = buf.read_line()
                stripped_line = line.strip() if line else line  # line is sometimes None so we need to check here
                if not stripped_line:
                    self.listener.on_keep_alive()  # keep-alive new lines are expected
                elif stripped_line.isdigit():
                    length = int(stripped_line)
                    break
                else:
                    raise TweepError('Expecting length, unexpected value found')

            data = buf.read_len(length)
            if self.running and data:
                if self.listener.on_data(data) is False:
                    self.running = False

            # # Note: keep-alive newlines might be inserted before each length value.
            # # read until we get a digit...
            # c = b'\n'
            # for c in resp.iter_content(decode_unicode=True):
            #     if c == b'\n':
            #         continue
            #     break
            #
            # delimited_string = c
            #
            # # read rest of delimiter length..
            # d = b''
            # for d in resp.iter_content(decode_unicode=True):
            #     if d != b'\n':
            #         delimited_string += d
            #         continue
            #     break
            #
            # # read the next twitter status object
            # if delimited_string.decode('utf-8').strip().isdigit():
            #     status_id = int(delimited_string)
            #     data = resp.raw.read(status_id)
            #     if self.running:
            #         if self.listener.on_data(data.decode('utf-8')) is False:
            #             self.running = False

        if resp.raw.closed:
            self.on_closed(resp)

    def _start(self, is_async):
        self.running = True
        if is_async:
            self._thread = Thread(target=self._run)
            self._thread.daemon = self.daemon
            self._thread.start()
        else:
            self._run()

    def on_closed(self, resp):
        """ Called when the response has been closed by Twitter """
        pass

    def sample(self, is_async=False, languages=None, stall_warnings=False):
        self.session.params = {'delimited': 'length'}
        if self.running:
            raise TweepError('Stream object already connected!')
        self.url = '/%s/statuses/sample.json' % STREAM_VERSION
        if languages:
            self.session.params['language'] = ','.join(map(str, languages))
        if stall_warnings:
            self.session.params['stall_warnings'] = 'true'
        self._start(is_async)

    def filter(self, follow=None, track=None, is_async=False, locations=None,
               stall_warnings=False, languages=None, encoding='utf8', filter_level=None):
        self.body = {}
        self.session.headers['Content-type'] = "application/x-www-form-urlencoded"
        if self.running:
            raise TweepError('Stream object already connected!')
        self.url = '/%s/statuses/filter.json' % STREAM_VERSION
        if follow:
            self.body['follow'] = ','.join(follow).encode(encoding)
        if track:
            self.body['track'] = ','.join(track).encode(encoding)
        if locations and len(locations) > 0:
            if len(locations) % 4 != 0:
                raise TweepError("Wrong number of locations points, "
                                 "it has to be a multiple of 4")
            self.body['locations'] = ','.join(['%.4f' % l for l in locations])
        if stall_warnings:
            self.body['stall_warnings'] = stall_warnings
        if languages:
            self.body['language'] = ','.join(map(str, languages))
        if filter_level:
            self.body['filter_level'] = filter_level.encode(encoding)
        self.session.params = {'delimited': 'length'}
        self._start(is_async)

    def disconnect(self):
        self.running = False
