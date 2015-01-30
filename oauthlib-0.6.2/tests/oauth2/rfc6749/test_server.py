# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from ...unittest import TestCase
import Crypto.PublicKey.RSA as RSA
import json
import jwt
import mock

from oauthlib import common
from oauthlib.oauth2.rfc6749.endpoints import Server
from oauthlib.oauth2.rfc6749.endpoints.authorization import AuthorizationEndpoint
from oauthlib.oauth2.rfc6749.endpoints.token import TokenEndpoint
from oauthlib.oauth2.rfc6749.endpoints.resource import ResourceEndpoint
from oauthlib.oauth2.rfc6749.grant_types import AuthorizationCodeGrant
from oauthlib.oauth2.rfc6749.grant_types import ImplicitGrant
from oauthlib.oauth2.rfc6749.grant_types import ResourceOwnerPasswordCredentialsGrant
from oauthlib.oauth2.rfc6749.grant_types import ClientCredentialsGrant
from oauthlib.oauth2.rfc6749 import tokens, errors


class AuthorizationEndpointTest(TestCase):

    def setUp(self):
        self.mock_validator = mock.MagicMock()
        self.addCleanup(setattr, self, 'mock_validator', mock.MagicMock())
        auth_code = AuthorizationCodeGrant(
                request_validator=self.mock_validator)
        auth_code.save_authorization_code = mock.MagicMock()
        implicit = ImplicitGrant(
                request_validator=self.mock_validator)
        implicit.save_token = mock.MagicMock()
        response_types = {
                'code': auth_code,
                'token': implicit,
        }
        self.expires_in = 1800
        token = tokens.BearerToken(self.mock_validator,
                expires_in=self.expires_in)
        self.endpoint = AuthorizationEndpoint(
                default_response_type='code',
                default_token_type=token,
                response_types=response_types)

    @mock.patch('oauthlib.common.generate_token', new=lambda: 'abc')
    def test_authorization_grant(self):
        uri = 'http://i.b/l?response_type=code&client_id=me&scope=all+of+them&state=xyz'
        uri += '&redirect_uri=http%3A%2F%2Fback.to%2Fme'
        headers, body, status_code = self.endpoint.create_authorization_response(
                uri, scopes=['all', 'of', 'them'])
        self.assertIn('Location', headers)
        self.assertURLEqual(headers['Location'], 'http://back.to/me?code=abc&state=xyz')

    @mock.patch('oauthlib.common.generate_token', new=lambda: 'abc')
    def test_implicit_grant(self):
        uri = 'http://i.b/l?response_type=token&client_id=me&scope=all+of+them&state=xyz'
        uri += '&redirect_uri=http%3A%2F%2Fback.to%2Fme'
        headers, body, status_code = self.endpoint.create_authorization_response(
                uri, scopes=['all', 'of', 'them'])
        self.assertIn('Location', headers)
        self.assertURLEqual(headers['Location'], 'http://back.to/me#access_token=abc&expires_in=' + str(self.expires_in) + '&token_type=Bearer&state=xyz&scope=all+of+them', parse_fragment=True)

    def test_missing_type(self):
        uri = 'http://i.b/l?client_id=me&scope=all+of+them'
        uri += '&redirect_uri=http%3A%2F%2Fback.to%2Fme'
        self.mock_validator.validate_request = mock.MagicMock(
                side_effect=errors.InvalidRequestError())
        headers, body, status_code = self.endpoint.create_authorization_response(
                uri, scopes=['all', 'of', 'them'])
        self.assertIn('Location', headers)
        self.assertURLEqual(headers['Location'], 'http://back.to/me?error=invalid_request&error_description=Missing+response_type+parameter.')

    def test_invalid_type(self):
        uri = 'http://i.b/l?response_type=invalid&client_id=me&scope=all+of+them'
        uri += '&redirect_uri=http%3A%2F%2Fback.to%2Fme'
        self.mock_validator.validate_request = mock.MagicMock(
                side_effect=errors.UnsupportedResponseTypeError())
        headers, body, status_code = self.endpoint.create_authorization_response(
                uri, scopes=['all', 'of', 'them'])
        self.assertIn('Location', headers)
        self.assertURLEqual(headers['Location'], 'http://back.to/me?error=unsupported_response_type')


