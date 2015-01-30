# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from mock import patch

from oauthlib.oauth2 import LegacyApplicationClient

from ....unittest import TestCase


@patch('time.time', new=lambda: 1000)
class LegacyApplicationClientTest(TestCase):

    client_id = "someclientid"
    scope = ["/profile"]
    kwargs = {
        "some": "providers",
        "require": "extra arguments"
    }

    username = "foo"
    password = "bar"
    body = "not=empty"

    body_up = "not=empty&grant_type=password&username=%s&password=%s" % (username, password)
    body_kwargs = body_up + "&some=providers&require=extra+arguments"

    token_json = ('{   "access_token":"2YotnFZFEjr1zCsicMWpAA",'
                  '    "token_type":"example",'
                  '    "expires_in":3600,'
                  '    "scope":"/profile",'
                  '    "refresh_token":"tGzv3JOkF0XG5Qx2TlKWIA",'
                  '    "example_parameter":"example_value"}')
    token = {
        "access_token": "2YotnFZFEjr1zCsicMWpAA",
        "token_type": "example",
        "expires_in": 3600,
        "expires_at": 4600,
        "scope": scope,
        "refresh_token": "tGzv3JOkF0XG5Qx2TlKWIA",
        "example_parameter": "example_value"
    }

    def test_request_body(self):
        client = LegacyApplicationClient(self.client_id)

        # Basic, no extra arguments
        body = client.prepare_request_body(self.username, self.password,
                body=self.body)
        self.assertFormBodyEqual(body, self.body_up)

        # With extra parameters
        body = client.prepare_request_body(self.username, self.password,
                body=self.body, **self.kwargs)
        self.assertFormBodyEqual(body, self.body_kwargs)

    def test_parse_token_response(self):
        client = LegacyApplicationClient(self.client_id)

        # Parse code and state
        response = client.parse_request_body_response(self.token_json, scope=self.scope)
        self.assertEqual(response, self.token)
        self.assertEqual(client.access_token, response.get("access_token"))
        self.assertEqual(client.refresh_token, response.get("refresh_token"))
        self.assertEqual(client.token_type, response.get("token_type"))

        # Mismatching state
        self.assertRaises(Warning, client.parse_request_body_response, self.token_json, scope="invalid")
