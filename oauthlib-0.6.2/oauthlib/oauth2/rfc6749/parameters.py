# -*- coding: utf-8 -*-
"""
oauthlib.oauth2.rfc6749.parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains methods related to `Section 4`_ of the OAuth 2 RFC.

.. _`Section 4`: http://tools.ietf.org/html/rfc6749#section-4
"""
from __future__ import absolute_import, unicode_literals

import json
import time
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse
from oauthlib.common import add_params_to_uri, add_params_to_qs, unicode_type
from .errors import raise_from_error, MissingTokenError, MissingTokenTypeError
from .errors import MismatchingStateError, MissingCodeError
from .errors import InsecureTransportError
from .utils import list_to_scope, scope_to_list, is_secure_transport


def prepare_grant_uri(uri, client_id, response_type, redirect_uri=None,
            scope=None, state=None, **kwargs):
    """Prepare the authorization grant request URI.

    The client constructs the request URI by adding the following
    parameters to the query component of the authorization endpoint URI
    using the ``application/x-www-form-urlencoded`` format as defined by
    [`W3C.REC-html401-19991224`_]:

    :param response_type: To indicate which OAuth 2 grant/flow is required,
                          "code" and "token".
    :param client_id: The client identifier as described in `Section 2.2`_.
    :param redirect_uri: The client provided URI to redirect back to after
                         authorization as described in `Section 3.1.2`_.
    :param scope: The scope of the access request as described by
                  `Section 3.3`_.

    :param state: An opaque value used by the client to maintain
                  state between the request and callback.  The authorization
                  server includes this value when redirecting the user-agent
                  back to the client.  The parameter SHOULD be used for
                  preventing cross-site request forgery as described in
                  `Section 10.12`_.
    :param kwargs: Extra arguments to embed in the grant/authorization URL.

    An example of an authorization code grant authorization URL:

    .. code-block:: http

        GET /authorize?response_type=code&client_id=s6BhdRkqt3&state=xyz
            &redirect_uri=https%3A%2F%2Fclient%2Eexample%2Ecom%2Fcb HTTP/1.1
        Host: server.example.com

    .. _`W3C.REC-html401-19991224`: http://tools.ietf.org/html/rfc6749#ref-W3C.REC-html401-19991224
    .. _`Section 2.2`: http://tools.ietf.org/html/rfc6749#section-2.2
    .. _`Section 3.1.2`: http://tools.ietf.org/html/rfc6749#section-3.1.2
    .. _`Section 3.3`: http://tools.ietf.org/html/rfc6749#section-3.3
    .. _`section 10.12`: http://tools.ietf.org/html/rfc6749#section-10.12
    """
    if not is_secure_transport(uri):
        raise InsecureTransportError()

    params = [(('response_type', response_type)),
              (('client_id', client_id))]

    if redirect_uri:
        params.append(('redirect_uri', redirect_uri))
    if scope:
        params.append(('scope', list_to_scope(scope)))
    if state:
        params.append(('state', state))

    for k in kwargs:
        if kwargs[k]:
            params.append((unicode_type(k), kwargs[k]))

    return add_params_to_uri(uri, params)


def prepare_token_request(grant_type, body='', **kwargs):
    """Prepare the access token request.

    The client makes a request to the token endpoint by adding the
    following parameters using the ``application/x-www-form-urlencoded``
    format in the HTTP request entity-body:

    :param grant_type: To indicate grant type being used, i.e. "password",
            "authorization_code" or "client_credentials".
    :param body: Existing request body to embed parameters in.
    :param code: If using authorization code grant, pass the previously
                 obtained authorization code as the ``code`` argument.
    :param redirect_uri: If the "redirect_uri" parameter was included in the
                         authorization request as described in
                         `Section 4.1.1`_, and their values MUST be identical.
    :param kwargs: Extra arguments to embed in the request body.

    An example of an authorization code token request body:

    .. code-block:: http

        grant_type=authorization_code&code=SplxlOBeZQQYbYS6WxSbIA
        &redirect_uri=https%3A%2F%2Fclient%2Eexample%2Ecom%2Fcb

    .. _`Section 4.1.1`: http://tools.ietf.org/html/rfc6749#section-4.1.1
    """
    params = [('grant_type', grant_type)]

    if 'scope' in kwargs:
        kwargs['scope'] = list_to_scope(kwargs['scope'])

    for k in kwargs:
        if kwargs[k]:
            params.append((unicode_type(k), kwargs[k]))

    return add_params_to_qs(body, params)


def parse_authorization_code_response(uri, state=None):
    """Parse authorization grant response URI into a dict.

    If the resource owner grants the access request, the authorization
    server issues an authorization code and delivers it to the client by
    adding the following parameters to the query component of the
    redirection URI using the ``application/x-www-form-urlencoded`` format:

    **code**
            REQUIRED.  The authorization code generated by the
            authorization server.  The authorization code MUST expire
            shortly after it is issued to mitigate the risk of leaks.  A
            maximum authorization code lifetime of 10 minutes is
            RECOMMENDED.  The client MUST NOT use the authorization code
            more than once.  If an authorization code is used more than
            once, the authorization server MUST deny the request and SHOULD
            revoke (when possible) all tokens previously issued based on
            that authorization code.  The authorization code is bound to
            the client identifier and redirection URI.

    **state**
            REQUIRED if the "state" parameter was present in the client
            authorization request.  The exact value received from the
            client.

    :param uri: The full redirect URL back to the client.
    :param state: The state parameter from the authorization request.

    For example, the authorization server redirects the user-agent by
    sending the following HTTP response:

    .. code-block:: http

        HTTP/1.1 302 Found
        Location: https://client.example.com/cb?code=SplxlOBeZQQYbYS6WxSbIA
                &state=xyz

    """
    if not is_secure_transport(uri):
        raise InsecureTransportError()

    query = urlparse.urlparse(uri).query
    params = dict(urlparse.parse_qsl(query))

    if not 'code' in params:
        raise MissingCodeError("Missing code parameter in response.")

    if state and params.get('state', None) != state:
        raise MismatchingStateError()

    return params


