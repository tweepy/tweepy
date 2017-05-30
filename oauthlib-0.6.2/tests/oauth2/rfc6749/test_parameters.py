from __future__ import absolute_import, unicode_literals

from mock import patch

from ...unittest import TestCase
from oauthlib.oauth2.rfc6749.parameters import *
from oauthlib.oauth2.rfc6749.errors import *


@patch('time.time', new=lambda: 1000)
class ParameterTests(TestCase):

    state = 'xyz'
    auth_base = {
        'uri': 'https://server.example.com/authorize',
        'client_id': 's6BhdRkqt3',
        'redirect_uri': 'https://client.example.com/cb',
        'state': state,
        'scope': 'photos'
    }
    list_scope = ['list', 'of', 'scopes']

    auth_grant = {'response_type': 'code'}
    auth_grant_list_scope = {}
    auth_implicit = {'response_type': 'token', 'extra': 'extra'}
    auth_implicit_list_scope = {}

    def setUp(self):
        self.auth_grant.update(self.auth_base)
        self.auth_implicit.update(self.auth_base)
        self.auth_grant_list_scope.update(self.auth_grant)
        self.auth_grant_list_scope['scope'] = self.list_scope
        self.auth_implicit_list_scope.update(self.auth_implicit)
        self.auth_implicit_list_scope['scope'] = self.list_scope

    auth_base_uri = ('https://server.example.com/authorize?response_type={0}'
                     '&client_id=s6BhdRkqt3&redirect_uri=https%3A%2F%2F'
                     'client.example.com%2Fcb&scope={1}&state={2}{3}')

    auth_grant_uri = auth_base_uri.format('code', 'photos', state, '')
    auth_grant_uri_list_scope = auth_base_uri.format('code', 'list+of+scopes', state, '')
    auth_implicit_uri = auth_base_uri.format('token', 'photos', state, '&extra=extra')
    auth_implicit_uri_list_scope = auth_base_uri.format('token', 'list+of+scopes', state, '&extra=extra')

    grant_body = {
        'grant_type': 'authorization_code',
        'code': 'SplxlOBeZQQYbYS6WxSbIA',
        'redirect_uri': 'https://client.example.com/cb'
    }
    grant_body_scope = {'scope': 'photos'}
    grant_body_list_scope = {'scope': list_scope}
    auth_grant_body = ('grant_type=authorization_code&'
                       'code=SplxlOBeZQQYbYS6WxSbIA&'
                       'redirect_uri=https%3A%2F%2Fclient.example.com%2Fcb')
    auth_grant_body_scope = auth_grant_body + '&scope=photos'
    auth_grant_body_list_scope = auth_grant_body + '&scope=list+of+scopes'

    pwd_body = {
        'grant_type': 'password',
        'username': 'johndoe',
        'password': 'A3ddj3w'
    }
    password_body = 'grant_type=password&username=johndoe&password=A3ddj3w'

    cred_grant = {'grant_type': 'client_credentials'}
    cred_body = 'grant_type=client_credentials'

    grant_response = 'https://client.example.com/cb?code=SplxlOBeZQQYbYS6WxSbIA&state=xyz'
    grant_dict = {'code': 'SplxlOBeZQQYbYS6WxSbIA', 'state': state}

    error_nocode = 'https://client.example.com/cb?state=xyz'
    error_nostate = 'https://client.example.com/cb?code=SplxlOBeZQQYbYS6WxSbIA'
    error_wrongstate = 'https://client.example.com/cb?code=SplxlOBeZQQYbYS6WxSbIA&state=abc'
    error_response = 'https://client.example.com/cb?error=access_denied&state=xyz'

    implicit_base = 'https://example.com/cb#access_token=2YotnFZFEjr1zCsicMWpAA&scope=abc&'
    implicit_response = implicit_base + 'state={0}&token_type=example&expires_in=3600'.format(state)
    implicit_notype = implicit_base + 'state={0}&expires_in=3600'.format(state)
    implicit_wrongstate = implicit_base + 'state={0}&token_type=exampleexpires_in=3600'.format('invalid')
    implicit_nostate = implicit_base + 'token_type=example&expires_in=3600'
    implicit_notoken = 'https://example.com/cb#state=xyz&token_type=example&expires_in=3600'

    implicit_dict = {
        'access_token': '2YotnFZFEjr1zCsicMWpAA',
        'state': state,
        'token_type': 'example',
        'expires_in': '3600',
        'expires_at': 4600,
        'scope': ['abc']
    }

    json_response = ('{ "access_token": "2YotnFZFEjr1zCsicMWpAA",'
                     '  "token_type": "example",'
                     '  "expires_in": 3600,'
                     '  "refresh_token": "tGzv3JOkF0XG5Qx2TlKWIA",'
                     '  "example_parameter": "example_value",'
                     '  "scope":"abc def"}')

    json_error = '{ "error": "invalid_request" }'

    json_notoken = ('{ "token_type": "example",'
                    '  "expires_in": 3600,'
                    '  "refresh_token": "tGzv3JOkF0XG5Qx2TlKWIA",'
                    '  "example_parameter": "example_value" }')

    json_notype = ('{  "access_token": "2YotnFZFEjr1zCsicMWpAA",'
                   '   "expires_in": 3600,'
                   '   "refresh_token": "tGzv3JOkF0XG5Qx2TlKWIA",'
                   '   "example_parameter": "example_value" }')

    json_dict = {
       'access_token': '2YotnFZFEjr1zCsicMWpAA',
       'token_type': 'example',
       'expires_in': 3600,
       'expires_at': 4600,
       'refresh_token': 'tGzv3JOkF0XG5Qx2TlKWIA',
       'example_parameter': 'example_value',
       'scope': ['abc', 'def']
    }

    def test_prepare_grant_uri(self):
        """Verify correct authorization URI construction."""
        self.assertURLEqual(prepare_grant_uri(**self.auth_grant), self.auth_grant_uri)
        self.assertURLEqual(prepare_grant_uri(**self.auth_grant_list_scope), self.auth_grant_uri_list_scope)
        self.assertURLEqual(prepare_grant_uri(**self.auth_implicit), self.auth_implicit_uri)
        self.assertURLEqual(prepare_grant_uri(**self.auth_implicit_list_scope), self.auth_implicit_uri_list_scope)

    def test_prepare_token_request(self):
        """Verify correct access token request body construction."""
        self.assertFormBodyEqual(prepare_token_request(**self.grant_body), self.auth_grant_body)
        self.assertFormBodyEqual(prepare_token_request(**self.pwd_body), self.password_body)
        self.assertFormBodyEqual(prepare_token_request(**self.cred_grant), self.cred_body)

    def test_grant_response(self):
        """Verify correct parameter parsing and validation for auth code responses."""
        params = parse_authorization_code_response(self.grant_response)
        self.assertEqual(params, self.grant_dict)
        params = parse_authorization_code_response(self.grant_response, state=self.state)
        self.assertEqual(params, self.grant_dict)

        self.assertRaises(MissingCodeError, parse_authorization_code_response,
                self.error_nocode)
        self.assertRaises(MissingCodeError, parse_authorization_code_response,
                self.error_response)
        self.assertRaises(MismatchingStateError, parse_authorization_code_response,
                self.error_nostate, state=self.state)
        self.assertRaises(MismatchingStateError, parse_authorization_code_response,
                self.error_wrongstate, state=self.state)

    def test_implicit_token_response(self):
        """Verify correct parameter parsing and validation for implicit responses."""
        self.assertEqual(parse_implicit_response(self.implicit_response),
                self.implicit_dict)
        self.assertRaises(MissingTokenError, parse_implicit_response,
                self.implicit_notoken)
        self.assertRaises(MissingTokenTypeError, parse_implicit_response,
                self.implicit_notype)
        self.assertRaises(ValueError, parse_implicit_response,
                self.implicit_nostate, state=self.state)
        self.assertRaises(ValueError, parse_implicit_response,
                self.implicit_wrongstate, state=self.state)

    def test_json_token_response(self):
        """Verify correct parameter parsing and validation for token responses. """
        self.assertEqual(parse_token_response(self.json_response), self.json_dict)
        self.assertRaises(InvalidRequestError, parse_token_response, self.json_error)
        self.assertRaises(MissingTokenError, parse_token_response, self.json_notoken)
        self.assertRaises(Warning, parse_token_response, self.json_response, scope='aaa')
