"""Ensure all tokens are associated with a resource owner.
"""
from __future__ import absolute_import, unicode_literals
import json
import mock

from .test_utils import get_query_credentials, get_fragment_credentials
from ....unittest import TestCase

from oauthlib.oauth2 import RequestValidator
from oauthlib.oauth2 import WebApplicationServer, MobileApplicationServer
from oauthlib.oauth2 import LegacyApplicationServer, BackendApplicationServer


class ResourceOwnerAssociationTest(TestCase):

    auth_uri = 'http://example.com/path?client_id=abc'
    token_uri = 'http://example.com/path'

    def set_client(self, request):
        request.client = mock.MagicMock()
        request.client.client_id = 'mocked'
        return True

    def set_user(self, client_id, code, client, request):
        request.user = 'test'
        return True

    def set_user_from_username(self, username, password, client, request):
        request.user = 'test'
        return True

    def set_user_from_credentials(self, request):
        request.user = 'test'
        request.client = mock.MagicMock()
        request.client.client_id = 'mocked'
        return True

    def inspect_client(self, request, refresh_token=False):
        if not request.user:
            raise ValueError()
        return 'abc'

    def setUp(self):
        self.validator = mock.MagicMock(spec=RequestValidator)
        self.validator.get_default_redirect_uri.return_value = 'http://i.b./path'
        self.validator.authenticate_client.side_effect = self.set_client
        self.web = WebApplicationServer(self.validator,
                token_generator=self.inspect_client)
        self.mobile = MobileApplicationServer(self.validator,
                token_generator=self.inspect_client)
        self.legacy = LegacyApplicationServer(self.validator,
                token_generator=self.inspect_client)
        self.backend = BackendApplicationServer(self.validator,
                token_generator=self.inspect_client)

    def test_web_application(self):
        # TODO: code generator + intercept test
        h, _, s = self.web.create_authorization_response(
                self.auth_uri + '&response_type=code',
                credentials={'user': 'test'}, scopes=['random'])
        self.assertEqual(s, 302)
        self.assertIn('Location', h)
        code = get_query_credentials(h['Location'])['code'][0]
        self.assertRaises(ValueError,
                self.web.create_token_response, self.token_uri,
                body='grant_type=authorization_code&code=%s' % code)

        self.validator.validate_code.side_effect = self.set_user
        _, body, _ = self.web.create_token_response(self.token_uri,
                body='grant_type=authorization_code&code=%s' % code)
        self.assertEqual(json.loads(body)['access_token'], 'abc')

    def test_mobile_application(self):
        self.assertRaises(ValueError,
                self.mobile.create_authorization_response,
                self.auth_uri + '&response_type=token')

        h, _, s = self.mobile.create_authorization_response(
                self.auth_uri + '&response_type=token',
                credentials={'user': 'test'}, scopes=['random'])
        self.assertEqual(s, 302)
        self.assertIn('Location', h)
        self.assertEqual(get_fragment_credentials(h['Location'])['access_token'][0], 'abc')

    def test_legacy_application(self):
        body = 'grant_type=password&username=abc&password=secret'
        self.assertRaises(ValueError,
                self.legacy.create_token_response,
                self.token_uri, body=body)

        self.validator.validate_user.side_effect = self.set_user_from_username
        _, body, _ = self.legacy.create_token_response(
                self.token_uri, body=body)
        self.assertEqual(json.loads(body)['access_token'], 'abc')

    def test_backend_application(self):
        body = 'grant_type=client_credentials'
        self.assertRaises(ValueError,
                self.backend.create_token_response,
                self.token_uri, body=body)

        self.validator.authenticate_client.side_effect = self.set_user_from_credentials
        _, body, _ = self.backend.create_token_response(
                self.token_uri, body=body)
        self.assertEqual(json.loads(body)['access_token'], 'abc')