def parse_implicit_response(uri, state=None, scope=None):
    """Parse the implicit token response URI into a dict.

    If the resource owner grants the access request, the authorization
    server issues an access token and delivers it to the client by adding
    the following parameters to the fragment component of the redirection
    URI using the ``application/x-www-form-urlencoded`` format:

    **access_token**
            REQUIRED.  The access token issued by the authorization server.

    **token_type**
            REQUIRED.  The type of the token issued as described in
            Section 7.1.  Value is case insensitive.

    **expires_in**
            RECOMMENDED.  The lifetime in seconds of the access token.  For
            example, the value "3600" denotes that the access token will
            expire in one hour from the time the response was generated.
            If omitted, the authorization server SHOULD provide the
            expiration time via other means or document the default value.

    **scope**
            OPTIONAL, if identical to the scope requested by the client,
            otherwise REQUIRED.  The scope of the access token as described
            by Section 3.3.

    **state**
            REQUIRED if the "state" parameter was present in the client
            authorization request.  The exact value received from the
            client.

    Similar to the authorization code response, but with a full token provided
    in the URL fragment:

    .. code-block:: http

        HTTP/1.1 302 Found
        Location: http://example.com/cb#access_token=2YotnFZFEjr1zCsicMWpAA
                &state=xyz&token_type=example&expires_in=3600
    """
    if not is_secure_transport(uri):
        raise InsecureTransportError()

    fragment = urlparse.urlparse(uri).fragment
    params = dict(urlparse.parse_qsl(fragment, keep_blank_values=True))

    if 'scope' in params:
        params['scope'] = scope_to_list(params['scope'])

    if 'expires_in' in params:
        params['expires_at'] = time.time() + int(params['expires_in'])

    if state and params.get('state', None) != state:
        raise ValueError("Mismatching or missing state in params.")

    validate_token_parameters(params, scope)
    return params


def parse_token_response(body, scope=None):
    """Parse the JSON token response body into a dict.

    The authorization server issues an access token and optional refresh
    token, and constructs the response by adding the following parameters
    to the entity body of the HTTP response with a 200 (OK) status code:

    access_token
            REQUIRED.  The access token issued by the authorization server.
    token_type
            REQUIRED.  The type of the token issued as described in
            `Section 7.1`_.  Value is case insensitive.
    expires_in
            RECOMMENDED.  The lifetime in seconds of the access token.  For
            example, the value "3600" denotes that the access token will
            expire in one hour from the time the response was generated.
            If omitted, the authorization server SHOULD provide the
            expiration time via other means or document the default value.
    refresh_token
            OPTIONAL.  The refresh token which can be used to obtain new
            access tokens using the same authorization grant as described
            in `Section 6`_.
    scope
            OPTIONAL, if identical to the scope requested by the client,
            otherwise REQUIRED.  The scope of the access token as described
            by `Section 3.3`_.

    The parameters are included in the entity body of the HTTP response
    using the "application/json" media type as defined by [`RFC4627`_].  The
    parameters are serialized into a JSON structure by adding each
    parameter at the highest structure level.  Parameter names and string
    values are included as JSON strings.  Numerical values are included
    as JSON numbers.  The order of parameters does not matter and can
    vary.

    :param body: The full json encoded response body.
    :param scope: The scope requested during authorization.

    For example:

    .. code-block:: http

        HTTP/1.1 200 OK
        Content-Type: application/json
        Cache-Control: no-store
        Pragma: no-cache

        {
            "access_token":"2YotnFZFEjr1zCsicMWpAA",
            "token_type":"example",
            "expires_in":3600,
            "refresh_token":"tGzv3JOkF0XG5Qx2TlKWIA",
            "example_parameter":"example_value"
        }

    .. _`Section 7.1`: http://tools.ietf.org/html/rfc6749#section-7.1
    .. _`Section 6`: http://tools.ietf.org/html/rfc6749#section-6
    .. _`Section 3.3`: http://tools.ietf.org/html/rfc6749#section-3.3
    .. _`RFC4627`: http://tools.ietf.org/html/rfc4627
    """
    params = json.loads(body)

    if 'scope' in params:
        params['scope'] = scope_to_list(params['scope'])

    if 'expires_in' in params:
        params['expires_at'] = time.time() + int(params['expires_in'])

    validate_token_parameters(params, scope)
    return params


def validate_token_parameters(params, scope=None):
    """Ensures token precence, token type, expiration and scope in params."""
    if 'error' in params:
        raise_from_error(params.get('error'), params)

    if not 'access_token' in params:
        raise MissingTokenError(description="Missing access token parameter.")

    if not 'token_type' in params:
        raise MissingTokenTypeError()

    # If the issued access token scope is different from the one requested by
    # the client, the authorization server MUST include the "scope" response
    # parameter to inform the client of the actual scope granted.
    # http://tools.ietf.org/html/rfc6749#section-3.3
    new_scope = params.get('scope', None)
    scope = scope_to_list(scope)
    if scope and new_scope and set(scope) != set(new_scope):
        raise Warning("Scope has changed to %s." % new_scope)
