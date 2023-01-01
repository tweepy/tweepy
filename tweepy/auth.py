# Tweepy
# Copyright 2009-2023 Joshua Roesslein
# See LICENSE for details.

import logging
import warnings

import requests
from requests.auth import AuthBase, HTTPBasicAuth
from requests_oauthlib import OAuth1, OAuth1Session, OAuth2Session

from tweepy.errors import TweepyException

WARNING_MESSAGE = """Warning! Due to a Twitter API bug, signin_with_twitter
and access_type don't always play nice together. Details
https://dev.twitter.com/discussions/21281"""

log = logging.getLogger(__name__)


class OAuth1UserHandler:
    """OAuth 1.0a User Context authentication handler

    .. versionchanged:: 4.5
        Renamed from :class:`OAuthHandler`
    """

    def __init__(self, consumer_key, consumer_secret, access_token=None,
                 access_token_secret=None, callback=None):
        if not isinstance(consumer_key, (str, bytes)):
            raise TypeError("Consumer key must be string or bytes, not "
                            + type(consumer_key).__name__)
        if not isinstance(consumer_secret, (str, bytes)):
            raise TypeError("Consumer secret must be string or bytes, not "
                            + type(consumer_secret).__name__)

        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.callback = callback
        self.username = None
        self.request_token = {}
        self.oauth = OAuth1Session(consumer_key, client_secret=consumer_secret,
                                   callback_uri=self.callback)

    def apply_auth(self):
        return OAuth1(
            self.consumer_key, client_secret=self.consumer_secret,
            resource_owner_key=self.access_token,
            resource_owner_secret=self.access_token_secret, decoding=None
        )

    def _get_oauth_url(self, endpoint):
        return 'https://api.twitter.com/oauth/' + endpoint

    def _get_request_token(self, access_type=None):
        try:
            url = self._get_oauth_url('request_token')
            if access_type:
                url += f'?x_auth_access_type={access_type}'
            return self.oauth.fetch_request_token(url)
        except Exception as e:
            raise TweepyException(e)

    def get_authorization_url(self, signin_with_twitter=False,
                              access_type=None):
        """Get the authorization URL to redirect the user to"""
        try:
            if signin_with_twitter:
                url = self._get_oauth_url('authenticate')
                if access_type:
                    log.warning(WARNING_MESSAGE)
            else:
                url = self._get_oauth_url('authorize')
            self.request_token = self._get_request_token(
                access_type=access_type
            )
            return self.oauth.authorization_url(url)
        except Exception as e:
            raise TweepyException(e)

    def get_access_token(self, verifier=None):
        """After user has authorized the app, get access token and secret with
        verifier
        """
        try:
            url = self._get_oauth_url('access_token')
            self.oauth = OAuth1Session(
                self.consumer_key, client_secret=self.consumer_secret,
                resource_owner_key=self.request_token['oauth_token'],
                resource_owner_secret=self.request_token['oauth_token_secret'],
                verifier=verifier, callback_uri=self.callback
            )
            resp = self.oauth.fetch_access_token(url)
            self.access_token = resp['oauth_token']
            self.access_token_secret = resp['oauth_token_secret']
            return self.access_token, self.access_token_secret
        except Exception as e:
            raise TweepyException(e)

    def set_access_token(self, key, secret):
        """
        .. deprecated:: 4.5
            Set through initialization instead.
        """
        self.access_token = key
        self.access_token_secret = secret


class OAuthHandler(OAuth1UserHandler):
    """Alias for :class:`OAuth1UserHandler`

    .. deprecated:: 4.5
        Use :class:`OAuth1UserHandler` instead.
    """

    def __init__(self, consumer_key, consumer_secret, access_token=None,
                 access_token_secret=None, callback=None):
        warnings.warn(
            "OAuthHandler is deprecated; use OAuth1UserHandler instead.",
            DeprecationWarning
        )
        super().__init__(consumer_key, consumer_secret, access_token, 
                         access_token_secret, callback)


class OAuth2AppHandler:
    """OAuth 2.0 Bearer Token (App-Only) using API / Consumer key and secret
    authentication handler

    .. versionchanged:: 4.5
        Renamed from :class:`AppAuthHandler`
    """

    def __init__(self, consumer_key, consumer_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self._bearer_token = ''

        resp = requests.post(
            'https://api.twitter.com/oauth2/token',
            auth=(self.consumer_key, self.consumer_secret),
            data={'grant_type': 'client_credentials'}
        )
        data = resp.json()
        if data.get('token_type') != 'bearer':
            raise TweepyException('Expected token_type to equal "bearer", '
                                  f'but got {data.get("token_type")} instead')

        self._bearer_token = data['access_token']

    def apply_auth(self):
        return OAuth2BearerHandler(self._bearer_token)


class AppAuthHandler(OAuth2AppHandler):
    """Alias for :class:`OAuth2AppHandler`

    .. deprecated:: 4.5
        Use :class:`OAuth2AppHandler` instead.
    """

    def __init__(self, consumer_key, consumer_secret):
        warnings.warn(
            "AppAuthHandler is deprecated; use OAuth2AppHandler instead.",
            DeprecationWarning
        )
        super().__init__(consumer_key, consumer_secret)


class OAuth2BearerHandler(AuthBase):
    """OAuth 2.0 Bearer Token (App-Only) authentication handler

    .. versionadded:: 4.5
    """

    def __init__(self, bearer_token):
        self.bearer_token = bearer_token

    def __call__(self, request):
        request.headers['Authorization'] = 'Bearer ' + self.bearer_token
        return request

    def apply_auth(self):
        return self


class OAuth2UserHandler(OAuth2Session):
    """OAuth 2.0 Authorization Code Flow with PKCE (User Context)
    authentication handler

    .. versionadded:: 4.5
    """

    def __init__(self, *, client_id, redirect_uri, scope, client_secret=None):
        super().__init__(client_id, redirect_uri=redirect_uri, scope=scope)
        if client_secret is not None:
            self.auth = HTTPBasicAuth(client_id, client_secret)
        else:
            self.auth = None

    def get_authorization_url(self):
        """Get the authorization URL to redirect the user to"""
        authorization_url, state = self.authorization_url(
            "https://twitter.com/i/oauth2/authorize",
            code_challenge=self._client.create_code_challenge(
                self._client.create_code_verifier(128), "S256"
            ), code_challenge_method="S256"
        )
        return authorization_url

    def fetch_token(self, authorization_response):
        """After user has authorized the app, fetch access token with
        authorization response URL
        """
        return super().fetch_token(
            "https://api.twitter.com/2/oauth2/token",
            authorization_response=authorization_response,
            auth=self.auth,
            include_client_id=True,
            code_verifier=self._client.code_verifier
        )
