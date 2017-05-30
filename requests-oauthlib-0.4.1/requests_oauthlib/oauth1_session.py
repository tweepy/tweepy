from __future__ import unicode_literals

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

import logging

from oauthlib.common import add_params_to_uri, urldecode
from oauthlib.oauth1 import SIGNATURE_HMAC, SIGNATURE_TYPE_AUTH_HEADER
import requests

from . import OAuth1

import sys
if sys.version > "3":
    unicode = str


log = logging.getLogger(__name__)


class TokenRequestDenied(ValueError):

    def __init__(self, message, status_code):
        super(TokenRequestDenied, self).__init__(message)
        self.status_code = status_code


class OAuth1Session(requests.Session):
    """Request signing and convenience methods for the oauth dance.

    What is the difference between OAuth1Session and OAuth1?

    OAuth1Session actually uses OAuth1 internally and it's purpose is to assist
    in the OAuth workflow through convenience methods to prepare authorization
    URLs and parse the various token and redirection responses. It also provide
    rudimentary validation of responses.

    An example of the OAuth workflow using a basic CLI app and Twitter.

    >>> # Credentials obtained during the registration.
    >>> client_key = 'client key'
    >>> client_secret = 'secret'
    >>> callback_uri = 'https://127.0.0.1/callback'
    >>>
    >>> # Endpoints found in the OAuth provider API documentation
    >>> request_token_url = 'https://api.twitter.com/oauth/request_token'
    >>> authorization_url = 'https://api.twitter.com/oauth/authorize'
    >>> access_token_url = 'https://api.twitter.com/oauth/access_token'
    >>>
    >>> oauth_session = OAuth1Session(client_key,client_secret=client_secret, callback_uri=callback_uri)
    >>>
    >>> # First step, fetch the request token.
    >>> oauth_session.fetch_request_token(request_token_url)
    {
        'oauth_token': 'kjerht2309u',
        'oauth_token_secret': 'lsdajfh923874',
    }
    >>>
    >>> # Second step. Follow this link and authorize
    >>> oauth_session.authorization_url(authorization_url)
    'https://api.twitter.com/oauth/authorize?oauth_token=sdf0o9823sjdfsdf&oauth_callback=https%3A%2F%2F127.0.0.1%2Fcallback'
    >>>
    >>> # Third step. Fetch the access token
    >>> redirect_response = raw_input('Paste the full redirect URL here.')
    >>> oauth_session.parse_authorization_response(redirect_response)
    {
        'oauth_token: 'kjerht2309u',
        'oauth_token_secret: 'lsdajfh923874',
        'oauth_verifier: 'w34o8967345',
    }
    >>> oauth_session.fetch_access_token(access_token_url)
    {
        'oauth_token': 'sdf0o9823sjdfsdf',
        'oauth_token_secret': '2kjshdfp92i34asdasd',
    }
    >>> # Done. You can now make OAuth requests.
    >>> status_url = 'http://api.twitter.com/1/statuses/update.json'
    >>> new_status = {'status':  'hello world!'}
    >>> oauth_session.post(status_url, data=new_status)
    <Response [200]>
    """

    def __init__(self, client_key,
            client_secret=None,
            resource_owner_key=None,
            resource_owner_secret=None,
            callback_uri=None,
            signature_method=SIGNATURE_HMAC,
            signature_type=SIGNATURE_TYPE_AUTH_HEADER,
            rsa_key=None,
            verifier=None,
            client_class=None,
            force_include_body=False,
            **kwargs):
        """Construct the OAuth 1 session.

        :param client_key: A client specific identifier.
        :param client_secret: A client specific secret used to create HMAC and
                              plaintext signatures.
        :param resource_owner_key: A resource owner key, also referred to as
                                   request token or access token depending on
                                   when in the workflow it is used.
        :param resource_owner_secret: A resource owner secret obtained with
                                      either a request or access token. Often
                                      referred to as token secret.
        :param callback_uri: The URL the user is redirect back to after
                             authorization.
        :param signature_method: Signature methods determine how the OAuth
                                 signature is created. The three options are
                                 oauthlib.oauth1.SIGNATURE_HMAC (default),
                                 oauthlib.oauth1.SIGNATURE_RSA and
                                 oauthlib.oauth1.SIGNATURE_PLAIN.
        :param signature_type: Signature type decides where the OAuth
                               parameters are added. Either in the
                               Authorization header (default) or to the URL
                               query parameters or the request body. Defined as
                               oauthlib.oauth1.SIGNATURE_TYPE_AUTH_HEADER,
                               oauthlib.oauth1.SIGNATURE_TYPE_QUERY and
                               oauthlib.oauth1.SIGNATURE_TYPE_BODY
                               respectively.
        :param rsa_key: The private RSA key as a string. Can only be used with
                        signature_method=oauthlib.oauth1.SIGNATURE_RSA.
        :param verifier: A verifier string to prove authorization was granted.
        :param client_class: A subclass of `oauthlib.oauth1.Client` to use with
                             `requests_oauthlib.OAuth1` instead of the default
        :param force_include_body: Always include the request body in the
                                   signature creation.
        :param **kwargs: Additional keyword arguments passed to `OAuth1`
        """
        super(OAuth1Session, self).__init__()
        self._client = OAuth1(client_key,
                client_secret=client_secret,
                resource_owner_key=resource_owner_key,
                resource_owner_secret=resource_owner_secret,
                callback_uri=callback_uri,
                signature_method=signature_method,
                signature_type=signature_type,
                rsa_key=rsa_key,
                verifier=verifier,
                client_class=client_class,
                force_include_body=force_include_body,
                **kwargs)
        self.auth = self._client

    def authorization_url(self, url, request_token=None, **kwargs):
        """Create an authorization URL by appending request_token and optional
        kwargs to url.

        This is the second step in the OAuth 1 workflow. The user should be
        redirected to this authorization URL, grant access to you, and then
        be redirected back to you. The redirection back can either be specified
        during client registration or by supplying a callback URI per request.

        :param url: The authorization endpoint URL.
        :param request_token: The previously obtained request token.
        :param kwargs: Optional parameters to append to the URL.
        :returns: The authorization URL with new parameters embedded.

        An example using a registered default callback URI.

        >>> request_token_url = 'https://api.twitter.com/oauth/request_token'
        >>> authorization_url = 'https://api.twitter.com/oauth/authorize'
        >>> oauth_session = OAuth1Session('client-key', client_secret='secret')
        >>> oauth_session.fetch_request_token(request_token_url)
        {
            'oauth_token': 'sdf0o9823sjdfsdf',
            'oauth_token_secret': '2kjshdfp92i34asdasd',
        }
        >>> oauth_session.authorization_url(authorization_url)
        'https://api.twitter.com/oauth/authorize?oauth_token=sdf0o9823sjdfsdf'
        >>> oauth_session.authorization_url(authorization_url, foo='bar')
        'https://api.twitter.com/oauth/authorize?oauth_token=sdf0o9823sjdfsdf&foo=bar'

        An example using an explicit callback URI.

        >>> request_token_url = 'https://api.twitter.com/oauth/request_token'
        >>> authorization_url = 'https://api.twitter.com/oauth/authorize'
        >>> oauth_session = OAuth1Session('client-key', client_secret='secret', callback_uri='https://127.0.0.1/callback')
        >>> oauth_session.fetch_request_token(request_token_url)
        {
            'oauth_token': 'sdf0o9823sjdfsdf',
            'oauth_token_secret': '2kjshdfp92i34asdasd',
        }
        >>> oauth_session.authorization_url(authorization_url)
        'https://api.twitter.com/oauth/authorize?oauth_token=sdf0o9823sjdfsdf&oauth_callback=https%3A%2F%2F127.0.0.1%2Fcallback'
        """
        kwargs['oauth_token'] = request_token or self._client.client.resource_owner_key
        log.debug('Adding parameters %s to url %s', kwargs, url)
        return add_params_to_uri(url, kwargs.items())

    def fetch_request_token(self, url, realm=None):
        """Fetch a request token.

        This is the first step in the OAuth 1 workflow. A request token is
        obtained by making a signed post request to url. The token is then
        parsed from the application/x-www-form-urlencoded response and ready
        to be used to construct an authorization url.

        :param url: The request token endpoint URL.
        :param realm: A list of realms to request access to.
        :returns: The response in dict format.

        Note that a previously set callback_uri will be reset for your
        convenience, or else signature creation will be incorrect on
        consecutive requests.

        >>> request_token_url = 'https://api.twitter.com/oauth/request_token'
        >>> oauth_session = OAuth1Session('client-key', client_secret='secret')
        >>> oauth_session.fetch_request_token(request_token_url)
        {
            'oauth_token': 'sdf0o9823sjdfsdf',
            'oauth_token_secret': '2kjshdfp92i34asdasd',
        }
        """
        self._client.client.realm = ' '.join(realm) if realm else None
        token = self._fetch_token(url)
        log.debug('Resetting callback_uri and realm (not needed in next phase).')
        self._client.client.callback_uri = None
        self._client.client.realm = None
        return token

    def fetch_access_token(self, url):
        """Fetch an access token.

        This is the final step in the OAuth 1 workflow. An access token is
        obtained using all previously obtained credentials, including the
        verifier from the authorization step.

        Note that a previously set verifier will be reset for your
        convenience, or else signature creation will be incorrect on
        consecutive requests.

        >>> access_token_url = 'https://api.twitter.com/oauth/access_token'
        >>> redirect_response = 'https://127.0.0.1/callback?oauth_token=kjerht2309uf&oauth_token_secret=lsdajfh923874&oauth_verifier=w34o8967345'
        >>> oauth_session = OAuth1Session('client-key', client_secret='secret')
        >>> oauth_session.parse_authorization_response(redirect_response)
        {
            'oauth_token: 'kjerht2309u',
            'oauth_token_secret: 'lsdajfh923874',
            'oauth_verifier: 'w34o8967345',
        }
        >>> oauth_session.fetch_access_token(access_token_url)
        {
            'oauth_token': 'sdf0o9823sjdfsdf',
            'oauth_token_secret': '2kjshdfp92i34asdasd',
        }
        """
        if not getattr(self._client.client, 'verifier', None):
            raise ValueError('No client verifier has been set.')
        token = self._fetch_token(url)
        log.debug('Resetting verifier attribute, should not be used anymore.')
        self._client.client.verifier = None
        return token

    def parse_authorization_response(self, url):
        """Extract parameters from the post authorization redirect response URL.

        :param url: The full URL that resulted from the user being redirected
                    back from the OAuth provider to you, the client.
        :returns: A dict of parameters extracted from the URL.

        >>> redirect_response = 'https://127.0.0.1/callback?oauth_token=kjerht2309uf&oauth_token_secret=lsdajfh923874&oauth_verifier=w34o8967345'
        >>> oauth_session = OAuth1Session('client-key', client_secret='secret')
        >>> oauth_session.parse_authorization_response(redirect_response)
        {
            'oauth_token: 'kjerht2309u',
            'oauth_token_secret: 'lsdajfh923874',
            'oauth_verifier: 'w34o8967345',
        }
        """
        log.debug('Parsing token from query part of url %s', url)
        token = dict(urldecode(urlparse(url).query))
        log.debug('Updating internal client token attribute.')
        self._populate_attributes(token)
        return token

    def _populate_attributes(self, token):
        if 'oauth_token' in token:
            self._client.client.resource_owner_key = token['oauth_token']
        else:
            raise ValueError('Response does not contain a token. %s', token)
        if 'oauth_token_secret' in token:
            self._client.client.resource_owner_secret = (
                token['oauth_token_secret'])
        if 'oauth_verifier' in token:
            self._client.client.verifier = token['oauth_verifier']

    def _fetch_token(self, url):
        log.debug('Fetching token from %s using client %s', url, self._client.client)
        r = self.post(url)

        if r.status_code >= 400:
            error = "Token request failed with code %s, response was '%s'."
            raise TokenRequestDenied(error % (r.status_code, r.text), r.status_code)

        log.debug('Decoding token from response "%s"', r.text)
        try:
            token = dict(urldecode(r.text))
        except ValueError as e:
            error = ("Unable to decode token from token response. "
                     "This is commonly caused by an unsuccessful request where"
                     " a non urlencoded error message is returned. "
                     "The decoding error was %s""" % e)
            raise ValueError(error)

        log.debug('Obtained token %s', token)
        log.debug('Updating internal client attributes from token data.')
        self._populate_attributes(token)
        return token

    def rebuild_auth(self, prepared_request, response):
        """
        When being redirected we should always strip Authorization
        header, since nonce may not be reused as per OAuth spec.
        """
        prepared_request.headers.pop('Authorization', True)
        prepared_request.prepare_auth(self.auth)
        return
