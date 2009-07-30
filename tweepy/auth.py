# Tweepy
# Copyright 2009 Joshua Roesslein
# See LICENSE

from urllib2 import Request, urlopen
import base64

import oauth
from error import TweepError

class AuthHandler(object):

  def apply_auth(self, headers):
    """Apply authentication headers to request"""
    raise NotImplemented

class BasicAuthHandler(AuthHandler):

  def __init__(self, username, password):
    self._b64up = base64.b64encode('%s:%s' % (username, password))

  def apply_auth(self, headers):
    headers['Authorization'] = 'Basic %s' % self._b64up

"""OAuth authentication handler"""
class OAuthHandler(AuthHandler):

  REQUEST_TOKEN_URL = 'http://twitter.com/oauth/request_token'
  AUTHORIZATION_URL = 'http://twitter.com/oauth/authorize'
  ACCESS_TOKEN_URL = 'http://twitter.com/oauth/access_token'

  def __init__(self, consumer_key, consumer_secrete):
    self._consumer = oauth.OAuthConsumer(consumer_key, consumer_secrete)
    self._sigmethod = oauth.OAuthSignatureMethod_HMAC_SHA1()
    self.request_token = None
    self.access_token = None

  def _get_request_token(self):
    try:
      request = oauth.OAuthRequest.from_consumer_and_token(self._consumer, http_url = self.REQUEST_TOKEN_URL)
      request.sign_request(self._sigmethod, self._consumer, None)
      resp = urlopen(Request(self.REQUEST_TOKEN_URL, headers=request.to_header()))
      return oauth.OAuthToken.from_string(resp.read())

    except Exception, e:
      raise TweepError(e)

  def get_authorization_url(self, callback=None):
    try:
      # get the request token
      self.request_token = self._get_request_token()

      # build auth request and return as url
      request = oauth.OAuthRequest.from_token_and_callback(
          token=token, callback=callback, http_url=self.AUTHORIZATION_URL)
      return request.to_url()

    except Exception, e:
      raise TweepError(e)

  def get_access_token(self):
    try:
      # build request
      request = oauth.OAuthRequest.from_consumer_and_token(self._consumer,
          token=self.request_token, http_url=self.ACCESS_TOKEN_URL)
      request.sign_request(self._sigmethod, self._consumer, self.request_token)

      # send request
      resp = urlopen(Request(self.ACCESS_TOKEN_URL, headers=request.to_header()))
      self.access_token = oauth.OAuthToken.from_string(resp.read())
    except Exception, e:
      raise TweepError(e)
      


