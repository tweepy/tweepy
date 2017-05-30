# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from json import loads
from mock import MagicMock

from oauthlib.common import urlencode
from oauthlib.oauth2 import RequestValidator, RevocationEndpoint

from ....unittest import TestCase


class RevocationEndpointTest(TestCase):

    def setUp(self):
        self.validator = MagicMock(wraps=RequestValidator())
        self.validator.authenticate_client.return_value = True
        self.validator.revoke_token.return_value = True
        self.endpoint = RevocationEndpoint(self.validator)

        self.uri = 'https://example.com/revoke_token'
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

    def test_revoke_token(self):
        for token_type in ('access_token', 'refresh_token', 'invalid'):
            body = urlencode([('token', 'foo'),
                              ('token_type_hint', token_type)])
            h, b, s = self.endpoint.create_revocation_response(self.uri,
                    headers=self.headers, body=body)
            self.assertEqual(h, {})
            self.assertEqual(b, None)
            self.assertEqual(s, 200)

    def test_revoke_with_callback(self):
        callback = 'package.hello_world'
        for token_type in ('access_token', 'refresh_token', 'invalid'):
            body = urlencode([('token', 'foo'),
                              ('token_type_hint', token_type),
                              ('callback', callback)])
            h, b, s = self.endpoint.create_revocation_response(self.uri,
                    headers=self.headers, body=body)
            self.assertEqual(h, {})
            self.assertEqual(b, callback + '()')
            self.assertEqual(s, 200)

    def test_revoke_unsupported_token(self):
        endpoint = RevocationEndpoint(self.validator,
                                      supported_token_types=['access_token'])
        body = urlencode([('token', 'foo'),
                          ('token_type_hint', 'refresh_token')])
        h, b, s = endpoint.create_revocation_response(self.uri,
                headers=self.headers, body=body)
        self.assertEqual(h, {})
        self.assertEqual(loads(b)['error'], 'unsupported_token_type')
        self.assertEqual(s, 400)

        h, b, s = endpoint.create_revocation_response(self.uri,
                headers=self.headers, body='')
        self.assertEqual(h, {})
        self.assertEqual(loads(b)['error'], 'invalid_request')
        self.assertEqual(s, 400)


