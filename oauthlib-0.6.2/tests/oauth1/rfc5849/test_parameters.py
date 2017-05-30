# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from oauthlib.common import urlencode
from oauthlib.oauth1.rfc5849.parameters import (_append_params, prepare_headers,
    prepare_form_encoded_body, prepare_request_uri_query)
from ...unittest import TestCase


class ParameterTests(TestCase):
    auth_only_params = [
        ('oauth_consumer_key', "9djdj82h48djs9d2"),
        ('oauth_token', "kkk9d7dh3k39sjv7"),
        ('oauth_signature_method', "HMAC-SHA1"),
        ('oauth_timestamp', "137131201"),
        ('oauth_nonce', "7d8f3e4a"),
        ('oauth_signature', "bYT5CMsGcbgUdFHObYMEfcx6bsw=")
    ]
    auth_and_data = list(auth_only_params)
    auth_and_data.append(('data_param_foo', 'foo'))
    auth_and_data.append(('data_param_1', '1'))
    realm = 'testrealm'
    norealm_authorization_header = ' '.join((
        'OAuth',
        'oauth_consumer_key="9djdj82h48djs9d2",',
        'oauth_token="kkk9d7dh3k39sjv7",',
        'oauth_signature_method="HMAC-SHA1",',
        'oauth_timestamp="137131201",',
        'oauth_nonce="7d8f3e4a",',
        'oauth_signature="bYT5CMsGcbgUdFHObYMEfcx6bsw%3D"',
    ))
    withrealm_authorization_header = ' '.join((
        'OAuth',
        'realm="testrealm",',
        'oauth_consumer_key="9djdj82h48djs9d2",',
        'oauth_token="kkk9d7dh3k39sjv7",',
        'oauth_signature_method="HMAC-SHA1",',
        'oauth_timestamp="137131201",',
        'oauth_nonce="7d8f3e4a",',
        'oauth_signature="bYT5CMsGcbgUdFHObYMEfcx6bsw%3D"',
    ))

    def test_append_params(self):
        unordered_1 = [
            ('oauth_foo', 'foo'),
            ('lala', 123),
            ('oauth_baz', 'baz'),
            ('oauth_bar', 'bar'), ]
        unordered_2 = [
            ('teehee', 456),
            ('oauth_quux', 'quux'), ]
        expected = [
            ('teehee', 456),
            ('lala', 123),
            ('oauth_quux', 'quux'),
            ('oauth_foo', 'foo'),
            ('oauth_baz', 'baz'),
            ('oauth_bar', 'bar'), ]
        self.assertEqual(_append_params(unordered_1, unordered_2), expected)

    def test_prepare_headers(self):
        self.assertEqual(
            prepare_headers(self.auth_only_params, {}),
            {'Authorization': self.norealm_authorization_header})
        self.assertEqual(
            prepare_headers(self.auth_only_params, {}, realm=self.realm),
            {'Authorization': self.withrealm_authorization_header})

    def test_prepare_headers_ignore_data(self):
        self.assertEqual(
            prepare_headers(self.auth_and_data, {}),
            {'Authorization': self.norealm_authorization_header})
        self.assertEqual(
            prepare_headers(self.auth_and_data, {}, realm=self.realm),
            {'Authorization': self.withrealm_authorization_header})

    def test_prepare_form_encoded_body(self):
        existing_body = ''
        form_encoded_body = 'data_param_foo=foo&data_param_1=1&oauth_consumer_key=9djdj82h48djs9d2&oauth_token=kkk9d7dh3k39sjv7&oauth_signature_method=HMAC-SHA1&oauth_timestamp=137131201&oauth_nonce=7d8f3e4a&oauth_signature=bYT5CMsGcbgUdFHObYMEfcx6bsw%3D'
        self.assertEqual(
            urlencode(prepare_form_encoded_body(self.auth_and_data, existing_body)),
            form_encoded_body)

    def test_prepare_request_uri_query(self):
        url = 'http://notarealdomain.com/foo/bar/baz?some=args&go=here'
        request_uri_query = 'http://notarealdomain.com/foo/bar/baz?some=args&go=here&data_param_foo=foo&data_param_1=1&oauth_consumer_key=9djdj82h48djs9d2&oauth_token=kkk9d7dh3k39sjv7&oauth_signature_method=HMAC-SHA1&oauth_timestamp=137131201&oauth_nonce=7d8f3e4a&oauth_signature=bYT5CMsGcbgUdFHObYMEfcx6bsw%3D'
        self.assertEqual(
            prepare_request_uri_query(self.auth_and_data, url),
            request_uri_query)