class TokenEndpointTest(TestCase):

    def setUp(self):
        def set_user(request):
            request.user = mock.MagicMock()
            request.client = mock.MagicMock()
            request.client.client_id = 'mocked_client_id'
            return True

        self.mock_validator = mock.MagicMock()
        self.mock_validator.authenticate_client.side_effect = set_user
        self.addCleanup(setattr, self, 'mock_validator', mock.MagicMock())
        auth_code = AuthorizationCodeGrant(
                request_validator=self.mock_validator)
        password = ResourceOwnerPasswordCredentialsGrant(
                request_validator=self.mock_validator)
        client = ClientCredentialsGrant(
                request_validator=self.mock_validator)
        supported_types = {
                'authorization_code': auth_code,
                'password': password,
                'client_credentials': client,
        }
        self.expires_in = 1800
        token = tokens.BearerToken(self.mock_validator,
                expires_in=self.expires_in)
        self.endpoint = TokenEndpoint('authorization_code',
                default_token_type=token, grant_types=supported_types)

    @mock.patch('oauthlib.common.generate_token', new=lambda: 'abc')
    def test_authorization_grant(self):
        body = 'grant_type=authorization_code&code=abc&scope=all+of+them&state=xyz'
        headers, body, status_code = self.endpoint.create_token_response(
                '', body=body)
        token = {
            'token_type': 'Bearer',
            'expires_in': self.expires_in,
            'access_token': 'abc',
            'refresh_token': 'abc',
            'state': 'xyz'
        }
        self.assertEqual(json.loads(body), token)

    @mock.patch('oauthlib.common.generate_token', new=lambda: 'abc')
    def test_password_grant(self):
        body = 'grant_type=password&username=a&password=hello&scope=all+of+them'
        headers, body, status_code = self.endpoint.create_token_response(
                '', body=body)
        token = {
            'token_type': 'Bearer',
            'expires_in': self.expires_in,
            'access_token': 'abc',
            'refresh_token': 'abc',
            'scope': 'all of them',
        }
        self.assertEqual(json.loads(body), token)

    @mock.patch('oauthlib.common.generate_token', new=lambda: 'abc')
    def test_client_grant(self):
        body = 'grant_type=client_credentials&scope=all+of+them'
        headers, body, status_code = self.endpoint.create_token_response(
                '', body=body)
        token = {
            'token_type': 'Bearer',
            'expires_in': self.expires_in,
            'access_token': 'abc',
            'scope': 'all of them',
        }
        self.assertEqual(json.loads(body), token)

    def test_missing_type(self):
        _, body, _ = self.endpoint.create_token_response('', body='')
        token = {'error': 'unsupported_grant_type'}
        self.assertEqual(json.loads(body), token)

    def test_invalid_type(self):
        body = 'grant_type=invalid'
        _, body, _ = self.endpoint.create_token_response('', body=body)
        token = {'error': 'unsupported_grant_type'}
        self.assertEqual(json.loads(body), token)


