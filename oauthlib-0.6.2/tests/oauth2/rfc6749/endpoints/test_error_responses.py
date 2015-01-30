"""Ensure the correct error responses are returned for all defined error types.
"""
from __future__ import absolute_import, unicode_literals
import json
import mock

from ....unittest import TestCase

from oauthlib.oauth2 import RequestValidator
from oauthlib.oauth2 import WebApplicationServer, MobileApplicationServer
from oauthlib.oauth2 import LegacyApplicationServer, BackendApplicationServer
from oauthlib.oauth2.rfc6749 import errors


class ErrorResponseTest(TestCase):

    def set_client(self, request):
        request.client = mock.MagicMock()
        request.client.client_id = 'mocked'
        return True

    def setUp(self):
        self.validator = mock.MagicMock(spec=RequestValidator)
        self.validator.get_default_redirect_uri.return_value = None
        self.web = WebApplicationServer(self.validator)
        self.mobile = MobileApplicationServer(self.validator)
        self.legacy = LegacyApplicationServer(self.validator)
        self.backend = BackendApplicationServer(self.validator)

    def test_invalid_redirect_uri(self):
        uri = 'https://example.com/authorize?client_id=foo&redirect_uri=wrong'
        # Authorization code grant
        self.assertRaises(errors.InvalidRedirectURIError,
                self.web.validate_authorization_request, uri)
        self.assertRaises(errors.InvalidRedirectURIError,
                self.web.create_authorization_response, uri, scopes=['foo'])

        # Implicit grant
        self.assertRaises(errors.InvalidRedirectURIError,
                self.mobile.validate_authorization_request, uri)
        self.assertRaises(errors.InvalidRedirectURIError,
                self.mobile.create_authorization_response, uri, scopes=['foo'])

    def test_missing_redirect_uri(self):
        uri = 'https://example.com/authorize?client_id=foo'
        # Authorization code grant
        self.assertRaises(errors.MissingRedirectURIError,
                self.web.validate_authorization_request, uri)
        self.assertRaises(errors.MissingRedirectURIError,
                self.web.create_authorization_response, uri, scopes=['foo'])

        # Implicit grant
        self.assertRaises(errors.MissingRedirectURIError,
                self.mobile.validate_authorization_request, uri)
        self.assertRaises(errors.MissingRedirectURIError,
                self.mobile.create_authorization_response, uri, scopes=['foo'])

    def test_mismatching_redirect_uri(self):
        uri = 'https://example.com/authorize?client_id=foo&redirect_uri=https%3A%2F%2Fi.b%2Fback'
        # Authorization code grant
        self.validator.validate_redirect_uri.return_value = False
        self.assertRaises(errors.MismatchingRedirectURIError,
                self.web.validate_authorization_request, uri)
        self.assertRaises(errors.MismatchingRedirectURIError,
                self.web.create_authorization_response, uri, scopes=['foo'])

        # Implicit grant
        self.assertRaises(errors.MismatchingRedirectURIError,
                self.mobile.validate_authorization_request, uri)
        self.assertRaises(errors.MismatchingRedirectURIError,
                self.mobile.create_authorization_response, uri, scopes=['foo'])

    def test_missing_client_id(self):
        uri = 'https://example.com/authorize?redirect_uri=https%3A%2F%2Fi.b%2Fback'
        # Authorization code grant
        self.validator.validate_redirect_uri.return_value = False
        self.assertRaises(errors.MissingClientIdError,
                self.web.validate_authorization_request, uri)
        self.assertRaises(errors.MissingClientIdError,
                self.web.create_authorization_response, uri, scopes=['foo'])

        # Implicit grant
        self.assertRaises(errors.MissingClientIdError,
                self.mobile.validate_authorization_request, uri)
        self.assertRaises(errors.MissingClientIdError,
                self.mobile.create_authorization_response, uri, scopes=['foo'])

    def test_invalid_client_id(self):
        uri = 'https://example.com/authorize?client_id=foo&redirect_uri=https%3A%2F%2Fi.b%2Fback'
        # Authorization code grant
        self.validator.validate_client_id.return_value = False
        self.assertRaises(errors.InvalidClientIdError,
                self.web.validate_authorization_request, uri)
        self.assertRaises(errors.InvalidClientIdError,
                self.web.create_authorization_response, uri, scopes=['foo'])

        # Implicit grant
        self.assertRaises(errors.InvalidClientIdError,
                self.mobile.validate_authorization_request, uri)
        self.assertRaises(errors.InvalidClientIdError,
                self.mobile.create_authorization_response, uri, scopes=['foo'])

    def test_invalid_request(self):
        self.validator.get_default_redirect_uri.return_value = 'https://i.b/cb'
        token_uri = 'https://i.b/token'
        invalid_uris = [
            # Duplicate parameters
            'https://i.b/auth?client_id=foo&client_id=bar&response_type={0}',
            # Missing response type
            'https://i.b/auth?client_id=foo',
        ]

        # Authorization code grant
        for uri in invalid_uris:
            self.assertRaises(errors.InvalidRequestError,
                    self.web.validate_authorization_request,
                    uri.format('code'))
            h, _, s = self.web.create_authorization_response(
                    uri.format('code'), scopes=['foo'])
            self.assertEqual(s, 302)
            self.assertIn('Location', h)
            self.assertIn('error=invalid_request', h['Location'])
        invalid_bodies = [
            # duplicate params
            'grant_type=authorization_code&client_id=nope&client_id=nope&code=foo'
        ]
        for body in invalid_bodies:
            _, body, _ = self.web.create_token_response(token_uri,
                    body=body)
            self.assertEqual('invalid_request', json.loads(body)['error'])

        # Implicit grant
        for uri in invalid_uris:
            self.assertRaises(errors.InvalidRequestError,
                    self.mobile.validate_authorization_request,
                    uri.format('token'))
            h, _, s = self.mobile.create_authorization_response(
                    uri.format('token'), scopes=['foo'])
            self.assertEqual(s, 302)
            self.assertIn('Location', h)
            self.assertIn('error=invalid_request', h['Location'])

        # Password credentials grant
        invalid_bodies = [
            # duplicate params
            'grant_type=password&username=foo&username=bar&password=baz'
            # missing username
            'grant_type=password&password=baz'
            # missing password
            'grant_type=password&username=foo'
        ]
        self.validator.authenticate_client.side_effect = self.set_client
        for body in invalid_bodies:
            _, body, _ = self.legacy.create_token_response(token_uri,
                    body=body)
            self.assertEqual('invalid_request', json.loads(body)['error'])

        # Client credentials grant
        invalid_bodies = [
            # duplicate params
            'grant_type=client_credentials&scope=foo&scope=bar'
        ]
        for body in invalid_bodies:
            _, body, _ = self.backend.create_token_response(token_uri,
                    body=body)
            self.assertEqual('invalid_request', json.loads(body)['error'])

    def test_unauthorized_client(self):
        self.validator.get_default_redirect_uri.return_value = 'https://i.b/cb'
        self.validator.validate_grant_type.return_value = False
        self.validator.validate_response_type.return_value = False
        self.validator.authenticate_client.side_effect = self.set_client
        token_uri = 'https://i.b/token'

        # Authorization code grant
        self.assertRaises(errors.UnauthorizedClientError,
                self.web.validate_authorization_request,
                'https://i.b/auth?response_type=code&client_id=foo')
        _, body, _ = self.web.create_token_response(token_uri,
                body='grant_type=authorization_code&code=foo')
        self.assertEqual('unauthorized_client', json.loads(body)['error'])

        # Implicit grant
        self.assertRaises(errors.UnauthorizedClientError,
                self.mobile.validate_authorization_request,
                'https://i.b/auth?response_type=token&client_id=foo')

        # Password credentials grant
        _, body, _ = self.legacy.create_token_response(token_uri,
                body='grant_type=password&username=foo&password=bar')
        self.assertEqual('unauthorized_client', json.loads(body)['error'])

        # Client credentials grant
        _, body, _ = self.backend.create_token_response(token_uri,
                body='grant_type=client_credentials')
        self.assertEqual('unauthorized_client', json.loads(body)['error'])

    def test_access_denied(self):
        self.validator.authenticate_client.side_effect = self.set_client
        self.validator.confirm_redirect_uri.return_value = False
        token_uri = 'https://i.b/token'
        # Authorization code grant
        _, body, _ = self.web.create_token_response(token_uri,
                body='grant_type=authorization_code&code=foo')
        self.assertEqual('access_denied', json.loads(body)['error'])

    def test_unsupported_response_type(self):
        self.validator.get_default_redirect_uri.return_value = 'https://i.b/cb'

        # Authorization code grant
        self.assertRaises(errors.UnsupportedResponseTypeError,
                self.web.validate_authorization_request,
                'https://i.b/auth?response_type=foo&client_id=foo')

        # Implicit grant
        self.assertRaises(errors.UnsupportedResponseTypeError,
                self.mobile.validate_authorization_request,
                'https://i.b/auth?response_type=foo&client_id=foo')

    def test_invalid_scope(self):
        self.validator.get_default_redirect_uri.return_value = 'https://i.b/cb'
        self.validator.validate_scopes.return_value = False
        self.validator.authenticate_client.side_effect = self.set_client

        # Authorization code grant
        self.assertRaises(errors.InvalidScopeError,
                self.web.validate_authorization_request,
                'https://i.b/auth?response_type=code&client_id=foo')

        # Implicit grant
        self.assertRaises(errors.InvalidScopeError,
                self.mobile.validate_authorization_request,
                'https://i.b/auth?response_type=token&client_id=foo')

        # Password credentials grant
        _, body, _ = self.legacy.create_token_response(
                'https://i.b/token',
                body='grant_type=password&username=foo&password=bar')
        self.assertEqual('invalid_scope', json.loads(body)['error'])

        # Client credentials grant
        _, body, _ = self.backend.create_token_response(
                'https://i.b/token',
                body='grant_type=client_credentials')
        self.assertEqual('invalid_scope', json.loads(body)['error'])

    def test_server_error(self):
        def raise_error(*args, **kwargs):
            raise ValueError()

        self.validator.validate_client_id.side_effect = raise_error
        self.validator.authenticate_client.side_effect = raise_error
        self.validator.get_default_redirect_uri.return_value = 'https://i.b/cb'

        # Authorization code grant
        self.web.catch_errors = True
        _, _, s = self.web.create_authorization_response(
                'https://i.b/auth?client_id=foo&response_type=code',
                scopes=['foo'])
        self.assertEqual(s, 500)
        _, _, s = self.web.create_token_response(
                'https://i.b/token',
                body='grant_type=authorization_code&code=foo',
                scopes=['foo'])
        self.assertEqual(s, 500)

        # Implicit grant
        self.mobile.catch_errors = True
        _, _, s = self.mobile.create_authorization_response(
                'https://i.b/auth?client_id=foo&response_type=token',
                scopes=['foo'])
        self.assertEqual(s, 500)

        # Password credentials grant
        self.legacy.catch_errors = True
        _, _, s = self.legacy.create_token_response(
                'https://i.b/token',
                body='grant_type=password&username=foo&password=foo')
        self.assertEqual(s, 500)

        # Client credentials grant
        self.backend.catch_errors = True
        _, _, s = self.backend.create_token_response(
                'https://i.b/token',
                body='grant_type=client_credentials')
        self.assertEqual(s, 500)

    def test_temporarily_unavailable(self):
        # Authorization code grant
        self.web.available = False
        _, _, s = self.web.create_authorization_response(
                'https://i.b/auth?client_id=foo&response_type=code',
                scopes=['foo'])
        self.assertEqual(s, 503)
        _, _, s = self.web.create_token_response(
                'https://i.b/token',
                body='grant_type=authorization_code&code=foo',
                scopes=['foo'])
        self.assertEqual(s, 503)

        # Implicit grant
        self.mobile.available = False
        _, _, s = self.mobile.create_authorization_response(
                'https://i.b/auth?client_id=foo&response_type=token',
                scopes=['foo'])
        self.assertEqual(s, 503)

        # Password credentials grant
        self.legacy.available = False
        _, _, s = self.legacy.create_token_response(
                'https://i.b/token',
                body='grant_type=password&username=foo&password=foo')
        self.assertEqual(s, 503)

        # Client credentials grant
        self.backend.available = False
        _, _, s = self.backend.create_token_response(
                'https://i.b/token',
                body='grant_type=client_credentials')
        self.assertEqual(s, 503)

    def test_invalid_client(self):
        self.validator.authenticate_client.return_value = False
        self.validator.authenticate_client_id.return_value = False

        # Authorization code grant
        _, body, _ = self.web.create_token_response('https://i.b/token',
                body='grant_type=authorization_code&code=foo')
        self.assertEqual('invalid_client', json.loads(body)['error'])

        # Password credentials grant
        _, body, _ = self.legacy.create_token_response('https://i.b/token',
                body='grant_type=password&username=foo&password=bar')
        self.assertEqual('invalid_client', json.loads(body)['error'])

        # Client credentials grant
        _, body, _ = self.legacy.create_token_response('https://i.b/token',
                body='grant_type=client_credentials')
        self.assertEqual('invalid_client', json.loads(body)['error'])

    def test_invalid_grant(self):
        self.validator.authenticate_client.side_effect = self.set_client

        # Authorization code grant
        self.validator.validate_code.return_value = False
        _, body, _ = self.web.create_token_response('https://i.b/token',
                body='grant_type=authorization_code&code=foo')
        self.assertEqual('invalid_grant', json.loads(body)['error'])

        # Password credentials grant
        self.validator.validate_user.return_value = False
        _, body, _ = self.legacy.create_token_response('https://i.b/token',
                body='grant_type=password&username=foo&password=bar')
        self.assertEqual('invalid_grant', json.loads(body)['error'])

    def test_unsupported_grant_type(self):
        self.validator.authenticate_client.side_effect = self.set_client

        # Authorization code grant
        _, body, _ = self.web.create_token_response('https://i.b/token',
                body='grant_type=bar&code=foo')
        self.assertEqual('unsupported_grant_type', json.loads(body)['error'])

        # Password credentials grant
        _, body, _ = self.legacy.create_token_response('https://i.b/token',
                body='grant_type=bar&username=foo&password=bar')
        self.assertEqual('unsupported_grant_type', json.loads(body)['error'])

        # Client credentials grant
        _, body, _ = self.backend.create_token_response('https://i.b/token',
                body='grant_type=bar')
        self.assertEqual('unsupported_grant_type', json.loads(body)['error'])
