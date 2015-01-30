# -*- coding: utf-8 -*-
"""
oauthlib.oauth2.rfc6749.grant_types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from __future__ import unicode_literals, absolute_import
import json

from oauthlib import common
from oauthlib.common import log
from oauthlib.uri_validate import is_absolute_uri

from .base import GrantTypeBase
from .. import errors
from ..request_validator import RequestValidator


class AuthorizationCodeGrant(GrantTypeBase):
    """`Authorization Code Grant`_

    The authorization code grant type is used to obtain both access
    tokens and refresh tokens and is optimized for confidential clients.
    Since this is a redirection-based flow, the client must be capable of
    interacting with the resource owner's user-agent (typically a web
    browser) and capable of receiving incoming requests (via redirection)
    from the authorization server::

        +----------+
        | Resource |
        |   Owner  |
        |          |
        +----------+
             ^
             |
            (B)
        +----|-----+          Client Identifier      +---------------+
        |         -+----(A)-- & Redirection URI ---->|               |
        |  User-   |                                 | Authorization |
        |  Agent  -+----(B)-- User authenticates --->|     Server    |
        |          |                                 |               |
        |         -+----(C)-- Authorization Code ---<|               |
        +-|----|---+                                 +---------------+
          |    |                                         ^      v
         (A)  (C)                                        |      |
          |    |                                         |      |
          ^    v                                         |      |
        +---------+                                      |      |
        |         |>---(D)-- Authorization Code ---------'      |
        |  Client |          & Redirection URI                  |
        |         |                                             |
        |         |<---(E)----- Access Token -------------------'
        +---------+       (w/ Optional Refresh Token)

    Note: The lines illustrating steps (A), (B), and (C) are broken into
    two parts as they pass through the user-agent.

    Figure 3: Authorization Code Flow

    The flow illustrated in Figure 3 includes the following steps:

    (A)  The client initiates the flow by directing the resource owner's
         user-agent to the authorization endpoint.  The client includes
         its client identifier, requested scope, local state, and a
         redirection URI to which the authorization server will send the
         user-agent back once access is granted (or denied).

    (B)  The authorization server authenticates the resource owner (via
         the user-agent) and establishes whether the resource owner
         grants or denies the client's access request.

    (C)  Assuming the resource owner grants access, the authorization
         server redirects the user-agent back to the client using the
         redirection URI provided earlier (in the request or during
         client registration).  The redirection URI includes an
         authorization code and any local state provided by the client
         earlier.

    (D)  The client requests an access token from the authorization
         server's token endpoint by including the authorization code
         received in the previous step.  When making the request, the
         client authenticates with the authorization server.  The client
         includes the redirection URI used to obtain the authorization
         code for verification.

    (E)  The authorization server authenticates the client, validates the
         authorization code, and ensures that the redirection URI
         received matches the URI used to redirect the client in
         step (C).  If valid, the authorization server responds back with
         an access token and, optionally, a refresh token.

    .. _`Authorization Code Grant`: http://tools.ietf.org/html/rfc6749#section-4.1
    """
    def __init__(self, request_validator=None):
        self.request_validator = request_validator or RequestValidator()

    def create_authorization_code(self, request):
        """Generates an authorization grant represented as a dictionary."""
        grant = {'code': common.generate_token()}
        if hasattr(request, 'state') and request.state:
            grant['state'] = request.state
        log.debug('Created authorization code grant %r for request %r.',
                  grant, request)
        return grant

    def create_authorization_response(self, request, token_handler):
        """
        The client constructs the request URI by adding the following
        parameters to the query component of the authorization endpoint URI
        using the "application/x-www-form-urlencoded" format, per `Appendix B`_:

        response_type
                REQUIRED.  Value MUST be set to "code".
        client_id
                REQUIRED.  The client identifier as described in `Section 2.2`_.
        redirect_uri
                OPTIONAL.  As described in `Section 3.1.2`_.
        scope
                OPTIONAL.  The scope of the access request as described by
                `Section 3.3`_.
        state
                RECOMMENDED.  An opaque value used by the client to maintain
                state between the request and callback.  The authorization
                server includes this value when redirecting the user-agent back
                to the client.  The parameter SHOULD be used for preventing
                cross-site request forgery as described in `Section 10.12`_.

        The client directs the resource owner to the constructed URI using an
        HTTP redirection response, or by other means available to it via the
        user-agent.

        :param request: oauthlib.commong.Request
        :param token_handler: A token handler instace, for example of type
                              oauthlib.oauth2.BearerToken.
        :returns: headers, body, status
        :raises: FatalClientError on invalid redirect URI or client id.
                 ValueError if scopes are not set on the request object.

        A few examples::

            >>> from your_validator import your_validator
            >>> request = Request('https://example.com/authorize?client_id=valid'
            ...                   '&redirect_uri=http%3A%2F%2Fclient.com%2F')
            >>> from oauthlib.common import Request
            >>> from oauthlib.oauth2 import AuthorizationCodeGrant, BearerToken
            >>> token = BearerToken(your_validator)
            >>> grant = AuthorizationCodeGrant(your_validator)
            >>> grant.create_authorization_response(request, token)
            Traceback (most recent call last):
                File "<stdin>", line 1, in <module>
                File "oauthlib/oauth2/rfc6749/grant_types.py", line 513, in create_authorization_response
                    raise ValueError('Scopes must be set on post auth.')
            ValueError: Scopes must be set on post auth.
            >>> request.scopes = ['authorized', 'in', 'some', 'form']
            >>> grant.create_authorization_response(request, token)
            (u'http://client.com/?error=invalid_request&error_description=Missing+response_type+parameter.', None, None, 400)
            >>> request = Request('https://example.com/authorize?client_id=valid'
            ...                   '&redirect_uri=http%3A%2F%2Fclient.com%2F'
            ...                   '&response_type=code')
            >>> request.scopes = ['authorized', 'in', 'some', 'form']
            >>> grant.create_authorization_response(request, token)
            (u'http://client.com/?code=u3F05aEObJuP2k7DordviIgW5wl52N', None, None, 200)
            >>> # If the client id or redirect uri fails validation
            >>> grant.create_authorization_response(request, token)
            Traceback (most recent call last):
                File "<stdin>", line 1, in <module>
                File "oauthlib/oauth2/rfc6749/grant_types.py", line 515, in create_authorization_response
                    >>> grant.create_authorization_response(request, token)
                File "oauthlib/oauth2/rfc6749/grant_types.py", line 591, in validate_authorization_request
            oauthlib.oauth2.rfc6749.errors.InvalidClientIdError

        .. _`Appendix B`: http://tools.ietf.org/html/rfc6749#appendix-B
        .. _`Section 2.2`: http://tools.ietf.org/html/rfc6749#section-2.2
        .. _`Section 3.1.2`: http://tools.ietf.org/html/rfc6749#section-3.1.2
        .. _`Section 3.3`: http://tools.ietf.org/html/rfc6749#section-3.3
        .. _`Section 10.12`: http://tools.ietf.org/html/rfc6749#section-10.12
        """
        try:
            # request.scopes is only mandated in post auth and both pre and
            # post auth use validate_authorization_request
            if not request.scopes:
                raise ValueError('Scopes must be set on post auth.')

            self.validate_authorization_request(request)
            log.debug('Pre resource owner authorization validation ok for %r.',
                      request)

        # If the request fails due to a missing, invalid, or mismatching
        # redirection URI, or if the client identifier is missing or invalid,
        # the authorization server SHOULD inform the resource owner of the
        # error and MUST NOT automatically redirect the user-agent to the
        # invalid redirection URI.
        except errors.FatalClientError as e:
            log.debug('Fatal client error during validation of %r. %r.',
                      request, e)
            raise

        # If the resource owner denies the access request or if the request
        # fails for reasons other than a missing or invalid redirection URI,
        # the authorization server informs the client by adding the following
        # parameters to the query component of the redirection URI using the
        # "application/x-www-form-urlencoded" format, per Appendix B:
        # http://tools.ietf.org/html/rfc6749#appendix-B
        except errors.OAuth2Error as e:
            log.debug('Client error during validation of %r. %r.', request, e)
            request.redirect_uri = request.redirect_uri or self.error_uri
            return {'Location': common.add_params_to_uri(request.redirect_uri, e.twotuples)}, None, 302

        grant = self.create_authorization_code(request)
        log.debug('Saving grant %r for %r.', grant, request)
        self.request_validator.save_authorization_code(request.client_id, grant, request)
        return {'Location': common.add_params_to_uri(request.redirect_uri, grant.items())}, None, 302

    def create_token_response(self, request, token_handler):
        """Validate the authorization code.

        The client MUST NOT use the authorization code more than once. If an
        authorization code is used more than once, the authorization server
        MUST deny the request and SHOULD revoke (when possible) all tokens
        previously issued based on that authorization code. The authorization
        code is bound to the client identifier and redirection URI.
        """
        headers = {
                'Content-Type': 'application/json',
                'Cache-Control': 'no-store',
                'Pragma': 'no-cache',
        }
        try:
            self.validate_token_request(request)
            log.debug('Token request validation ok for %r.', request)
        except errors.OAuth2Error as e:
            log.debug('Client error during validation of %r. %r.', request, e)
            return headers, e.json, e.status_code

        token = token_handler.create_token(request, refresh_token=True)
        self.request_validator.invalidate_authorization_code(
                request.client_id, request.code, request)
        return headers, json.dumps(token), 200

    def validate_authorization_request(self, request):
        """Check the authorization request for normal and fatal errors.

        A normal error could be a missing response_type parameter or the client
        attempting to access scope it is not allowed to ask authorization for.
        Normal errors can safely be included in the redirection URI and
        sent back to the client.

        Fatal errors occur when the client_id or redirect_uri is invalid or
        missing. These must be caught by the provider and handled, how this
        is done is outside of the scope of OAuthLib but showing an error
        page describing the issue is a good idea.
        """

        # First check for fatal errors

        # If the request fails due to a missing, invalid, or mismatching
        # redirection URI, or if the client identifier is missing or invalid,
        # the authorization server SHOULD inform the resource owner of the
        # error and MUST NOT automatically redirect the user-agent to the
        # invalid redirection URI.

        # REQUIRED. The client identifier as described in Section 2.2.
        # http://tools.ietf.org/html/rfc6749#section-2.2
        if not request.client_id:
            raise errors.MissingClientIdError(state=request.state, request=request)

        if not self.request_validator.validate_client_id(request.client_id, request):
            raise errors.InvalidClientIdError(state=request.state, request=request)

        # OPTIONAL. As described in Section 3.1.2.
        # http://tools.ietf.org/html/rfc6749#section-3.1.2
        log.debug('Validating redirection uri %s for client %s.',
                  request.redirect_uri, request.client_id)
        if request.redirect_uri is not None:
            request.using_default_redirect_uri = False
            log.debug('Using provided redirect_uri %s', request.redirect_uri)
            if not is_absolute_uri(request.redirect_uri):
                raise errors.InvalidRedirectURIError(state=request.state, request=request)

            if not self.request_validator.validate_redirect_uri(
                    request.client_id, request.redirect_uri, request):
                raise errors.MismatchingRedirectURIError(state=request.state, request=request)
        else:
            request.redirect_uri = self.request_validator.get_default_redirect_uri(
                    request.client_id, request)
            request.using_default_redirect_uri = True
            log.debug('Using default redirect_uri %s.', request.redirect_uri)
            if not request.redirect_uri:
                raise errors.MissingRedirectURIError(state=request.state, request=request)

        # Then check for normal errors.

        # If the resource owner denies the access request or if the request
        # fails for reasons other than a missing or invalid redirection URI,
        # the authorization server informs the client by adding the following
        # parameters to the query component of the redirection URI using the
        # "application/x-www-form-urlencoded" format, per Appendix B.
        # http://tools.ietf.org/html/rfc6749#appendix-B

        # Note that the correct parameters to be added are automatically
        # populated through the use of specific exceptions.
        if request.response_type is None:
            raise errors.InvalidRequestError(state=request.state,
                    description='Missing response_type parameter.', request=request)

        for param in ('client_id', 'response_type', 'redirect_uri', 'scope', 'state'):
            if param in request.duplicate_params:
                raise errors.InvalidRequestError(state=request.state,
                        description='Duplicate %s parameter.' % param, request=request)

        if not self.request_validator.validate_response_type(request.client_id,
                request.response_type, request.client, request):
            log.debug('Client %s is not authorized to use response_type %s.',
                      request.client_id, request.response_type)
            raise errors.UnauthorizedClientError(request=request)

        # REQUIRED. Value MUST be set to "code".
        if request.response_type != 'code':
            raise errors.UnsupportedResponseTypeError(state=request.state, request=request)

        # OPTIONAL. The scope of the access request as described by Section 3.3
        # http://tools.ietf.org/html/rfc6749#section-3.3
        self.validate_scopes(request)

        return request.scopes, {
                'client_id': request.client_id,
                'redirect_uri': request.redirect_uri,
                'response_type': request.response_type,
                'state': request.state,
                'request': request,
        }

    def validate_token_request(self, request):
        # REQUIRED. Value MUST be set to "authorization_code".
        if request.grant_type != 'authorization_code':
            raise errors.UnsupportedGrantTypeError(request=request)

        if request.code is None:
            raise errors.InvalidRequestError(
                description='Missing code parameter.', request=request)

        for param in ('client_id', 'grant_type', 'redirect_uri'):
            if param in request.duplicate_params:
                raise errors.InvalidRequestError(state=request.state,
                                                 description='Duplicate %s parameter.' % param,
                                                 request=request)

        if self.request_validator.client_authentication_required(request):
            # If the client type is confidential or the client was issued client
            # credentials (or assigned other authentication requirements), the
            # client MUST authenticate with the authorization server as described
            # in Section 3.2.1.
            # http://tools.ietf.org/html/rfc6749#section-3.2.1
            if not self.request_validator.authenticate_client(request):
                log.debug('Client authentication failed, %r.', request)
                raise errors.InvalidClientError(request=request)
        elif not self.request_validator.authenticate_client_id(request.client_id, request):
            # REQUIRED, if the client is not authenticating with the
            # authorization server as described in Section 3.2.1.
            # http://tools.ietf.org/html/rfc6749#section-3.2.1
            log.debug('Client authentication failed, %r.', request)
            raise errors.InvalidClientError(request=request)

        if not hasattr(request.client, 'client_id'):
            raise NotImplementedError('Authenticate client must set the '
                                      'request.client.client_id attribute '
                                      'in authenticate_client.')

        # Ensure client is authorized use of this grant type
        self.validate_grant_type(request)

        # REQUIRED. The authorization code received from the
        # authorization server.
        if not self.request_validator.validate_code(request.client_id,
                                                    request.code, request.client, request):
            log.debug('Client, %r (%r), is not allowed access to scopes %r.',
                      request.client_id, request.client, request.scopes)
            raise errors.InvalidGrantError(request=request)

        for attr in ('user', 'state', 'scopes'):
            if getattr(request, attr) is None:
                log.debug('request.%s was not set on code validation.', attr)

        # REQUIRED, if the "redirect_uri" parameter was included in the
        # authorization request as described in Section 4.1.1, and their
        # values MUST be identical.
        if not self.request_validator.confirm_redirect_uri(request.client_id, request.code,
                                                           request.redirect_uri, request.client):
            log.debug('Redirect_uri (%r) invalid for client %r (%r).',
                      request.redirect_uri, request.client_id, request.client)
            raise errors.AccessDeniedError(request=request)
