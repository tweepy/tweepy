# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from ....unittest import TestCase

import mock
from oauthlib import common
from oauthlib.common import Request
from oauthlib.oauth2.rfc6749.grant_types import ImplicitGrant
from oauthlib.oauth2.rfc6749.tokens import BearerToken


class ImplicitGrantTest(TestCase):

    def setUp(self):
        mock_client = mock.MagicMock()
        mock_client.user.return_value = 'mocked user'
        self.request = Request('http://a.b/path')
        self.request.scopes = ('hello', 'world')
        self.request.client = mock_client
        self.request.client_id = 'abcdef'
        self.request.response_type = 'token'
        self.request.state = 'xyz'
        self.request.redirect_uri = 'https://b.c/p'

        self.mock_validator = mock.MagicMock()
        self.auth = ImplicitGrant(request_validator=self.mock_validator)

    def test_create_token_response(self):
        bearer = BearerToken(self.mock_validator, expires_in=1800)
        orig_generate_token = common.generate_token
        self.addCleanup(setattr, common, 'generate_token', orig_generate_token)
        common.generate_token = lambda *args, **kwargs: '1234'
        headers, body, status_code = self.auth.create_token_response(
                self.request, bearer)
        correct_uri = 'https://b.c/p#access_token=1234&token_type=Bearer&expires_in=1800&state=xyz&scope=hello+world'
        self.assertEqual(status_code, 302)
        self.assertIn('Location', headers)
        self.assertURLEqual(headers['Location'], correct_uri, parse_fragment=True)

    def test_error_response(self):
        pass
