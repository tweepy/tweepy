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
  import json
except ImportError:
  import simplejson as json

class Stream(object):

  host = 'stream.twitter.com'

  def __init__(self, username, password, callback, timeout=2.0, retry_count = 3, 
                retry_time = 5.0, snooze_time = 10.0, buffer_size=1500):
    self.auth = BasicAuthHandler(username, password)
    self.running = False
    self.timeout = timeout
    self.retry_count = retry_count
    self.retry_time = retry_time
    self.snooze_time = snooze_time
    self.buffer_size = buffer_size
    self.callback = callback
    self.api = API()

  def _run(self):
    # setup
    headers = {}
    self.auth.apply_auth(None, None, headers, None)

    # enter loop
    error_counter = 0
    conn = None
    while self.running:
      if error_counter > self.retry_count:
        # quit if error count greater than retry count
        break
      try:
        conn = httplib.HTTPConnection(self.host, timeout=self.timeout)
        conn.request('POST', self.url, headers=headers)
        resp = conn.getresponse()
        if resp.status != 200:
          error_counter += 1
          sleep(self.retry_time)
        else:
          error_counter = 0
          self._read_loop(resp)
      except timeout:
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
        self.callback('status', status)
      elif 'delete' in data:
        self.callback('delete', json.loads(data)['delete']['status'])
      elif 'limit' in data:
        self.callback('limit', json.loads(data)['limit'])

  def firehose(self, count=None, ):
    if self.running:
      raise TweepError('Stream object already connected!')
    self.url = '/firehose.json?delimited=length'
    if count:
      self.url += '&count=%s' % count
    self.running = True
    Thread(target=self._run).start()

  def gardenhose(self):
    if self.running:
      raise TweepError('Stream object already connected!')
    self.url = '/gardenhose.json?delimited=length'
    self.running = True
    Thread(target=self._run).start()

  def birddog(self, follow, count=None):
    if self.running:
      raise TweepError('Stream object already connected!')
    self.url = '/birddog.json?delimited=length&follow=%s' % str(follow).strip('[]').replace(' ', '')
    if count:
      self.url += '&count=%s' % count
    self.running = True
    Thread(target=self._run).start()

  def shadow(self, follow, count=None):
    if self.running:
      raise TweepError('Stream object already connected!')
    self.url = '/shadow.json?delimited=length&follow=%s' % str(follow).strip('[]').replace(' ', '')
    if count:
      self.url += '&count=%s' % count
    self.running = True
    Thread(target=self._run).start()

  def spritzer(self):
    if self.running:
      raise TweepError('Stream object already connected!')
    self.url = '/spritzer.json?delimited=length'
    self.running = True
    Thread(target=self._run).start()

  def follow(self, follow=None):
    if self.running:
      raise TweepError('Stream object already connected!')
    self.url = '/follow.json?delimited=length'
    if follow:
      self.url += '&follow=%s' % str(follow).strip('[]').replace(' ', '')
    self.running = True
    Thread(target=self._run).start()

  def track(self, track=None):
    if self.running:
      raise TweepError('Stream object already connected!')
    self.url = '/track.json?delimited=length'
    if track:
      self.url += '&track=%s' % str(track).strip('[]').replace(' ', '')
    self.running = True
    Thread(target=self._run).start()
    
  def disconnect(self):
    if self.running is False:
      return
    self.running = False
      
