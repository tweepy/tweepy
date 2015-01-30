"""Ensure extra credentials can be supplied for inclusion in tokens.
"""
from __future__ import absolute_import, unicode_literals
import mock

from ....unittest import TestCase

from oauthlib.oauth2 import RequestValidator
from oauthlib.oauth2 import WebApplicationServer, MobileApplicationServer
from oauthlib.oauth2 import LegacyApplicationServer, BackendApplicationServer


class ExtraCredentialsTest(TestCase):

    def set_client(self, request):
        request.client = mock.MagicMock()
        request.client.client_id = 'mocked'
        return True

    def setUp(self):
        self.validator = mock.MagicMock(spec=RequestValidator)
        self.validator.get_default_redirect_uri.return_value = 'https://i.b/cb'
        self.web = WebApplicationServer(self.validator)
        self.mobile = MobileApplicationServer(self.validator)
        self.legacy = LegacyApplicationServer(self.validator)
        self.backend = BackendApplicationServer(self.validator)

    def test_post_authorization_request(self):
        def save_code(client_id, token, request):
            self.assertEqual('creds', request.extra)

        def save_token(token, request):
            self.assertEqual('creds', request.extra)

        # Authorization code grant
        self.validator.save_authorization_code.side_effect = save_code
        self.web.create_authorization_response(
                'https://i.b/auth?client_id=foo&response_type=code',
                scopes=['foo'],
                credentials={'extra': 'creds'})

        # Implicit grant
        self.validator.save_bearer_token.side_effect = save_token
        self.web.create_authorization_response(
                'https://i.b/auth?client_id=foo&response_type=token',
                scopes=['foo'],
                credentials={'extra': 'creds'})

    def test_token_request(self):
        def save_token(token, request):
            self.assertIn('extra', token)

        self.validator.save_bearer_token.side_effect = save_token
        self.validator.authenticate_client.side_effect = self.set_client

        # Authorization code grant
        self.web.create_token_response('https://i.b/token',
                body='grant_type=authorization_code&code=foo',
                credentials={'extra': 'creds'})

        # Password credentials grant
        self.legacy.create_token_response('https://i.b/token',
                body='grant_type=password&username=foo&password=bar',
                credentials={'extra': 'creds'})

        # Client credentials grant
        self.backend.create_token_response('https://i.b/token',
                body='grant_type=client_credentials',
                credentials={'extra': 'creds'})
