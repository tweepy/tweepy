# -*- coding: utf-8 -*-
"""
oauthlib.oauth2.rfc6749.grant_types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from __future__ import unicode_literals, absolute_import

from oauthlib.common import log
from oauthlib.oauth2.rfc6749 import errors, utils


class GrantTypeBase(object):
    error_uri = None
    request_validator = None

    def create_authorization_response(self, request, token_handler):
        raise NotImplementedError('Subclasses must implement this method.')

    def create_token_response(self, request, token_handler):
        raise NotImplementedError('Subclasses must implement this method.')

    def validate_grant_type(self, request):
        if not self.request_validator.validate_grant_type(request.client_id,
                request.grant_type, request.client, request):
            log.debug('Unauthorized from %r (%r) access to grant type %s.',
                      request.client_id, request.client, request.grant_type)
            raise errors.UnauthorizedClientError(request=request)

    def validate_scopes(self, request):
        if not request.scopes:
            request.scopes = utils.scope_to_list(request.scope) or utils.scope_to_list(
                    self.request_validator.get_default_scopes(request.client_id, request))
        log.debug('Validating access to scopes %r for client %r (%r).',
                  request.scopes, request.client_id, request.client)
        if not self.request_validator.validate_scopes(request.client_id,
                request.scopes, request.client, request):
            raise errors.InvalidScopeError(state=request.state, request=request)
