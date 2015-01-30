# -*- coding: utf-8 -*-
"""
oauthlib.oauth2.rfc6749
~~~~~~~~~~~~~~~~~~~~~~~

This module is an implementation of various logic needed
for consuming and providing OAuth 2.0 RFC6749.
"""
from __future__ import absolute_import, unicode_literals

from .base import Client
from ..parameters import prepare_token_request
from ..parameters import parse_token_response


class BackendApplicationClient(Client):
    """A public client utilizing the client credentials grant workflow.

    The client can request an access token using only its client
    credentials (or other supported means of authentication) when the
    client is requesting access to the protected resources under its
    control, or those of another resource owner which has been previously
    arranged with the authorization server (the method of which is beyond
    the scope of this specification).

    The client credentials grant type MUST only be used by confidential
    clients.

    Since the client authentication is used as the authorization grant,
    no additional authorization request is needed.
    """

    def prepare_request_body(self, body='', scope=None, **kwargs):
        """Add the client credentials to the request body.

        The client makes a request to the token endpoint by adding the
        following parameters using the "application/x-www-form-urlencoded"
        format per `Appendix B`_ in the HTTP request entity-body:

        :param scope:   The scope of the access request as described by
                        `Section 3.3`_.
        :param kwargs:  Extra credentials to include in the token request.

        The client MUST authenticate with the authorization server as
        described in `Section 3.2.1`_.

        The prepared body will include all provided credentials as well as
        the ``grant_type`` parameter set to ``client_credentials``::

            >>> from oauthlib.oauth2 import BackendApplicationClient
            >>> client = BackendApplicationClient('your_id')
            >>> client.prepare_request_body(scope=['hello', 'world'])
            'grant_type=client_credentials&scope=hello+world'

        .. _`Appendix B`: http://tools.ietf.org/html/rfc6749#appendix-B
        .. _`Section 3.3`: http://tools.ietf.org/html/rfc6749#section-3.3
        .. _`Section 3.2.1`: http://tools.ietf.org/html/rfc6749#section-3.2.1
        """
        return prepare_token_request('client_credentials', body=body,
                                     scope=scope, **kwargs)

    def parse_request_body_response(self, body, scope=None):
        """Parse the JSON response body.

        If the access token request is valid and authorized, the
        authorization server issues an access token as described in
        `Section 5.1`_.  A refresh token SHOULD NOT be included.  If the request
        failed client authentication or is invalid, the authorization server
        returns an error response as described in `Section 5.2`_.

        :param body: The response body from the token request.
        :param scope: Scopes originally requested.
        :return: Dictionary of token parameters.
        :raises: Warning if scope has changed. OAuth2Error if response is invalid.

        These response are json encoded and could easily be parsed without
        the assistance of OAuthLib. However, there are a few subtle issues
        to be aware of regarding the response which are helpfully addressed
        through the raising of various errors.

        A successful response should always contain

        **access_token**
                The access token issued by the authorization server. Often
                a random string.

        **token_type**
            The type of the token issued as described in `Section 7.1`_.
            Commonly ``Bearer``.

        While it is not mandated it is recommended that the provider include

        **expires_in**
            The lifetime in seconds of the access token.  For
            example, the value "3600" denotes that the access token will
            expire in one hour from the time the response was generated.
            If omitted, the authorization server SHOULD provide the
            expiration time via other means or document the default value.

        **scope**
            Providers may supply this in all responses but are required to only
            if it has changed since the authorization request.

        A normal response might look like::

            >>> json.loads(response_body)
            {
                    'access_token': 'sdfkjh345',
                    'token_type': 'Bearer',
                    'expires_in': '3600',
                    'refresh_token': 'x345dgasd',
                    'scope': 'hello world',
            }
            >>> from oauthlib.oauth2 import BackendApplicationClient
            >>> client = BackendApplicationClient('your_id')
            >>> client.parse_request_body_response(response_body)
            {
                    'access_token': 'sdfkjh345',
                    'token_type': 'Bearer',
                    'expires_in': '3600',
                    'refresh_token': 'x345dgasd',
                    'scope': ['hello', 'world'],    # note the list
            }

        If there was a scope change you will be notified with a warning::

            >>> client.parse_request_body_response(response_body, scope=['images'])
            Traceback (most recent call last):
                File "<stdin>", line 1, in <module>
                File "oauthlib/oauth2/rfc6749/__init__.py", line 421, in parse_request_body_response
                    .. _`Section 5.2`: http://tools.ietf.org/html/rfc6749#section-5.2
                File "oauthlib/oauth2/rfc6749/parameters.py", line 263, in parse_token_response
                    validate_token_parameters(params, scope)
                File "oauthlib/oauth2/rfc6749/parameters.py", line 285, in validate_token_parameters
                    raise Warning("Scope has changed to %s." % new_scope)
            Warning: Scope has changed to [u'hello', u'world'].

        If there was an error on the providers side you will be notified with
        an error. For example, if there was no ``token_type`` provided::

            >>> client.parse_request_body_response(response_body)
            Traceback (most recent call last):
                File "<stdin>", line 1, in <module>
                File "oauthlib/oauth2/rfc6749/__init__.py", line 421, in parse_request_body_response
                    File "oauthlib/oauth2/rfc6749/__init__.py", line 421, in parse_request_body_response
                File "oauthlib/oauth2/rfc6749/parameters.py", line 263, in parse_token_response
                    validate_token_parameters(params, scope)
                File "oauthlib/oauth2/rfc6749/parameters.py", line 276, in validate_token_parameters
                    raise MissingTokenTypeError()
            oauthlib.oauth2.rfc6749.errors.MissingTokenTypeError

        .. _`Section 5.1`: http://tools.ietf.org/html/rfc6749#section-5.1
        .. _`Section 5.2`: http://tools.ietf.org/html/rfc6749#section-5.2
        .. _`Section 7.1`: http://tools.ietf.org/html/rfc6749#section-7.1
        """
        self.token = parse_token_response(body, scope=scope)
        self._populate_attributes(self.token)
        return self.token
