# -*- coding: utf-8 -*-
"""
oauthlib.oauth2.rfc6749.grant_types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from __future__ import unicode_literals, absolute_import
import json

from oauthlib.common import log

from .base import GrantTypeBase
from .. import errors, utils
from ..request_validator import RequestValidator


class RefreshTokenGrant(GrantTypeBase):
    """`Refresh token grant`_

    .. _`Refresh token grant`: http://tools.ietf.org/html/rfc6749#section-6
    """

    @property
    def issue_new_refresh_tokens(self):
        return True

    def __init__(self, request_validator=None, issue_new_refresh_tokens=True):
        self.request_validator = request_validator or RequestValidator()

    def create_token_response(self, request, token_handler):
        """Create a new access token from a refresh_token.

        If valid and authorized, the authorization server issues an access
        token as described in `Section 5.1`_. If the request failed
        verification or is invalid, the authorization server returns an error
        response as described in `Section 5.2`_.

        The authorization server MAY issue a new refresh token, in which case
        the client MUST discard the old refresh token and replace it with the
        new refresh token. The authorization server MAY revoke the old
        refresh token after issuing a new refresh token to the client. If a
        new refresh token is issued, the refresh token scope MUST be
        identical to that of the refresh token included by the client in the
        request.

        .. _`Section 5.1`: http://tools.ietf.org/html/rfc6749#section-5.1
        .. _`Section 5.2`: http://tools.ietf.org/html/rfc6749#section-5.2
        """
        headers = {
                'Content-Type': 'application/json',
                'Cache-Control': 'no-store',
                'Pragma': 'no-cache',
        }
        try:
            log.debug('Validating refresh token request, %r.', request)
            self.validate_token_request(request)
        except errors.OAuth2Error as e:
            return headers, e.json, e.status_code

        token = token_handler.create_token(request,
                refresh_token=self.issue_new_refresh_tokens)
        log.debug('Issuing new token to client id %r (%r), %r.',
                  request.client_id, request.client, token)
        return headers, json.dumps(token), 200

    def validate_token_request(self, request):
        # REQUIRED. Value MUST be set to "refresh_token".
        if request.grant_type != 'refresh_token':
            raise errors.UnsupportedGrantTypeError(request=request)

        if request.refresh_token is None:
            raise errors.InvalidRequestError(
                description='Missing refresh token parameter.',
                request=request)

        # Because refresh tokens are typically long-lasting credentials used to
        # request additional access tokens, the refresh token is bound to the
        # client to which it was issued.  If the client type is confidential or
        # the client was issued client credentials (or assigned other
        # authentication requirements), the client MUST authenticate with the
        # authorization server as described in Section 3.2.1.
        # http://tools.ietf.org/html/rfc6749#section-3.2.1
        if self.request_validator.client_authentication_required(request):
            log.debug('Authenticating client, %r.', request)
            if not self.request_validator.authenticate_client(request):
                log.debug('Invalid client (%r), denying access.', request)
                raise errors.InvalidClientError(request=request)
        elif not self.request_validator.authenticate_client_id(request.client_id, request):
            log.debug('Client authentication failed, %r.', request)
            raise errors.InvalidClientError(request=request)

        # Ensure client is authorized use of this grant type
        self.validate_grant_type(request)

        # REQUIRED. The refresh token issued to the client.
        log.debug('Validating refresh token %s for client %r.',
                  request.refresh_token, request.client)
        if not self.request_validator.validate_refresh_token(
                request.refresh_token, request.client, request):
            log.debug('Invalid refresh token, %s, for client %r.',
                      request.refresh_token, request.client)
            raise errors.InvalidGrantError(request=request)

        original_scopes = utils.scope_to_list(
                self.request_validator.get_original_scopes(
                    request.refresh_token, request))

        if request.scope:
            request.scopes = utils.scope_to_list(request.scope)
            if (not all((s in original_scopes for s in request.scopes))
                and not self.request_validator.is_within_original_scope(
                    request.scopes, request.refresh_token, request)):
                log.debug('Refresh token %s lack requested scopes, %r.',
                        request.refresh_token, request.scopes)
                raise errors.InvalidScopeError(
                        state=request.state, request=request)
        else:
            request.scopes = original_scopes
