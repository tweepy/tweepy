from __future__ import unicode_literals, absolute_import

from mock import MagicMock, ANY
from ....unittest import TestCase

from oauthlib.oauth1.rfc5849 import Client
from oauthlib.oauth1 import RequestValidator
from oauthlib.oauth1.rfc5849.endpoints import ResourceEndpoint


class ResourceEndpointTest(TestCase):

    def setUp(self):
        self.validator = MagicMock(wraps=RequestValidator())
        self.validator.check_client_key.return_value = True
        self.validator.check_access_token.return_value = True
        self.validator.allowed_signature_methods = ['HMAC-SHA1']
        self.validator.get_client_secret.return_value = 'bar'
        self.validator.get_access_token_secret.return_value = 'secret'
        self.validator.timestamp_lifetime = 600
        self.validator.validate_client_key.return_value = True
        self.validator.validate_access_token.return_value = True
        self.validator.validate_timestamp_and_nonce.return_value = True
        self.validator.validate_realms.return_value = True
        self.validator.dummy_client = 'dummy'
        self.validator.dummy_secret = 'dummy'
        self.validator.dummy_access_token = 'dummy'
        self.endpoint = ResourceEndpoint(self.validator)
        self.client = Client('foo',
                client_secret='bar',
                resource_owner_key='token',
                resource_owner_secret='secret')
        self.uri, self.headers, self.body = self.client.sign(
                'https://i.b/protected_resource')

    def test_missing_parameters(self):
        self.validator.check_access_token.return_value = False
        v, r = self.endpoint.validate_protected_resource_request(
                self.uri)
        self.assertFalse(v)

    def test_check_access_token(self):
        self.validator.check_access_token.return_value = False
        v, r = self.endpoint.validate_protected_resource_request(
                self.uri, headers=self.headers)
        self.assertFalse(v)

    def test_validate_client_key(self):
        self.validator.validate_client_key.return_value = False
        v, r = self.endpoint.validate_protected_resource_request(
                self.uri, headers=self.headers)
        self.assertFalse(v)

    def test_validate_access_token(self):
        self.validator.validate_access_token.return_value = False
        v, r = self.endpoint.validate_protected_resource_request(
                self.uri, headers=self.headers)
        self.assertFalse(v)

    def test_validate_realms(self):
        self.validator.validate_realms.return_value = False
        v, r = self.endpoint.validate_protected_resource_request(
                self.uri, headers=self.headers)
        self.assertFalse(v)

    def test_validate_signature(self):
        client = Client('foo',
                resource_owner_key='token',
                resource_owner_secret='secret')
        _, headers, _ = client.sign(self.uri + '/extra')
        v, r = self.endpoint.validate_protected_resource_request(
                self.uri, headers=headers)
        self.assertFalse(v)

    def test_valid_request(self):
        v, r = self.endpoint.validate_protected_resource_request(
                self.uri, headers=self.headers)
        self.assertTrue(v)
        self.validator.validate_timestamp_and_nonce.assert_called_once_with(
             self.client.client_key, ANY, ANY, ANY,
             access_token=self.client.resource_owner_key)
