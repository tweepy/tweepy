"""Ensure credentials are preserved through the authorization.

The Authorization Code Grant will need to preserve state as well as redirect
uri and the Implicit Grant will need to preserve state.
"""
from __future__ import absolute_import, unicode_literals
import json
import mock

from .test_utils import get_query_credentials, get_fragment_credentials
from ....unittest import TestCase

from oauthlib.oauth2 import RequestValidator
from oauthlib.oauth2 import WebApplicationServer, MobileApplicationServer
from oauthlib.oauth2.rfc6749 import errors


class PreservationTest(TestCase):

    DEFAULT_REDIRECT_URI = 'http://i.b./path'

    def setUp(self):
        self.validator = mock.MagicMock(spec=RequestValidator)
        self.validator.get_default_redirect_uri.return_value = self.DEFAULT_REDIRECT_URI
        self.validator.authenticate_client.side_effect = self.set_client
        self.web = WebApplicationServer(self.validator)
        self.mobile = MobileApplicationServer(self.validator)

    def set_state(self, state):
        def set_request_state(client_id, code, client, request):
            request.state = state
            return True
        return set_request_state

    def set_client(self, request):
        request.client = mock.MagicMock()
        request.client.client_id = 'mocked'
        return True

    def test_state_preservation(self):
        auth_uri = 'http://example.com/path?state=xyz&client_id=abc&response_type='
        token_uri = 'http://example.com/path'

        # authorization grant
        h, _, s = self.web.create_authorization_response(
                auth_uri + 'code', scopes=['random'])
        self.assertEqual(s, 302)
        self.assertIn('Location', h)
        code = get_query_credentials(h['Location'])['code'][0]
        self.validator.validate_code.side_effect = self.set_state('xyz')
        _, body, _ = self.web.create_token_response(token_uri,
                body='grant_type=authorization_code&code=%s' % code)
        self.assertEqual(json.loads(body)['state'], 'xyz')

        # implicit grant
        h, _, s = self.mobile.create_authorization_response(
                auth_uri + 'token', scopes=['random'])
        self.assertEqual(s, 302)
        self.assertIn('Location', h)
        self.assertEqual(get_fragment_credentials(h['Location'])['state'][0], 'xyz')

    def test_redirect_uri_preservation(self):
        auth_uri = 'http://example.com/path?redirect_uri=http%3A%2F%2Fi.b%2Fpath&client_id=abc'
        redirect_uri = 'http://i.b/path'
        token_uri = 'http://example.com/path'

        # authorization grant
        h, _, s = self.web.create_authorization_response(
                auth_uri + '&response_type=code', scopes=['random'])
        self.assertEqual(s, 302)
        self.assertIn('Location', h)
        self.assertTrue(h['Location'].startswith(redirect_uri))

        # confirm_redirect_uri should return false if the redirect uri
        # was given in the authorization but not in the token request.
        self.validator.confirm_redirect_uri.return_value = False
        code = get_query_credentials(h['Location'])['code'][0]
        _, body, _ = self.web.create_token_response(token_uri,
                body='grant_type=authorization_code&code=%s' % code)
        self.assertEqual(json.loads(body)['error'], 'access_denied')

        # implicit grant
        h, _, s = self.mobile.create_authorization_response(
                auth_uri + '&response_type=token', scopes=['random'])
        self.assertEqual(s, 302)
        self.assertIn('Location', h)
        self.assertTrue(h['Location'].startswith(redirect_uri))

    def test_invalid_redirect_uri(self):
        auth_uri = 'http://example.com/path?redirect_uri=http%3A%2F%2Fi.b%2Fpath&client_id=abc'
        self.validator.validate_redirect_uri.return_value = False

        # authorization grant
        self.assertRaises(errors.MismatchingRedirectURIError,
                self.web.create_authorization_response,
                auth_uri + '&response_type=code', scopes=['random'])

        # implicit grant
        self.assertRaises(errors.MismatchingRedirectURIError,
                self.mobile.create_authorization_response,
                auth_uri + '&response_type=token', scopes=['random'])

    def test_default_uri(self):
        auth_uri = 'http://example.com/path?state=xyz&client_id=abc'

        self.validator.get_default_redirect_uri.return_value = None

        # authorization grant
        self.assertRaises(errors.MissingRedirectURIError,
                self.web.create_authorization_response,
                auth_uri + '&response_type=code', scopes=['random'])

        # implicit grant
        self.assertRaises(errors.MissingRedirectURIError,
                self.mobile.create_authorization_response,
                auth_uri + '&response_type=token', scopes=['random'])
