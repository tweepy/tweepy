from __future__ import unicode_literals, absolute_import

from mock import MagicMock
from ....unittest import TestCase

from oauthlib.oauth1 import RequestValidator
from oauthlib.oauth1.rfc5849 import errors
from oauthlib.oauth1.rfc5849.endpoints import AuthorizationEndpoint


class AuthorizationEndpointTest(TestCase):

    def setUp(self):
        self.validator = MagicMock(wraps=RequestValidator())
        self.validator.verify_request_token.return_value = True
        self.validator.verify_realms.return_value = True
        self.validator.get_realms.return_value = ['test']
        self.validator.save_verifier = MagicMock()
        self.endpoint = AuthorizationEndpoint(self.validator)
        self.uri = 'https://i.b/authorize?oauth_token=foo'

    def test_get_realms_and_credentials(self):
        realms, credentials = self.endpoint.get_realms_and_credentials(self.uri)
        self.assertEqual(realms, ['test'])

    def test_verify_token(self):
        self.validator.verify_request_token.return_value = False
        self.assertRaises(errors.InvalidClientError,
                self.endpoint.get_realms_and_credentials, self.uri)
        self.assertRaises(errors.InvalidClientError,
                self.endpoint.create_authorization_response, self.uri)

    def test_verify_realms(self):
        self.validator.verify_realms.return_value = False
        self.assertRaises(errors.InvalidRequestError,
                self.endpoint.create_authorization_response,
                self.uri,
                realms=['bar'])

    def test_create_authorization_response(self):
        self.validator.get_redirect_uri.return_value = 'https://c.b/cb'
        h, b, s = self.endpoint.create_authorization_response(self.uri)
        self.assertEqual(s, 302)
        self.assertIn('Location', h)
        location = h['Location']
        self.assertTrue(location.startswith('https://c.b/cb'))
        self.assertIn('oauth_verifier', location)

    def test_create_authorization_response_oob(self):
        self.validator.get_redirect_uri.return_value = 'oob'
        h, b, s = self.endpoint.create_authorization_response(self.uri)
        self.assertEqual(s, 200)
        self.assertNotIn('Location', h)
        self.assertIn('oauth_verifier', b)
        self.assertIn('oauth_token', b)
