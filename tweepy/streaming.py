# Tweepy
# Copyright 2009 Joshua Roesslein
# See LICENSE

import httplib
from threading import Thread

from . auth import BasicAuthHandler
from . parsers import parse_status
from . api import API
from . error import TweepError

try:
  import json
except ImportError:
  import simplejson as json

class Stream(object):

  def __init__(self, username, password, callback, host='stream.twitter.com', buffer_size=1500):
    self.host = host
    self.auth = BasicAuthHandler(username, password)
    self.running = False
    self.buffer_size = buffer_size
    self.callback = callback

  def _run(self):
    api = API()
    conn = httplib.HTTPConnection(self.host, timeout=5)
    headers = {}
    self.auth.apply_auth(None, None, headers, None)
    conn.request('POST', self.url, headers=headers)
    resp = conn.getresponse()
    data = ''
    while self.running:
      if resp.isclosed():
        break

      # read length
      length = ''
      while resp.isclosed() is False:
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
        status = parse_status(data, api)
        self.callback(status)

      # TODO: we should probably also parse delete/track messages
      # and pass to a callback

    conn.close()
    self.running = False

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
      
