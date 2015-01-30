# -*- coding: utf-8 -*-
"""
oauthlib.oauth2.rfc6749
~~~~~~~~~~~~~~~~~~~~~~~

This module is an implementation of various logic needed
for consuming OAuth 2.0 RFC6749.
"""
from __future__ import absolute_import, unicode_literals

import time

from oauthlib.oauth2.rfc6749 import tokens
from oauthlib.oauth2.rfc6749.parameters import prepare_token_request
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError
from oauthlib.oauth2.rfc6749.errors import InsecureTransportError
from oauthlib.oauth2.rfc6749.utils import is_secure_transport


AUTH_HEADER = 'auth_header'
URI_QUERY = 'query'
BODY = 'body'


class Client(object):
    """Base OAuth2 client responsible for access tokens.

    While this class can be used to simply append tokens onto requests
    it is often more useful to use a client targeted at a specific workflow.
    """

    def __init__(self, client_id,
            default_token_placement=AUTH_HEADER,
            token_type='Bearer',
            access_token=None,
            refresh_token=None,
            mac_key=None,
            mac_algorithm=None,
            token=None,
            **kwargs):
        """Initialize a client with commonly used attributes."""

        self.client_id = client_id
        self.default_token_placement = default_token_placement
        self.token_type = token_type
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.mac_key = mac_key
        self.mac_algorithm = mac_algorithm
        self.token = token or {}
        self._expires_at = None
        self._populate_attributes(self.token)

    @property
    def token_types(self):
        """Supported token types and their respective methods

        Additional tokens can be supported by extending this dictionary.

        The Bearer token spec is stable and safe to use.

        The MAC token spec is not yet stable and support for MAC tokens
        is experimental and currently matching version 00 of the spec.
        """
        return {
            'Bearer': self._add_bearer_token,
            'MAC': self._add_mac_token
        }

    def add_token(self, uri, http_method='GET', body=None, headers=None,
            token_placement=None, **kwargs):
        """Add token to the request uri, body or authorization header.

        The access token type provides the client with the information
        required to successfully utilize the access token to make a protected
        resource request (along with type-specific attributes).  The client
        MUST NOT use an access token if it does not understand the token
        type.

        For example, the "bearer" token type defined in
        [`I-D.ietf-oauth-v2-bearer`_] is utilized by simply including the access
        token string in the request:

        .. code-block:: http

            GET /resource/1 HTTP/1.1
            Host: example.com
            Authorization: Bearer mF_9.B5f-4.1JqM

        while the "mac" token type defined in [`I-D.ietf-oauth-v2-http-mac`_] is
        utilized by issuing a MAC key together with the access token which is
        used to sign certain components of the HTTP requests:

        .. code-block:: http

            GET /resource/1 HTTP/1.1
            Host: example.com
            Authorization: MAC id="h480djs93hd8",
                                nonce="274312:dj83hs9s",
                                mac="kDZvddkndxvhGRXZhvuDjEWhGeE="

        .. _`I-D.ietf-oauth-v2-bearer`: http://tools.ietf.org/html/rfc6749#section-12.2
        .. _`I-D.ietf-oauth-v2-http-mac`: http://tools.ietf.org/html/rfc6749#section-12.2
        """
        if not is_secure_transport(uri):
            raise InsecureTransportError()

        token_placement = token_placement or self.default_token_placement

        case_insensitive_token_types = dict((k.lower(), v) for k, v in self.token_types.items())
        if not self.token_type.lower() in case_insensitive_token_types:
            raise ValueError("Unsupported token type: %s" % self.token_type)

        if not self.access_token:
            raise ValueError("Missing access token.")

        if self._expires_at and self._expires_at < time.time():
            raise TokenExpiredError()

        return case_insensitive_token_types[self.token_type.lower()](uri, http_method, body,
                    headers, token_placement, **kwargs)

    def prepare_refresh_body(self, body='', refresh_token=None, scope=None, **kwargs):
        """Prepare an access token request, using a refresh token.

        If the authorization server issued a refresh token to the client, the
        client makes a refresh request to the token endpoint by adding the
        following parameters using the "application/x-www-form-urlencoded"
        format in the HTTP request entity-body:

        grant_type
                REQUIRED.  Value MUST be set to "refresh_token".
        refresh_token
                REQUIRED.  The refresh token issued to the client.
        scope
                OPTIONAL.  The scope of the access request as described by
                Section 3.3.  The requested scope MUST NOT include any scope
                not originally granted by the resource owner, and if omitted is
                treated as equal to the scope originally granted by the
                resource owner.
        """
        refresh_token = refresh_token or self.refresh_token
        return prepare_token_request('refresh_token', body=body, scope=scope,
                refresh_token=refresh_token, **kwargs)

    def _add_bearer_token(self, uri, http_method='GET', body=None,
            headers=None, token_placement=None):
        """Add a bearer token to the request uri, body or authorization header."""
        if token_placement == AUTH_HEADER:
            headers = tokens.prepare_bearer_headers(self.access_token, headers)

        elif token_placement == URI_QUERY:
            uri = tokens.prepare_bearer_uri(self.access_token, uri)

        elif token_placement == BODY:
            body = tokens.prepare_bearer_body(self.access_token, body)

        else:
            raise ValueError("Invalid token placement.")
        return uri, headers, body

    def _add_mac_token(self, uri, http_method='GET', body=None,
            headers=None, token_placement=AUTH_HEADER, ext=None, **kwargs):
        """Add a MAC token to the request authorization header.

        Warning: MAC token support is experimental as the spec is not yet stable.
        """
        headers = tokens.prepare_mac_header(self.access_token, uri,
                self.mac_key, http_method, headers=headers, body=body, ext=ext,
                hash_algorithm=self.mac_algorithm, **kwargs)
        return uri, headers, body

    def _populate_attributes(self, response):
        """Add commonly used values such as access_token to self."""

        if 'access_token' in response:
            self.access_token = response.get('access_token')

        if 'refresh_token' in response:
            self.refresh_token = response.get('refresh_token')

        if 'token_type' in response:
            self.token_type = response.get('token_type')

        if 'expires_in' in response:
            self.expires_in = response.get('expires_in')
            self._expires_at = time.time() + int(self.expires_in)

        if 'expires_at' in response:
            self._expires_at = int(response.get('expires_at'))

        if 'code' in response:
            self.code = response.get('code')

        if 'mac_key' in response:
            self.mac_key = response.get('mac_key')

        if 'mac_algorithm' in response:
            self.mac_algorithm = response.get('mac_algorithm')

    def prepare_request_uri(self, *args, **kwargs):
        """Abstract method used to create request URIs."""
        raise NotImplementedError("Must be implemented by inheriting classes.")

    def prepare_request_body(self, *args, **kwargs):
        """Abstract method used to create request bodies."""
        raise NotImplementedError("Must be implemented by inheriting classes.")

    def parse_request_uri_response(self, *args, **kwargs):
        """Abstract method used to parse redirection responses."""

    def parse_request_body_response(self, *args, **kwargs):
        """Abstract method used to parse JSON responses."""