class SignedTokenEndpointTest(TestCase):

    def setUp(self):
        self.expires_in = 1800

        def set_user(request):
            request.user = mock.MagicMock()
            request.client = mock.MagicMock()
            request.client.client_id = 'mocked_client_id'
            return True

        self.mock_validator = mock.MagicMock()
        self.mock_validator.authenticate_client.side_effect = set_user
        self.addCleanup(setattr, self, 'mock_validator', mock.MagicMock())

        self.private_pem = (
            "-----BEGIN RSA PRIVATE KEY-----\n"
            "MIIEpAIBAAKCAQEA6TtDhWGwzEOWZP6m/zHoZnAPLABfetvoMPmxPGjFjtDuMRPv\n"
            "EvI1sbixZBjBtdnc5rTtHUUQ25Am3JzwPRGo5laMGbj1pPyCPxlVi9LK82HQNX0B\n"
            "YK7tZtVfDHElQA7F4v3j9d3rad4O9/n+lyGIQ0tT7yQcBm2A8FEaP0bZYCLMjwMN\n"
            "WfaVLE8eXHyv+MfpNNLI9wttLxygKYM48I3NwsFuJgOa/KuodXaAmf8pJnx8t1Wn\n"
            "nxvaYXFiUn/TxmhM/qhemPa6+0nqq+aWV5eT7xn4K/ghLgNs09v6Yge0pmPl9Oz+\n"
            "+bjJ+aKRnAmwCOY8/5U5EilAiUOeBoO9+8OXtwIDAQABAoIBAGFTTbXXMkPK4HN8\n"
            "oItVdDlrAanG7hECuz3UtFUVE3upS/xG6TjqweVLwRqYCh2ssDXFwjy4mXRGDzF4\n"
            "e/e/6s9Txlrlh/w1MtTJ6ZzTdcViR9RKOczysjZ7S5KRlI3KnGFAuWPcG2SuOWjZ\n"
            "dZfzcj1Crd/ZHajBAVFHRsCo/ATVNKbTRprFfb27xKpQ2BwH/GG781sLE3ZVNIhs\n"
            "aRRaED4622kI1E/WXws2qQMqbFKzo0m1tPbLb3Z89WgZJ/tRQwuDype1Vfm7k6oX\n"
            "xfbp3948qSe/yWKRlMoPkleji/WxPkSIalzWSAi9ziN/0Uzhe65FURgrfHL3XR1A\n"
            "B8UR+aECgYEA7NPQZV4cAikk02Hv65JgISofqV49P8MbLXk8sdnI1n7Mj10TgzU3\n"
            "lyQGDEX4hqvT0bTXe4KAOxQZx9wumu05ejfzhdtSsEm6ptGHyCdmYDQeV0C/pxDX\n"
            "JNCK8XgMku2370XG0AnyBCT7NGlgtDcNCQufcesF2gEuoKiXg6Zjo7sCgYEA/Bzs\n"
            "9fWGZZnSsMSBSW2OYbFuhF3Fne0HcxXQHipl0Rujc/9g0nccwqKGizn4fGOE7a8F\n"
            "usQgJoeGcinL7E9OEP/uQ9VX1C9RNVjIxP1O5/Guw1zjxQQYetOvbPhN2QhD1Ye7\n"
            "0TRKrW1BapcjwLpFQlVg1ZeTPOi5lv24W/wX9jUCgYEAkrMSX/hPuTbrTNVZ3L6r\n"
            "NV/2hN+PaTPeXei/pBuXwOaCqDurnpcUfFcgN/IP5LwDVd+Dq0pHTFFDNv45EFbq\n"
            "R77o5n3ZVsIVEMiyJ1XgoK8oLDw7e61+15smtjT69Piz+09pu+ytMcwGn4y3Dmsb\n"
            "dALzHYnL8iLRU0ubrz0ec4kCgYAJiVKRTzNBPptQom49h85d9ac3jJCAE8o3WTjh\n"
            "Gzt0uHXrWlqgO280EY/DTnMOyXjqwLcXxHlu26uDP/99tdY/IF8z46sJ1KxetzgI\n"
            "84f7kBHLRAU9m5UNeFpnZdEUB5MBTbwWAsNcYgiabpMkpCcghjg+fBhOsoLqqjhC\n"
            "CnwhjQKBgQDkv0QTdyBU84TE8J0XY3eLQwXbrvG2yD5A2ntN3PyxGEneX5WTJGMZ\n"
            "xJxwaFYQiDS3b9E7b8Q5dg8qa5Y1+epdhx3cuQAWPm+AoHKshDfbRve4txBDQAqh\n"
            "c6MxSWgsa+2Ld5SWSNbGtpPcmEM3Fl5ttMCNCKtNc0UE16oHwaPAIw==\n"
            "-----END RSA PRIVATE KEY-----"
        )

        signed_token = tokens.signed_token_generator(self.private_pem,
                                                     user_id=123)
        self.endpoint = Server(
            self.mock_validator,
            token_expires_in=self.expires_in,
            token_generator=signed_token,
            refresh_token_generator=tokens.random_token_generator
        )

    @mock.patch('oauthlib.common.generate_token', new=lambda: 'abc')
    def test_authorization_grant(self):
        body = 'grant_type=authorization_code&code=abc&scope=all+of+them&state=xyz'
        headers, body, status_code = self.endpoint.create_token_response(
                '', body=body)
        body = json.loads(body)
        token = {
            'token_type': 'Bearer',
            'expires_in': self.expires_in,
            'access_token': body['access_token'],
            'refresh_token': 'abc',
            'state': 'xyz'
        }
        self.assertEqual(body, token)

    @mock.patch('oauthlib.common.generate_token', new=lambda: 'abc')
    def test_password_grant(self):
        body = 'grant_type=password&username=a&password=hello&scope=all+of+them'
        headers, body, status_code = self.endpoint.create_token_response(
                '', body=body)
        body = json.loads(body)
        token = {
            'token_type': 'Bearer',
            'expires_in': self.expires_in,
            'access_token': body['access_token'],
            'refresh_token': 'abc',
            'scope': 'all of them',
        }
        self.assertEqual(body, token)

    @mock.patch('oauthlib.common.generate_token', new=lambda: 'abc')
    def test_scopes_and_user_id_stored_in_access_token(self):
        body = 'grant_type=password&username=a&password=hello&scope=all+of+them'
        headers, body, status_code = self.endpoint.create_token_response(
                '', body=body)

        access_token = json.loads(body)['access_token']

        claims = common.verify_signed_token(self.private_pem, access_token)

        self.assertEqual(claims['scope'], 'all of them')
        self.assertEqual(claims['user_id'], 123)

    @mock.patch('oauthlib.common.generate_token', new=lambda: 'abc')
    def test_client_grant(self):
        body = 'grant_type=client_credentials&scope=all+of+them'
        headers, body, status_code = self.endpoint.create_token_response(
                '', body=body)
        body = json.loads(body)
        token = {
            'token_type': 'Bearer',
            'expires_in': self.expires_in,
            'access_token': body['access_token'],
            'scope': 'all of them',
        }
        self.assertEqual(body, token)

    def test_missing_type(self):
        _, body, _ = self.endpoint.create_token_response('', body='')
        token = {'error': 'unsupported_grant_type'}
        self.assertEqual(json.loads(body), token)

    def test_invalid_type(self):
        body = 'grant_type=invalid'
        _, body, _ = self.endpoint.create_token_response('', body=body)
        token = {'error': 'unsupported_grant_type'}
        self.assertEqual(json.loads(body), token)


class ResourceEndpointTest(TestCase):

    def setUp(self):
        self.mock_validator = mock.MagicMock()
        self.addCleanup(setattr, self, 'mock_validator', mock.MagicMock())
        token = tokens.BearerToken(request_validator=self.mock_validator)
        self.endpoint = ResourceEndpoint(default_token='Bearer',
                token_types={'Bearer': token})

    def test_defaults(self):
        uri = 'http://a.b/path?some=query'
        self.mock_validator.validate_bearer_token.return_value = False
        valid, request = self.endpoint.verify_request(uri)
        self.assertFalse(valid)
        self.assertEqual(request.token_type, 'Bearer')
