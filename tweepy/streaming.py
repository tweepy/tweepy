# Tweepy
# Copyright 2009 Joshua Roesslein
# See LICENSE

import httplib
from socket import timeout
from threading import Thread
from time import sleep

from . auth import BasicAuthHandler
from . parsers import parse_status
from . api import API
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

STREAM_VERSION = 1


class StreamListener(object):

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


class Stream(object):

    host = 'stream.twitter.com'

    def __init__(self, username, password, listener, timeout=5.0, retry_count = None,
                    retry_time = 10.0, snooze_time = 5.0, buffer_size=1500):
        self.auth = BasicAuthHandler(username, password)
        self.running = False
        self.timeout = timeout
        self.retry_count = retry_count
        self.retry_time = retry_time
        self.snooze_time = snooze_time
        self.buffer_size = buffer_size
        self.listener = listener
        self.api = API()

    def _run(self):
        # setup
        headers = {}
        self.auth.apply_auth(None, None, headers, None)

        # enter loop
        error_counter = 0
        conn = None
        while self.running:
            if self.retry_count and error_counter > self.retry_count:
                # quit if error count greater than retry count
                break
            try:
                conn = httplib.HTTPConnection(self.host)
                conn.connect()
                conn.sock.settimeout(self.timeout)
                conn.request('POST', self.url, headers=headers)
                resp = conn.getresponse()
                if resp.status != 200:
                    if self.listener.on_error(resp.status) is False:
                        break
                    error_counter += 1
                    sleep(self.retry_time)
                else:
                    error_counter = 0
                    self._read_loop(resp)
            except timeout:
                if self.listener.on_timeout() == False:
                    break
                if self.running is False:
                    break
                conn.close()
                sleep(self.snooze_time)
            except Exception:
                # any other exception is fatal, so kill loop
                break

        # cleanup
        self.running = False
        if conn:
            conn.close()

    def _read_loop(self, resp):
        data = ''
        while self.running:
            if resp.isclosed():
                break

            # read length
            length = ''
            while True:
                c = resp.read(1)
                if c == '\n':
                    break
                length += c
            length = length.strip()
            if length.isdigit():
                length = int(length)
            else:
                continue

            # read data
            data = resp.read(length)

            # turn json data into status object
            if 'in_reply_to_status_id' in data:
                status = parse_status(data, self.api)
                if self.listener.on_status(status) == False:
                    self.running = False
            elif 'delete' in data:
                delete = json.loads(data)['delete']['status']
                if self.listener.on_delete(delete['id'], delete['user_id']) == False:
                    self.running = False
            elif 'limit' in data:
                if self.listener.on_limit(json.loads(data)['limit']['track']) == False:
                    self.running = False

    def firehose(self, count=None):
        if self.running:
            raise TweepError('Stream object already connected!')
        self.url = '/%i/statuses/firehose.json?delimited=length' % STREAM_VERSION
        if count:
            self.url += '&count=%s' % count
        self.running = True
        Thread(target=self._run).start()

    def sample(self, count=None):
        if self.running:
            raise TweepError('Stream object already connected!')
        self.url = '/%i/statuses/sample.json?delimited=length' % STREAM_VERSION
        if count:
            self.url += '&count=%s' % count
        self.running = True
        Thread(target=self._run).start()

    def filter(self, follow=None, track=None):
        if self.running:
            raise TweepError('Stream object already connected!')
        self.url = '/%i/statuses/filter.json?delimited=length' % STREAM_VERSION
        if follow:
            self.url += '&follow=%s' % ','.join(follow)
        if track:
            self.url += '&track=%s' % ','.join(track)
        print self.url
        self.running = True
        Thread(target=self._run).start()

    def disconnect(self):
        if self.running is False:
            return
        self.running = False

