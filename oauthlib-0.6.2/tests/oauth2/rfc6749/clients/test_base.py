# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from ....unittest import TestCase

import datetime
from oauthlib import common
from oauthlib.oauth2.rfc6749 import utils
from oauthlib.oauth2 import Client
from oauthlib.oauth2.rfc6749.clients import AUTH_HEADER, URI_QUERY, BODY


class ClientTest(TestCase):

    client_id = "someclientid"
    uri = "https://example.com/path?query=world"
    body = "not=empty"
    headers = {}
    access_token = "token"
    mac_key = "secret"

    bearer_query = uri + "&access_token=" + access_token
    bearer_header = {
        "Authorization": "Bearer " + access_token
    }
    bearer_body = body + "&access_token=" + access_token

    mac_00_header = {
        "Authorization": 'MAC id="' + access_token + '", nonce="0:abc123",' +
                         ' bodyhash="Yqyso8r3hR5Nm1ZFv+6AvNHrxjE=",' +
                         ' mac="0X6aACoBY0G6xgGZVJ1IeE8dF9k="'
    }
    mac_01_header = {
        "Authorization": 'MAC id="' + access_token + '", ts="123456789",' +
                          ' nonce="abc123", mac="Xuk+9oqaaKyhitkgh1CD0xrI6+s="'
    }

    def test_add_bearer_token(self):
        """Test a number of bearer token placements"""

        # Invalid token type
        client = Client(self.client_id, token_type="invalid")
        self.assertRaises(ValueError, client.add_token, self.uri)

        # Case-insensitive token type
        client = Client(self.client_id, access_token=self.access_token, token_type="bEAreR")
        uri, headers, body = client.add_token(self.uri, body=self.body,
                headers=self.headers)
        self.assertURLEqual(uri, self.uri)
        self.assertFormBodyEqual(body, self.body)
        self.assertEqual(headers, self.bearer_header)

        # Missing access token
        client = Client(self.client_id)
        self.assertRaises(ValueError, client.add_token, self.uri)

        # The default token placement, bearer in auth header
        client = Client(self.client_id, access_token=self.access_token)
        uri, headers, body = client.add_token(self.uri, body=self.body,
                headers=self.headers)
        self.assertURLEqual(uri, self.uri)
        self.assertFormBodyEqual(body, self.body)
        self.assertEqual(headers, self.bearer_header)

        # Setting default placements of tokens
        client = Client(self.client_id, access_token=self.access_token,
                default_token_placement=AUTH_HEADER)
        uri, headers, body = client.add_token(self.uri, body=self.body,
                headers=self.headers)
        self.assertURLEqual(uri, self.uri)
        self.assertFormBodyEqual(body, self.body)
        self.assertEqual(headers, self.bearer_header)

        client = Client(self.client_id, access_token=self.access_token,
                default_token_placement=URI_QUERY)
        uri, headers, body = client.add_token(self.uri, body=self.body,
                headers=self.headers)
        self.assertURLEqual(uri, self.bearer_query)
        self.assertFormBodyEqual(body, self.body)
        self.assertEqual(headers, self.headers)

        client = Client(self.client_id, access_token=self.access_token,
                default_token_placement=BODY)
        uri, headers, body = client.add_token(self.uri, body=self.body,
                headers=self.headers)
        self.assertURLEqual(uri, self.uri)
        self.assertFormBodyEqual(body, self.bearer_body)
        self.assertEqual(headers, self.headers)

        # Asking for specific placement in the add_token method
        client = Client(self.client_id, access_token=self.access_token)
        uri, headers, body = client.add_token(self.uri, body=self.body,
                headers=self.headers, token_placement=AUTH_HEADER)
        self.assertURLEqual(uri, self.uri)
        self.assertFormBodyEqual(body, self.body)
        self.assertEqual(headers, self.bearer_header)

        client = Client(self.client_id, access_token=self.access_token)
        uri, headers, body = client.add_token(self.uri, body=self.body,
                headers=self.headers, token_placement=URI_QUERY)
        self.assertURLEqual(uri, self.bearer_query)
        self.assertFormBodyEqual(body, self.body)
        self.assertEqual(headers, self.headers)

        client = Client(self.client_id, access_token=self.access_token)
        uri, headers, body = client.add_token(self.uri, body=self.body,
                headers=self.headers, token_placement=BODY)
        self.assertURLEqual(uri, self.uri)
        self.assertFormBodyEqual(body, self.bearer_body)
        self.assertEqual(headers, self.headers)

        # Invalid token placement
        client = Client(self.client_id, access_token=self.access_token)
        self.assertRaises(ValueError, client.add_token, self.uri, body=self.body,
                headers=self.headers, token_placement="invalid")

        client = Client(self.client_id, access_token=self.access_token,
                default_token_placement="invalid")
        self.assertRaises(ValueError, client.add_token, self.uri, body=self.body,
                headers=self.headers)

    def test_add_mac_token(self):
        # Missing access token
        client = Client(self.client_id, token_type="MAC")
        self.assertRaises(ValueError, client.add_token, self.uri)

        # Invalid hash algorithm
        client = Client(self.client_id, token_type="MAC",
                access_token=self.access_token, mac_key=self.mac_key,
                mac_algorithm="hmac-sha-2")
        self.assertRaises(ValueError, client.add_token, self.uri)

        orig_generate_timestamp = common.generate_timestamp
        orig_generate_nonce = common.generate_nonce
        orig_generate_age = utils.generate_age
        self.addCleanup(setattr, common, 'generage_timestamp', orig_generate_timestamp)
        self.addCleanup(setattr, common, 'generage_nonce', orig_generate_nonce)
        self.addCleanup(setattr, utils, 'generate_age', orig_generate_age)
        common.generate_timestamp = lambda: '123456789'
        common.generate_nonce = lambda: 'abc123'
        utils.generate_age = lambda *args: 0

        # Add the Authorization header (draft 00)
        client = Client(self.client_id, token_type="MAC",
                access_token=self.access_token, mac_key=self.mac_key,
                mac_algorithm="hmac-sha-1")
        uri, headers, body = client.add_token(self.uri, body=self.body,
                headers=self.headers, issue_time=datetime.datetime.now())
        self.assertEqual(uri, self.uri)
        self.assertEqual(body, self.body)
        self.assertEqual(headers, self.mac_00_header)

        # Add the Authorization header (draft 00)
        client = Client(self.client_id, token_type="MAC",
                access_token=self.access_token, mac_key=self.mac_key,
                mac_algorithm="hmac-sha-1")
        uri, headers, body = client.add_token(self.uri, body=self.body,
                headers=self.headers, draft=1)
        self.assertEqual(uri, self.uri)
        self.assertEqual(body, self.body)
        self.assertEqual(headers, self.mac_01_header)
