"""
oauthlib.oauth2.rfc6749.tokens
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains methods for adding two types of access tokens to requests.

- Bearer http://tools.ietf.org/html/rfc6750
- MAC http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-01

"""
from __future__ import absolute_import, unicode_literals

from binascii import b2a_base64
import hashlib
import hmac
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

from oauthlib.common import add_params_to_uri, add_params_to_qs, unicode_type
from oauthlib import common
from . import utils


def prepare_mac_header(token, uri, key, http_method,
                       nonce=None,
                       headers=None,
                       body=None,
                       ext='',
                       hash_algorithm='hmac-sha-1',
                       issue_time=None,
                       draft=0):
    """Add an `MAC Access Authentication`_ signature to headers.

    Unlike OAuth 1, this HMAC signature does not require inclusion of the
    request payload/body, neither does it use a combination of client_secret
    and token_secret but rather a mac_key provided together with the access
    token.

    Currently two algorithms are supported, "hmac-sha-1" and "hmac-sha-256",
    `extension algorithms`_ are not supported.

    Example MAC Authorization header, linebreaks added for clarity

    Authorization: MAC id="h480djs93hd8",
                       nonce="1336363200:dj83hs9s",
                       mac="bhCQXTVyfj5cmA9uKkPFx1zeOXM="

    .. _`MAC Access Authentication`: http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-01
    .. _`extension algorithms`: http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-01#section-7.1

    :param uri: Request URI.
    :param headers: Request headers as a dictionary.
    :param http_method: HTTP Request method.
    :param key: MAC given provided by token endpoint.
    :param hash_algorithm: HMAC algorithm provided by token endpoint.
    :param issue_time: Time when the MAC credentials were issued (datetime).
    :param draft: MAC authentication specification version.
    :return: headers dictionary with the authorization field added.
    """
    http_method = http_method.upper()
    host, port = utils.host_from_uri(uri)

    if hash_algorithm.lower() == 'hmac-sha-1':
        h = hashlib.sha1
    elif hash_algorithm.lower() == 'hmac-sha-256':
        h = hashlib.sha256
    else:
        raise ValueError('unknown hash algorithm')

    if draft == 0:
        nonce = nonce or '{0}:{1}'.format(utils.generate_age(issue_time),
                                          common.generate_nonce())
    else:
        ts = common.generate_timestamp()
        nonce = common.generate_nonce()

    sch, net, path, par, query, fra = urlparse(uri)

    if query:
        request_uri = path + '?' + query
    else:
        request_uri = path

    # Hash the body/payload
    if body is not None and draft == 0:
        body = body.encode('utf-8')
        bodyhash = b2a_base64(h(body).digest())[:-1].decode('utf-8')
    else:
        bodyhash = ''

    # Create the normalized base string
    base = []
    if draft == 0:
        base.append(nonce)
    else:
        base.append(ts)
        base.append(nonce)
    base.append(http_method.upper())
    base.append(request_uri)
    base.append(host)
    base.append(port)
    if draft == 0:
        base.append(bodyhash)
    base.append(ext or '')
    base_string = '\n'.join(base) + '\n'

    # hmac struggles with unicode strings - http://bugs.python.org/issue5285
    if isinstance(key, unicode_type):
        key = key.encode('utf-8')
    sign = hmac.new(key, base_string.encode('utf-8'), h)
    sign = b2a_base64(sign.digest())[:-1].decode('utf-8')

    header = []
    header.append('MAC id="%s"' % token)
    if draft != 0:
        header.append('ts="%s"' % ts)
    header.append('nonce="%s"' % nonce)
    if bodyhash:
        header.append('bodyhash="%s"' % bodyhash)
    if ext:
        header.append('ext="%s"' % ext)
    header.append('mac="%s"' % sign)

    headers = headers or {}
    headers['Authorization'] = ', '.join(header)
    return headers


def prepare_bearer_uri(token, uri):
    """Add a `Bearer Token`_ to the request URI.
    Not recommended, use only if client can't use authorization header or body.

    http://www.example.com/path?access_token=h480djs93hd8

    .. _`Bearer Token`: http://tools.ietf.org/html/rfc6750
    """
    return add_params_to_uri(uri, [(('access_token', token))])


def prepare_bearer_headers(token, headers=None):
    """Add a `Bearer Token`_ to the request URI.
    Recommended method of passing bearer tokens.

    Authorization: Bearer h480djs93hd8

    .. _`Bearer Token`: http://tools.ietf.org/html/rfc6750
    """
    headers = headers or {}
    headers['Authorization'] = 'Bearer %s' % token
    return headers


def prepare_bearer_body(token, body=''):
    """Add a `Bearer Token`_ to the request body.

    access_token=h480djs93hd8

    .. _`Bearer Token`: http://tools.ietf.org/html/rfc6750
    """
    return add_params_to_qs(body, [(('access_token', token))])


def random_token_generator(request, refresh_token=False):
    return common.generate_token()


def signed_token_generator(private_pem, **kwargs):
    def signed_token_generator(request):
        request.claims = kwargs
        return common.generate_signed_token(private_pem, request)

    return signed_token_generator


class TokenBase(object):

    def __call__(self, request, refresh_token=False):
        raise NotImplementedError('Subclasses must implement this method.')

    def validate_request(self, request):
        raise NotImplementedError('Subclasses must implement this method.')

    def estimate_type(self, request):
        raise NotImplementedError('Subclasses must implement this method.')


class BearerToken(TokenBase):

    def __init__(self, request_validator=None, token_generator=None,
                 expires_in=None, refresh_token_generator=None):
        self.request_validator = request_validator
        self.token_generator = token_generator or random_token_generator
        self.refresh_token_generator = (
            refresh_token_generator or self.token_generator
        )
        self.expires_in = expires_in or 3600

    def create_token(self, request, refresh_token=False):
        """Create a BearerToken, by default without refresh token."""

        if callable(self.expires_in):
            expires_in = self.expires_in(request)
        else:
            expires_in = self.expires_in

        request.expires_in = expires_in

        token = {
            'access_token': self.token_generator(request),
            'expires_in': expires_in,
            'token_type': 'Bearer',
        }

        if request.scopes is not None:
            token['scope'] = ' '.join(request.scopes)

        if request.state is not None:
            token['state'] = request.state

        if refresh_token:
            if (request.refresh_token and
                    not self.request_validator.rotate_refresh_token(request)):
                token['refresh_token'] = request.refresh_token
            else:
                token['refresh_token'] = self.refresh_token_generator(request)

        token.update(request.extra_credentials or {})

        self.request_validator.save_bearer_token(token, request)
        return token

    def validate_request(self, request):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers.get('Authorization')[7:]
        else:
            token = request.access_token
        return self.request_validator.validate_bearer_token(
            token, request.scopes, request)

    def estimate_type(self, request):
        if request.headers.get('Authorization', '').startswith('Bearer'):
            return 9
        elif request.access_token is not None:
            return 5
        else:
            return 0
