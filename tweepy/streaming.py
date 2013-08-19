# Tweepy
# Copyright 2009-2010 Joshua Roesslein
# See LICENSE for details.

import logging
import httplib
from socket import timeout
from threading import Thread
from time import sleep

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
        data = json.loads(raw_data)

        if 'in_reply_to_status_id' in data:
            status = Status.parse(self.api, data)
            if self.on_status(status) is False:
                return False
        elif 'delete' in data:
            delete = data['delete']['status']
            if self.on_delete(delete['id'], delete['user_id']) is False:
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

    def on_delete(self, status_id, user_id):
        """Called when a delete notice arrives for a status"""
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
        self.retry_time = options.get("retry_time", 10.0)
        self.snooze_time = options.get("snooze_time",  5.0)
        self.buffer_size = options.get("buffer_size",  1500)
        if options.get("secure", True):
            self.scheme = "https"
        else:
            self.scheme = "http"

        self.api = API()
        self.headers = options.get("headers") or {}
        self.parameters = None
        self.body = None

    def _run(self):
        # Authenticate
        url = "%s://%s%s" % (self.scheme, self.host, self.url)

        # Connect and process the stream
        error_counter = 0
        conn = None
        exception = None
        while self.running:
            if self.retry_count is not None and error_counter > self.retry_count:
                # quit if error count greater than retry count
                break
            try:
                if self.scheme == "http":
                    conn = httplib.HTTPConnection(self.host, timeout=self.timeout)
                else:
                    conn = httplib.HTTPSConnection(self.host, timeout=self.timeout)
                self.auth.apply_auth(url, 'POST', self.headers, self.parameters)
                conn.connect()
                conn.request('POST', self.url, self.body, headers=self.headers)
                resp = conn.getresponse()
                if resp.status != 200:
                    if self.listener.on_error(resp.status) is False:
                        break
                    error_counter += 1
                    sleep(self.retry_time)
                else:
                    error_counter = 0
                    self.listener.on_connect()
                    self._read_loop(resp)
            except timeout:
                if self.listener.on_timeout() == False:
                    break
                if self.running is False:
                    break
                conn.close()
                sleep(self.snooze_time)
            except Exception, exception:
                # any other exception is fatal, so kill loop
                break

        # cleanup
        self.running = False
        if conn:
            conn.close()

        if exception:
            raise

    def _data(self, data):
        if self.listener.on_data(data) is False:
            self.running = False

    def _read_loop(self, resp):

        while self.running and not resp.isclosed():

            # Note: keep-alive newlines might be inserted before each length value.
            # read until we get a digit...
            c = '\n'
            while c == '\n' and self.running and not resp.isclosed():
                c = resp.read(1)
            delimited_string = c

            # read rest of delimiter length..
            d = ''
            while d != '\n' and self.running and not resp.isclosed():
                d = resp.read(1)
                delimited_string += d

            # read the next twitter status object
            if delimited_string.strip().isdigit():
                next_status_obj = resp.read( int(delimited_string) )
                self._data(next_status_obj)

        if resp.isclosed():
            self.on_closed(resp)

    def _start(self, async):
        self.running = True
        if async:
            Thread(target=self._run).start()
        else:
            self._run()

    def on_closed(self, resp):
        """ Called when the response has been closed by Twitter """
        pass

    def userstream(self, count=None, async=False, secure=True):
        self.parameters = {'delimited': 'length'}
        if self.running:
            raise TweepError('Stream object already connected!')
        self.url = '/2/user.json?delimited=length'
        self.host='userstream.twitter.com'
        self._start(async)

    def firehose(self, count=None, async=False):
        self.parameters = {'delimited': 'length'}
        if self.running:
            raise TweepError('Stream object already connected!')
        self.url = '/%s/statuses/firehose.json?delimited=length' % STREAM_VERSION
        if count:
            self.url += '&count=%s' % count
        self._start(async)

    def retweet(self, async=False):
        self.parameters = {'delimited': 'length'}
        if self.running:
            raise TweepError('Stream object already connected!')
        self.url = '/%s/statuses/retweet.json?delimited=length' % STREAM_VERSION
        self._start(async)

    def sample(self, count=None, async=False):
        self.parameters = {'delimited': 'length'}
        if self.running:
            raise TweepError('Stream object already connected!')
        self.url = '/%s/statuses/sample.json?delimited=length' % STREAM_VERSION
        if count:
            self.url += '&count=%s' % count
        self._start(async)

    def filter(self, follow=None, track=None, async=False, locations=None, 
        count = None, stall_warnings=False, languages=None):
        self.parameters = {}
        self.headers['Content-type'] = "application/x-www-form-urlencoded"
        if self.running:
            raise TweepError('Stream object already connected!')
        self.url = '/%s/statuses/filter.json?delimited=length' % STREAM_VERSION
        if follow:
            self.parameters['follow'] = ','.join(map(str, follow))
        if track:
            self.parameters['track'] = ','.join(map(str, track))
        if locations and len(locations) > 0:
            assert len(locations) % 4 == 0
            self.parameters['locations'] = ','.join(['%.2f' % l for l in locations])
        if count:
            self.parameters['count'] = count
        if stall_warnings:
            self.parameters['stall_warnings'] = stall_warnings
        if languages:
            self.parameters['language'] = ','.join(map(str, languages))
        self.body = urlencode_noplus(self.parameters)
        self.parameters['delimited'] = 'length'
        self._start(async)

    def disconnect(self):
        if self.running is False:
            return
        self.running = False

