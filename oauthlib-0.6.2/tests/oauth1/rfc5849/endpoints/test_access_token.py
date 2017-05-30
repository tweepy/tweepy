from __future__ import unicode_literals, absolute_import

from mock import MagicMock, ANY
from ....unittest import TestCase

from oauthlib.oauth1.rfc5849 import Client
from oauthlib.oauth1 import RequestValidator
from oauthlib.oauth1.rfc5849.endpoints import AccessTokenEndpoint


class AccessTokenEndpointTest(TestCase):

    def setUp(self):
        self.validator = MagicMock(wraps=RequestValidator())
        self.validator.check_client_key.return_value = True
        self.validator.check_request_token.return_value = True
        self.validator.check_verifier.return_value = True
        self.validator.allowed_signature_methods = ['HMAC-SHA1']
        self.validator.get_client_secret.return_value = 'bar'
        self.validator.get_request_token_secret.return_value = 'secret'
        self.validator.get_realms.return_value = ['foo']
        self.validator.timestamp_lifetime = 600
        self.validator.validate_client_key.return_value = True
        self.validator.validate_request_token.return_value = True
        self.validator.validate_verifier.return_value = True
        self.validator.validate_timestamp_and_nonce.return_value = True
        self.validator.invalidate_request_token.return_value = True
        self.validator.dummy_client = 'dummy'
        self.validator.dummy_secret = 'dummy'
        self.validator.dummy_request_token = 'dummy'
        self.validator.save_access_token = MagicMock()
        self.endpoint = AccessTokenEndpoint(self.validator)
        self.client = Client('foo',
                client_secret='bar',
                resource_owner_key='token',
                resource_owner_secret='secret',
                verifier='verfier')
        self.uri, self.headers, self.body = self.client.sign(
                'https://i.b/access_token')

    def test_check_request_token(self):
        self.validator.check_request_token.return_value = False
        h, b, s = self.endpoint.create_access_token_response(
                self.uri, headers=self.headers)
        self.assertEqual(s, 400)
        self.assertIn('invalid_request', b)

    def test_check_verifier(self):
        self.validator.check_verifier.return_value = False
        h, b, s = self.endpoint.create_access_token_response(
                self.uri, headers=self.headers)
        self.assertEqual(s, 400)
        self.assertIn('invalid_request', b)

    def test_validate_client_key(self):
        self.validator.validate_client_key.return_value = False
        h, b, s = self.endpoint.create_access_token_response(
                self.uri, headers=self.headers)
        self.assertEqual(s, 401)

    def test_validate_request_token(self):
        self.validator.validate_request_token.return_value = False
        h, b, s = self.endpoint.create_access_token_response(
                self.uri, headers=self.headers)
        self.assertEqual(s, 401)

    def test_validate_verifier(self):
        self.validator.validate_verifier.return_value = False
        h, b, s = self.endpoint.create_access_token_response(
                self.uri, headers=self.headers)
        self.assertEqual(s, 401)

    def test_validate_signature(self):
        client = Client('foo',
                resource_owner_key='token',
                resource_owner_secret='secret',
                verifier='verfier')
        _, headers, _ = client.sign(self.uri + '/extra')
        h, b, s = self.endpoint.create_access_token_response(
                self.uri, headers=headers)
        self.assertEqual(s, 401)

    def test_valid_request(self):
        h, b, s = self.endpoint.create_access_token_response(
                self.uri, headers=self.headers)
        self.assertEqual(s, 200)
        self.assertIn('oauth_token', b)
        self.validator.validate_timestamp_and_nonce.assert_called_once_with(
             self.client.client_key, ANY, ANY, ANY,
             request_token=self.client.resource_owner_key)
        self.validator.invalidate_request_token.assert_called_once_with(
                self.client.client_key, self.client.resource_owner_key, ANY)

