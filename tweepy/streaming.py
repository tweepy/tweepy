# Tweepy
# Copyright 2009-2010 Joshua Roesslein
# See LICENSE for details.

from __future__ import print_function

import logging
import requests
from requests.exceptions import Timeout
from threading import Thread
from time import sleep
from six.moves.html_parser import HTMLParser
import ssl

from tweepy.models import Status
from tweepy.api import API
from tweepy.error import TweepError

from tweepy.utils import import_simplejson, urlencode_noplus
json = import_simplejson()

STREAM_VERSION = '1.1'


class StreamListener(object):

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
        data = json.loads(HTMLParser().unescape(raw_data))

        if 'in_reply_to_status_id' in data:
            status = Status.parse(self.api, data)
            if self.on_status(status) is False:
                return False
        elif 'delete' in data:
            delete = data['delete']['status']
            if self.on_delete(delete['id'], delete['user_id']) is False:
                return False
        elif 'event' in data:
            status = Status.parse(self.api, data)
            if self.on_event(status) is False:
                return False
        elif 'direct_message' in data:
            status = Status.parse(self.api, data)
            if self.on_direct_message(status) is False:
                return False
        elif 'limit' in data:
            if self.on_limit(data['limit']['track']) is False:
                return False
        elif 'disconnect' in data:
            if self.on_disconnect(data['disconnect']) is False:
                return False
        else:
            logging.error("Unknown message type: " + str(raw_data))

    def on_status(self, status):
        """Called when a new status arrives"""
        return

    def on_exception(self, exception):
        """Called when an unhandled exception occurs."""
        return

    def on_delete(self, status_id, user_id):
        """Called when a delete notice arrives for a status"""
        return

    def on_event(self, status):
        """Called when a new event arrives"""
        return

    def on_direct_message(self, status):
        """Called when a new direct message arrives"""
        return

    def on_limit(self, track):
        """Called when a limitation notice arrvies"""
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
        https://dev.twitter.com/docs/streaming-apis/messages#Disconnect_messages_disconnect
        """
        return


class Stream(object):

    host = 'stream.twitter.com'

    def __init__(self, auth, listener, **options):
        self.auth = auth
        self.listener = listener
        self.running = False
        self.timeout = options.get("timeout", 300.0)
        self.retry_count = options.get("retry_count")
        # values according to https://dev.twitter.com/docs/streaming-apis/connecting#Reconnecting
        self.retry_time_start = options.get("retry_time", 5.0)
        self.retry_420_start = options.get("retry_420", 60.0)
        self.retry_time_cap = options.get("retry_time_cap", 320.0)
        self.snooze_time_step = options.get("snooze_time", 0.25)
        self.snooze_time_cap = options.get("snooze_time_cap", 16)
        self.buffer_size = options.get("buffer_size",  1500)

        self.api = API()
        self.session = requests.Session()
        self.session.headers = options.get("headers") or {}
        self.session.params = None
        self.body = None
        self.retry_time = self.retry_time_start
        self.snooze_time = self.snooze_time_step

    def _run(self):
        # Authenticate
        url = "https://%s%s" % (self.host, self.url)

        # Connect and process the stream
        error_counter = 0
        resp = None
        exception = None
        while self.running:
            if self.retry_count is not None and error_counter > self.retry_count:
                # quit if error count greater than retry count
                break
            try:
                auth = self.auth.apply_auth()
                resp = self.session.request('POST', url, data=self.body,
                        timeout=self.timeout, stream=True, auth=auth)
                if resp.status_code != 200:
                    if self.listener.on_error(resp.status_code) is False:
                        break
                    error_counter += 1
                    if resp.status_code == 420:
                        self.retry_time = max(self.retry_420_start, self.retry_time)
                    sleep(self.retry_time)
                    self.retry_time = min(self.retry_time * 2, self.retry_time_cap)
                else:
                    error_counter = 0
                    self.retry_time = self.retry_time_start
                    self.snooze_time = self.snooze_time_step
                    self.listener.on_connect()
                    self._read_loop(resp)
            except (Timeout, ssl.SSLError) as exc:
                # This is still necessary, as a SSLError can actually be thrown when using Requests
                # If it's not time out treat it like any other exception
                if isinstance(exc, ssl.SSLError) and not (exc.args and 'timed out' in str(exc.args[0])):
                    exception = exc
                    break
                if self.listener.on_timeout() == False:
                    break
                if self.running is False:
                    break
                sleep(self.snooze_time)
                self.snooze_time = min(self.snooze_time + self.snooze_time_step,
                                       self.snooze_time_cap)
            except Exception as exception:
                # any other exception is fatal, so kill loop
                break

        # cleanup
        self.running = False
        if resp:
            resp.close()

        self.session = requests.Session()

        if exception:
            # call a handler first so that the exception can be logged.
            self.listener.on_exception(exception)
            raise

    def _data(self, data):
        if self.listener.on_data(data) is False:
            self.running = False

    def _read_loop(self, resp):

        while self.running:

            # Note: keep-alive newlines might be inserted before each length value.
            # read until we get a digit...
            c = '\n'
            for c in resp.iter_content():
                if c == '\n':
                    continue
                break

            delimited_string = c

            # read rest of delimiter length..
            d = ''
            for d in resp.iter_content():
                if d != '\n':
                    delimited_string += d
                    continue
                break

            # read the next twitter status object
            if delimited_string.strip().isdigit():
                next_status_obj = resp.raw.read( int(delimited_string) )
                if self.running:
                    self._data(next_status_obj)

        if resp.raw._fp.isclosed():
            self.on_closed(resp)

    def _start(self, async):
        self.running = True
        if async:
            self._thread = Thread(target=self._run)
            self._thread.start()
        else:
            self._run()

    def on_closed(self, resp):
        """ Called when the response has been closed by Twitter """
        pass

    def userstream(self, stall_warnings=False, _with=None, replies=None,
            track=None, locations=None, async=False, encoding='utf8'):
        self.session.params = {'delimited': 'length'}
        if self.running:
            raise TweepError('Stream object already connected!')
        self.url = '/%s/user.json' % STREAM_VERSION
        self.host='userstream.twitter.com'
        if stall_warnings:
            self.session.params['stall_warnings'] = stall_warnings
        if _with:
            self.session.params['with'] = _with
        if replies:
            self.session.params['replies'] = replies
        if locations and len(locations) > 0:
            if len(locations) % 4 != 0:
                raise TweepError("Wrong number of locations points, "
                                 "it has to be a multiple of 4")
            self.session.params['locations'] = ','.join(['%.2f' % l for l in locations])
        if track:
            encoded_track = [s.encode(encoding) for s in track]
            self.session.params['track'] = ','.join(encoded_track)

        self._start(async)

    def firehose(self, count=None, async=False):
        self.session.params = {'delimited': 'length'}
        if self.running:
            raise TweepError('Stream object already connected!')
        self.url = '/%s/statuses/firehose.json' % STREAM_VERSION
        if count:
            self.url += '&count=%s' % count
        self._start(async)

    def retweet(self, async=False):
        self.session.params = {'delimited': 'length'}
        if self.running:
            raise TweepError('Stream object already connected!')
        self.url = '/%s/statuses/retweet.json' % STREAM_VERSION
        self._start(async)

    def sample(self, async=False):
        if self.running:
            raise TweepError('Stream object already connected!')
        self.url = '/%s/statuses/sample.json?delimited=length' % STREAM_VERSION
        self._start(async)

    def filter(self, follow=None, track=None, async=False, locations=None,
               stall_warnings=False, languages=None, encoding='utf8'):
        self.session.params = {}
        self.session.headers['Content-type'] = "application/x-www-form-urlencoded"
        if self.running:
            raise TweepError('Stream object already connected!')
        self.url = '/%s/statuses/filter.json' % STREAM_VERSION
        if follow:
            encoded_follow = [s.encode(encoding) for s in follow]
            self.session.params['follow'] = ','.join(encoded_follow)
        if track:
            encoded_track = [s.encode(encoding) for s in track]
            self.session.params['track'] = ','.join(encoded_track)
        if locations and len(locations) > 0:
            if len(locations) % 4 != 0:
                raise TweepError("Wrong number of locations points, "
                                 "it has to be a multiple of 4")
            self.session.params['locations'] = ','.join(['%.4f' % l for l in locations])
        if stall_warnings:
            self.session.params['stall_warnings'] = stall_warnings
        if languages:
            self.session.params['language'] = ','.join(map(str, languages))
        self.body = urlencode_noplus(self.session.params)
        self.session.params['delimited'] = 'length'
        self.host = 'stream.twitter.com'
        self._start(async)

    def sitestream(self, follow, stall_warnings=False, with_='user', replies=False, async=False):
        self.parameters = {}
        if self.running:
            raise TweepError('Stream object already connected!')
        self.url = '/%s/site.json' % STREAM_VERSION
        self.parameters['follow'] = ','.join(map(str, follow))
        self.parameters['delimited'] = 'length'
        if stall_warnings:
            self.parameters['stall_warnings'] = stall_warnings
        if with_:
            self.parameters['with'] = with_
        if replies:
            self.parameters['replies'] = replies
        self.body = urlencode_noplus(self.parameters)
        self._start(async)

    def disconnect(self):
        if self.running is False:
            return
        self.running = False

