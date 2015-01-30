# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from ...unittest import TestCase

from oauthlib.oauth2 import RequestValidator

class RequestValidatorTest(TestCase):

    def test_method_contracts(self):
        v = RequestValidator()
        self.assertRaises(NotImplementedError, v.authenticate_client, 'r')
        self.assertRaises(NotImplementedError, v.authenticate_client_id,
                'client_id', 'r')
        self.assertRaises(NotImplementedError, v.confirm_redirect_uri,
                'client_id', 'code', 'redirect_uri', 'client', 'request')
        self.assertRaises(NotImplementedError, v.get_default_redirect_uri,
                'client_id', 'request')
        self.assertRaises(NotImplementedError, v.get_default_scopes,
                'client_id', 'request')
        self.assertRaises(NotImplementedError, v.get_original_scopes,
                'refresh_token', 'request')
        self.assertFalse(v.is_within_original_scope(
                ['scope'], 'refresh_token', 'request'))
        self.assertRaises(NotImplementedError, v.invalidate_authorization_code,
                'client_id', 'code', 'request')
        self.assertRaises(NotImplementedError, v.save_authorization_code,
                'client_id', 'code', 'request')
        self.assertRaises(NotImplementedError, v.save_bearer_token,
                'token', 'request')
        self.assertRaises(NotImplementedError, v.validate_bearer_token,
                'token', 'scopes', 'request')
        self.assertRaises(NotImplementedError, v.validate_client_id,
                'client_id', 'request')
        self.assertRaises(NotImplementedError, v.validate_code,
                'client_id', 'code', 'client', 'request')
        self.assertRaises(NotImplementedError, v.validate_grant_type,
                'client_id', 'grant_type', 'client', 'request')
        self.assertRaises(NotImplementedError, v.validate_redirect_uri,
                'client_id', 'redirect_uri', 'request')
        self.assertRaises(NotImplementedError, v.validate_refresh_token,
                'refresh_token', 'client', 'request')
        self.assertRaises(NotImplementedError, v.validate_response_type,
                'client_id', 'response_type', 'client', 'request')
        self.assertRaises(NotImplementedError, v.validate_scopes,
                'client_id', 'scopes', 'client', 'request')
        self.assertRaises(NotImplementedError, v.validate_user,
                'username', 'password', 'client', 'request')
        self.assertTrue(v.client_authentication_required('r'))
