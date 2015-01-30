# -*- coding: utf-8 -*-
"""
oauthlib.oauth2.rfc6749
~~~~~~~~~~~~~~~~~~~~~~~

This module is an implementation of various logic needed
for consuming and providing OAuth 2.0 RFC6749.
"""
from __future__ import absolute_import, unicode_literals

from .base import Client
from ..parameters import prepare_grant_uri, prepare_token_request
from ..parameters import parse_authorization_code_response
from ..parameters import parse_token_response


class WebApplicationClient(Client):
    """A client utilizing the authorization code grant workflow.

    A web application is a confidential client running on a web
    server.  Resource owners access the client via an HTML user
    interface rendered in a user-agent on the device used by the
    resource owner.  The client credentials as well as any access
    token issued to the client are stored on the web server and are
    not exposed to or accessible by the resource owner.

    The authorization code grant type is used to obtain both access
    tokens and refresh tokens and is optimized for confidential clients.
    As a redirection-based flow, the client must be capable of
    interacting with the resource owner's user-agent (typically a web
    browser) and capable of receiving incoming requests (via redirection)
    from the authorization server.
    """

    def __init__(self, client_id, code=None, **kwargs):
        super(WebApplicationClient, self).__init__(client_id, **kwargs)
        self.code = code

    def prepare_request_uri(self, uri, redirect_uri=None, scope=None,
            state=None, **kwargs):
        """Prepare the authorization code request URI

        The client constructs the request URI by adding the following
        parameters to the query component of the authorization endpoint URI
        using the "application/x-www-form-urlencoded" format, per `Appendix B`_:

        :param redirect_uri:  OPTIONAL. The redirect URI must be an absolute URI
                              and it should have been registerd with the OAuth
                              provider prior to use. As described in `Section 3.1.2`_.

        :param scope:  OPTIONAL. The scope of the access request as described by
                       Section 3.3`_. These may be any string but are commonly
                       URIs or various categories such as ``videos`` or ``documents``.

        :param state:   RECOMMENDED.  An opaque value used by the client to maintain
                        state between the request and callback.  The authorization
                        server includes this value when redirecting the user-agent back
                        to the client.  The parameter SHOULD be used for preventing
                        cross-site request forgery as described in `Section 10.12`_.

        :param kwargs:  Extra arguments to include in the request URI.

        In addition to supplied parameters, OAuthLib will append the ``client_id``
        that was provided in the constructor as well as the mandatory ``response_type``
        argument, set to ``code``::

            >>> from oauthlib.oauth2 import WebApplicationClient
            >>> client = WebApplicationClient('your_id')
            >>> client.prepare_request_uri('https://example.com')
            'https://example.com?client_id=your_id&response_type=code'
            >>> client.prepare_request_uri('https://example.com', redirect_uri='https://a.b/callback')
            'https://example.com?client_id=your_id&response_type=code&redirect_uri=https%3A%2F%2Fa.b%2Fcallback'
            >>> client.prepare_request_uri('https://example.com', scope=['profile', 'pictures'])
            'https://example.com?client_id=your_id&response_type=code&scope=profile+pictures'
            >>> client.prepare_request_uri('https://example.com', foo='bar')
            'https://example.com?client_id=your_id&response_type=code&foo=bar'

        .. _`Appendix B`: http://tools.ietf.org/html/rfc6749#appendix-B
        .. _`Section 2.2`: http://tools.ietf.org/html/rfc6749#section-2.2
        .. _`Section 3.1.2`: http://tools.ietf.org/html/rfc6749#section-3.1.2
        .. _`Section 3.3`: http://tools.ietf.org/html/rfc6749#section-3.3
        .. _`Section 10.12`: http://tools.ietf.org/html/rfc6749#section-10.12
        """
        return prepare_grant_uri(uri, self.client_id, 'code',
                redirect_uri=redirect_uri, scope=scope, state=state, **kwargs)

    def prepare_request_body(self, client_id=None, code=None, body='',
            redirect_uri=None, **kwargs):
        """Prepare the access token request body.

        The client makes a request to the token endpoint by adding the
        following parameters using the "application/x-www-form-urlencoded"
        format in the HTTP request entity-body:

        :param client_id:   REQUIRED, if the client is not authenticating with the
                            authorization server as described in `Section 3.2.1`_.

        :param code:    REQUIRED. The authorization code received from the
                        authorization server.

        :param redirect_uri:    REQUIRED, if the "redirect_uri" parameter was included in the
                                authorization request as described in `Section 4.1.1`_, and their
                                values MUST be identical.

        :param kwargs: Extra parameters to include in the token request.

        In addition OAuthLib will add the ``grant_type`` parameter set to
        ``authorization_code``.

        If the client type is confidential or the client was issued client
        credentials (or assigned other authentication requirements), the
        client MUST authenticate with the authorization server as described
        in `Section 3.2.1`_::

            >>> from oauthlib.oauth2 import WebApplicationClient
            >>> client = WebApplicationClient('your_id')
            >>> client.prepare_request_body(code='sh35ksdf09sf')
            'grant_type=authorization_code&code=sh35ksdf09sf'
            >>> client.prepare_request_body(code='sh35ksdf09sf', foo='bar')
            'grant_type=authorization_code&code=sh35ksdf09sf&foo=bar'

        .. _`Section 4.1.1`: http://tools.ietf.org/html/rfc6749#section-4.1.1
        .. _`Section 3.2.1`: http://tools.ietf.org/html/rfc6749#section-3.2.1
        """
        code = code or self.code
        return prepare_token_request('authorization_code', code=code, body=body,
                client_id=self.client_id, redirect_uri=redirect_uri, **kwargs)

    def parse_request_uri_response(self, uri, state=None):
        """Parse the URI query for code and state.

        If the resource owner grants the access request, the authorization
        server issues an authorization code and delivers it to the client by
        adding the following parameters to the query component of the
        redirection URI using the "application/x-www-form-urlencoded" format:

        :param uri: The callback URI that resulted from the user being redirected
                    back from the provider to you, the client.
        :param state: The state provided in the authorization request.

        **code**
            The authorization code generated by the authorization server.
            The authorization code MUST expire shortly after it is issued
            to mitigate the risk of leaks. A maximum authorization code
            lifetime of 10 minutes is RECOMMENDED. The client MUST NOT
            use the authorization code more than once. If an authorization
            code is used more than once, the authorization server MUST deny
            the request and SHOULD revoke (when possible) all tokens
            previously issued based on that authorization code.
            The authorization code is bound to the client identifier and
            redirection URI.

        **state**
                If the "state" parameter was present in the authorization request.

        This method is mainly intended to enforce strict state checking with
        the added benefit of easily extracting parameters from the URI::

            >>> from oauthlib.oauth2 import WebApplicationClient
            >>> client = WebApplicationClient('your_id')
            >>> uri = 'https://example.com/callback?code=sdfkjh345&state=sfetw45'
            >>> client.parse_request_uri_response(uri, state='sfetw45')
            {'state': 'sfetw45', 'code': 'sdfkjh345'}
            >>> client.parse_request_uri_response(uri, state='other')
            Traceback (most recent call last):
                File "<stdin>", line 1, in <module>
                File "oauthlib/oauth2/rfc6749/__init__.py", line 357, in parse_request_uri_response
                    back from the provider to you, the client.
                File "oauthlib/oauth2/rfc6749/parameters.py", line 153, in parse_authorization_code_response
                    raise MismatchingStateError()
            oauthlib.oauth2.rfc6749.errors.MismatchingStateError
        """
        response = parse_authorization_code_response(uri, state=state)
        self._populate_attributes(response)
        return response

    def parse_request_body_response(self, body, scope=None):
        """Parse the JSON response body.

        If the access token request is valid and authorized, the
        authorization server issues an access token and optional refresh
        token as described in `Section 5.1`_.  If the request client
        authentication failed or is invalid, the authorization server returns
        an error response as described in `Section 5.2`_.

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
            >>> from oauthlib.oauth2 import WebApplicationClient
            >>> client = WebApplicationClient('your_id')
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
