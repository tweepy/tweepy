# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from ....unittest import TestCase

import json
import mock
from oauthlib.common import Request
from oauthlib.oauth2.rfc6749.grant_types import ClientCredentialsGrant
from oauthlib.oauth2.rfc6749.tokens import BearerToken


class ClientCredentialsGrantTest(TestCase):

    def setUp(self):
        mock_client = mock.MagicMock()
        mock_client.user.return_value = 'mocked user'
        self.request = Request('http://a.b/path')
        self.request.grant_type = 'client_credentials'
        self.request.client = mock_client
        self.request.scopes = ('mocked', 'scopes')
        self.mock_validator = mock.MagicMock()
        self.auth = ClientCredentialsGrant(
                request_validator=self.mock_validator)

    def test_create_token_response(self):
        bearer = BearerToken(self.mock_validator)
        headers, body, status_code = self.auth.create_token_response(
                self.request, bearer)
        token = json.loads(body)
        self.assertIn('access_token', token)
        self.assertIn('token_type', token)
        self.assertIn('expires_in', token)
        self.assertIn('Content-Type', headers)
        self.assertEqual(headers['Content-Type'], 'application/json')

    def test_error_response(self):
        bearer = BearerToken(self.mock_validator)
        self.mock_validator.authenticate_client.return_value = False
        headers, body, status_code = self.auth.create_token_response(
            self.request, bearer)
        error_msg = json.loads(body)
        self.assertIn('error', error_msg)
        self.assertEqual(error_msg['error'], 'invalid_client')
        self.assertIn('Content-Type', headers)
        self.assertEqual(headers['Content-Type'], 'application/json')

    def test_validate_token_response(self):
        # wrong grant type, scope
        pass
