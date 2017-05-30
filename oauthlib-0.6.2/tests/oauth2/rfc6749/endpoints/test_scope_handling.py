"""Ensure scope is preserved across authorization.

Fairly trivial in all grants except the Authorization Code Grant where scope
need to be persisted temporarily in an authorization code.
"""
from __future__ import absolute_import, unicode_literals
import json
import mock

from .test_utils import get_query_credentials, get_fragment_credentials
from ....unittest import TestCase

from oauthlib.oauth2 import RequestValidator
from oauthlib.oauth2 import WebApplicationServer, MobileApplicationServer
from oauthlib.oauth2 import LegacyApplicationServer, BackendApplicationServer


class TestScopeHandling(TestCase):

    DEFAULT_REDIRECT_URI = 'http://i.b./path'

    def set_scopes(self, scopes):
        def set_request_scopes(client_id, code, client, request):
            request.scopes = scopes
            return True
        return set_request_scopes

    def set_user(self, request):
        request.user = 'foo'
        request.client_id = 'bar'
        request.client = mock.MagicMock()
        request.client.client_id = 'mocked'
        return True

    def set_client(self, request):
        request.client = mock.MagicMock()
        request.client.client_id = 'mocked'
        return True

    def setUp(self):
        self.validator = mock.MagicMock(spec=RequestValidator)
        self.validator.get_default_redirect_uri.return_value = TestScopeHandling.DEFAULT_REDIRECT_URI
        self.validator.authenticate_client.side_effect = self.set_client
        self.web = WebApplicationServer(self.validator)
        self.mobile = MobileApplicationServer(self.validator)
        self.legacy = LegacyApplicationServer(self.validator)
        self.backend = BackendApplicationServer(self.validator)

    def test_scope_extraction(self):
        scopes = (
            ('images', ['images']),
            ('images+videos', ['images', 'videos']),
            ('http%3A%2f%2fa.b%2fvideos', ['http://a.b/videos']),
            ('http%3A%2f%2fa.b%2fvideos+pics', ['http://a.b/videos', 'pics']),
            ('pics+http%3A%2f%2fa.b%2fvideos', ['pics', 'http://a.b/videos']),
            ('http%3A%2f%2fa.b%2fvideos+https%3A%2f%2fc.d%2Fsecret', ['http://a.b/videos', 'https://c.d/secret']),
        )

        uri = 'http://example.com/path?client_id=abc&scope=%s&response_type=%s'
        for scope, correct_scopes in scopes:
            scopes, _ = self.web.validate_authorization_request(
                    uri % (scope, 'code'))
            self.assertItemsEqual(scopes, correct_scopes)
            scopes, _ = self.mobile.validate_authorization_request(
                    uri % (scope, 'token'))
            self.assertItemsEqual(scopes, correct_scopes)

    def test_scope_preservation(self):
        scope = 'pics+http%3A%2f%2fa.b%2fvideos'
        decoded_scope = 'pics http://a.b/videos'
        auth_uri = 'http://example.com/path?client_id=abc&response_type='
        token_uri = 'http://example.com/path'

        # authorization grant
        h, _, s = self.web.create_authorization_response(
                auth_uri + 'code', scopes=decoded_scope.split(' '))
        self.validator.validate_code.side_effect = self.set_scopes(decoded_scope.split(' '))
        self.assertEqual(s, 302)
        self.assertIn('Location', h)
        code = get_query_credentials(h['Location'])['code'][0]
        _, body, _ = self.web.create_token_response(token_uri,
                body='grant_type=authorization_code&code=%s' % code)
        self.assertEqual(json.loads(body)['scope'], decoded_scope)

        # implicit grant
        h, _, s = self.mobile.create_authorization_response(
                auth_uri + 'token', scopes=decoded_scope.split(' '))
        self.assertEqual(s, 302)
        self.assertIn('Location', h)
        self.assertEqual(get_fragment_credentials(h['Location'])['scope'][0], decoded_scope)

        # resource owner password credentials grant
        body = 'grant_type=password&username=abc&password=secret&scope=%s'

        _, body, _ = self.legacy.create_token_response(token_uri,
                body=body % scope)
        self.assertEqual(json.loads(body)['scope'], decoded_scope)

        # client credentials grant
        body = 'grant_type=client_credentials&scope=%s'
        self.validator.authenticate_client.side_effect = self.set_user
        _, body, _ = self.backend.create_token_response(token_uri,
                body=body % scope)
        self.assertEqual(json.loads(body)['scope'], decoded_scope)

    def test_scope_changed(self):
        scope = 'pics+http%3A%2f%2fa.b%2fvideos'
        scopes = ['images', 'http://a.b/videos']
        decoded_scope = 'images http://a.b/videos'
        auth_uri = 'http://example.com/path?client_id=abc&response_type='
        token_uri = 'http://example.com/path'

        # authorization grant
        h, _, s = self.web.create_authorization_response(
                auth_uri + 'code', scopes=scopes)
        self.assertEqual(s, 302)
        self.assertIn('Location', h)
        code = get_query_credentials(h['Location'])['code'][0]
        self.validator.validate_code.side_effect = self.set_scopes(scopes)
        _, body, _ = self.web.create_token_response(token_uri,
                body='grant_type=authorization_code&code=%s' % code)
        self.assertEqual(json.loads(body)['scope'], decoded_scope)

        # implicit grant
        self.validator.validate_scopes.side_effect = self.set_scopes(scopes)
        h, _, s = self.mobile.create_authorization_response(
                auth_uri + 'token', scopes=scopes)
        self.assertEqual(s, 302)
        self.assertIn('Location', h)
        self.assertEqual(get_fragment_credentials(h['Location'])['scope'][0], decoded_scope)

        # resource owner password credentials grant
        self.validator.validate_scopes.side_effect = self.set_scopes(scopes)
        body = 'grant_type=password&username=abc&password=secret&scope=%s'
        _, body, _ = self.legacy.create_token_response(token_uri,
                body=body % scope)
        self.assertEqual(json.loads(body)['scope'], decoded_scope)

        # client credentials grant
        self.validator.validate_scopes.side_effect = self.set_scopes(scopes)
        self.validator.authenticate_client.side_effect = self.set_user
        body = 'grant_type=client_credentials&scope=%s'
        _, body, _ = self.backend.create_token_response(token_uri,
                body=body % scope)

        self.assertEqual(json.loads(body)['scope'], decoded_scope)

    def test_invalid_scope(self):
        scope = 'pics+http%3A%2f%2fa.b%2fvideos'
        auth_uri = 'http://example.com/path?client_id=abc&response_type='
        token_uri = 'http://example.com/path'

        self.validator.validate_scopes.return_value = False

        # authorization grant
        h, _, s = self.web.create_authorization_response(
                auth_uri + 'code', scopes=['invalid'])
        self.assertEqual(s, 302)
        self.assertIn('Location', h)
        error = get_query_credentials(h['Location'])['error'][0]
        self.assertEqual(error, 'invalid_scope')

        # implicit grant
        h, _, s = self.mobile.create_authorization_response(
                auth_uri + 'token', scopes=['invalid'])
        self.assertEqual(s, 302)
        self.assertIn('Location', h)
        error = get_fragment_credentials(h['Location'])['error'][0]
        self.assertEqual(error, 'invalid_scope')

        # resource owner password credentials grant
        body = 'grant_type=password&username=abc&password=secret&scope=%s'
        _, body, _ = self.legacy.create_token_response(token_uri,
                body=body % scope)
        self.assertEqual(json.loads(body)['error'], 'invalid_scope')

        # client credentials grant
        self.validator.authenticate_client.side_effect = self.set_user
        body = 'grant_type=client_credentials&scope=%s'
        _, body, _ = self.backend.create_token_response(token_uri,
                body=body % scope)
        self.assertEqual(json.loads(body)['error'], 'invalid_scope')
