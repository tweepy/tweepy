#Embedded file name: /home/aaron/repos/tweepy/tweepy/auth.py
from urllib2 import Request, urlopen
import base64
from tweepy.error import TweepError
from tweepy.api import API
import requests
from requests_oauthlib import OAuth1Session, OAuth1

class AuthHandler(object):

    def apply_auth(self, url, method, headers, parameters):
        """Apply authentication headers to request"""
        raise NotImplementedError

    def get_username(self):
        """Return the username of the authenticated user"""
        raise NotImplementedError


class OAuthHandler(AuthHandler):
    """OAuth authentication handler"""
    OAUTH_HOST = 'api.twitter.com'
    OAUTH_ROOT = '/oauth/'

    def __init__(self, consumer_key, consumer_secret, callback=None, secure=False):
        if type(consumer_key) == unicode:
            consumer_key = bytes(consumer_key)

        if type(consumer_secret) == unicode:
            consumer_secret = bytes(consumer_secret)

        self._consumer = oauth.OAuthConsumer(consumer_key, consumer_secret)
        self._sigmethod = oauth.OAuthSignatureMethod_HMAC_SHA1()
        self.request_token = None
        self.access_token = None
        self.callback = callback
        self.username = None
        self.secure = secure
        self.oauth = OAuth1Session(consumer_key, client_secret=consumer_secret, callback_uri=self.callback)

    def _get_oauth_url(self, endpoint, secure = False):
        if self.secure or secure:
            prefix = 'https://'
        else:
            prefix = 'http://'
        return prefix + self.OAUTH_HOST + self.OAUTH_ROOT + endpoint

    def apply_auth(self):
        return OAuth1(self.consumer_key, client_secret=self.consumer_secret, resource_owner_key=self.access_token, resource_owner_secret=self.access_token_secret)

    def _get_request_token(self):
        try:
            url = self._get_oauth_url('request_token')
            return self.oauth.fetch_request_token(url)
            request = oauth.OAuthRequest.from_consumer_and_token(self._consumer, http_url=url, callback=self.callback)
            request.sign_request(self._sigmethod, self._consumer, None)
            resp = urlopen(Request(url, headers=request.to_header()))
            return oauth.OAuthToken.from_string(resp.read())
        except Exception as e:
            raise TweepError(e)

    def set_access_token(self, key, secret):
        self.access_token = key
        self.access_token_secret = secret

    def get_authorization_url(self, signin_with_twitter = False):
        """Get the authorization URL to redirect the user"""
        try:
            if signin_with_twitter:
                url = self._get_oauth_url('authenticate')
            else:
                url = self._get_oauth_url('authorize')
            self.request_token = self._get_request_token()
            return self.oauth.authorization_url(url)
            token = oauth.fetch_request_token(url)
            request = oauth.OAuthRequest.from_token_and_callback(token=self.request_token, http_url=url)
            return request.to_url()
        except Exception as e:
            raise TweepError(e)

    def get_access_token(self, verifier = None):
        """
        After user has authorized the request token, get access token
        with user supplied verifier.
        """
        try:
            url = self._get_oauth_url('access_token')
            self.oauth = OAuth1Session(self.consumer_key, client_secret=self.consumer_secret, resource_owner_key=self.request_token['oauth_token'], resource_owner_secret=self.request_token['oauth_token_secret'], verifier=verifier, callback_uri=self.callback)
            resp = self.oauth.fetch_access_token(url)
            self.access_token = resp['oauth_token']
            self.access_token_secret = resp['oauth_token_secret']
            return (self.access_token, self.access_token_secret)
            request = oauth.OAuthRequest.from_consumer_and_token(self._consumer, token=self.request_token, http_url=url, verifier=str(verifier))
            request.sign_request(self._sigmethod, self._consumer, self.request_token)
            resp = urlopen(Request(url, headers=request.to_header()))
            self.access_token = oauth.OAuthToken.from_string(resp.read())
            return self.access_token
        except Exception as e:
            raise TweepError(e)

    def get_xauth_access_token(self, username, password):
        """
        Get an access token from an username and password combination.
        In order to get this working you need to create an app at
        http://twitter.com/apps, after that send a mail to api@twitter.com
        and request activation of xAuth for it.
        """
        try:
            url = self._get_oauth_url('access_token', secure=True)
            request = oauth.OAuthRequest.from_consumer_and_token(oauth_consumer=self._consumer, http_method='POST', http_url=url, parameters={'x_auth_mode': 'client_auth',
             'x_auth_username': username,
             'x_auth_password': password})
            request.sign_request(self._sigmethod, self._consumer, None)
            resp = urlopen(Request(url, data=request.to_postdata()))
            self.access_token = oauth.OAuthToken.from_string(resp.read())
            return self.access_token
        except Exception as e:
            raise TweepError(e)

    def get_username(self):
        if self.username is None:
            api = API(self)
            user = api.verify_credentials()
            if user:
                self.username = user.screen_name
            else:
                raise TweepError('Unable to get username, invalid oauth token!')
        return self.username
