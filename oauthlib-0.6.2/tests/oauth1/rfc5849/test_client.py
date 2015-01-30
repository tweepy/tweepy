# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from oauthlib.common import Request
from oauthlib.oauth1 import SIGNATURE_RSA, SIGNATURE_PLAINTEXT
from oauthlib.oauth1 import SIGNATURE_TYPE_BODY, SIGNATURE_TYPE_QUERY
from oauthlib.oauth1.rfc5849 import Client, bytes_type
from ...unittest import TestCase


class ClientRealmTests(TestCase):

    def test_client_no_realm(self):
        client = Client("client-key")
        uri, header, body = client.sign("http://example-uri")
        self.assertTrue(
            header["Authorization"].startswith('OAuth oauth_nonce='))

    def test_client_realm_sign_with_default_realm(self):
        client = Client("client-key", realm="moo-realm")
        self.assertEqual(client.realm, "moo-realm")
        uri, header, body = client.sign("http://example-uri")
        self.assertTrue(
            header["Authorization"].startswith('OAuth realm="moo-realm",'))

    def test_client_realm_sign_with_additional_realm(self):
        client = Client("client-key", realm="moo-realm")
        uri, header, body = client.sign("http://example-uri", realm="baa-realm")
        self.assertTrue(
            header["Authorization"].startswith('OAuth realm="baa-realm",'))
        # make sure sign() does not override the default realm
        self.assertEqual(client.realm, "moo-realm")


class ClientConstructorTests(TestCase):

    def test_convert_to_unicode_resource_owner(self):
        client = Client('client-key',
                        resource_owner_key=b'owner key')
        self.assertFalse(isinstance(client.resource_owner_key, bytes_type))
        self.assertEqual(client.resource_owner_key, 'owner key')

    def test_give_explicit_timestamp(self):
        client = Client('client-key', timestamp='1')
        params = dict(client.get_oauth_params(Request('http://example.com')))
        self.assertEqual(params['oauth_timestamp'], '1')

    def test_give_explicit_nonce(self):
        client = Client('client-key', nonce='1')
        params = dict(client.get_oauth_params(Request('http://example.com')))
        self.assertEqual(params['oauth_nonce'], '1')

    def test_decoding(self):
        client = Client('client_key', decoding='utf-8')
        uri, headers, body = client.sign('http://a.b/path?query',
                http_method='POST', body='a=b',
                headers={'Content-Type': 'application/x-www-form-urlencoded'})
        self.assertIsInstance(uri, bytes_type)
        self.assertIsInstance(body, bytes_type)
        for k, v in headers.items():
            self.assertIsInstance(k, bytes_type)
            self.assertIsInstance(v, bytes_type)


class SignatureMethodTest(TestCase):

    def test_rsa_method(self):
        private_key = (
            "-----BEGIN RSA PRIVATE KEY-----\nMIICXgIBAAKBgQDk1/bxy"
            "S8Q8jiheHeYYp/4rEKJopeQRRKKpZI4s5i+UPwVpupG\nAlwXWfzXw"
            "SMaKPAoKJNdu7tqKRniqst5uoHXw98gj0x7zamu0Ck1LtQ4c7pFMVa"
            "h\n5IYGhBi2E9ycNS329W27nJPWNCbESTu7snVlG8V8mfvGGg3xNjT"
            "MO7IdrwIDAQAB\nAoGBAOQ2KuH8S5+OrsL4K+wfjoCi6MfxCUyqVU9"
            "GxocdM1m30WyWRFMEz2nKJ8fR\np3vTD4w8yplTOhcoXdQZl0kRoaD"
            "zrcYkm2VvJtQRrX7dKFT8dR8D/Tr7dNQLOXfC\nDY6xveQczE7qt7V"
            "k7lp4FqmxBsaaEuokt78pOOjywZoInjZhAkEA9wz3zoZNT0/i\nrf6"
            "qv2qTIeieUB035N3dyw6f1BGSWYaXSuerDCD/J1qZbAPKKhyHZbVaw"
            "Ft3UMhe\n542UftBaxQJBAO0iJy1I8GQjGnS7B3yvyH3CcLYGy296+"
            "XO/2xKp/d/ty1OIeovx\nC60pLNwuFNF3z9d2GVQAdoQ89hUkOtjZL"
            "eMCQQD0JO6oPHUeUjYT+T7ImAv7UKVT\nSuy30sKjLzqoGw1kR+wv7"
            "C5PeDRvscs4wa4CW9s6mjSrMDkDrmCLuJDtmf55AkEA\nkmaMg2PNr"
            "jUR51F0zOEFycaaqXbGcFwe1/xx9zLmHzMDXd4bsnwt9kk+fe0hQzV"
            "S\nJzatanQit3+feev1PN3QewJAWv4RZeavEUhKv+kLe95Yd0su7lT"
            "LVduVgh4v5yLT\nGa6FHdjGPcfajt+nrpB1n8UQBEH9ZxniokR/IPv"
            "dMlxqXA==\n-----END RSA PRIVATE KEY-----"
        )
        client = Client('client_key', signature_method=SIGNATURE_RSA,
            rsa_key=private_key, timestamp='1234567890', nonce='abc')
        u, h, b = client.sign('http://example.com')
        correct = ('OAuth oauth_nonce="abc", oauth_timestamp="1234567890", '
                   'oauth_version="1.0", oauth_signature_method="RSA-SHA1", '
                   'oauth_consumer_key="client_key", '
                   'oauth_signature="ktvzkUhtrIawBcq21DRJrAyysTc3E1Zq5GdGu8EzH'
                   'OtbeaCmOBDLGHAcqlm92mj7xp5E1Z6i2vbExPimYAJL7FzkLnkRE5YEJR4'
                   'rNtIgAf1OZbYsIUmmBO%2BCLuStuu5Lg3tAluwC7XkkgoXCBaRKT1mUXzP'
                   'HJILzZ8iFOvS6w5E%3D"')
        self.assertEqual(h['Authorization'], correct)


    def test_plaintext_method(self):
        client = Client('client_key',
                        signature_method=SIGNATURE_PLAINTEXT,
                        timestamp='1234567890',
                        nonce='abc',
                        client_secret='foo',
                        resource_owner_secret='bar')
        u, h, b = client.sign('http://example.com')
        correct = ('OAuth oauth_nonce="abc", oauth_timestamp="1234567890", '
                   'oauth_version="1.0", oauth_signature_method="PLAINTEXT", '
                   'oauth_consumer_key="client_key", '
                   'oauth_signature="foo%26bar"')
        self.assertEqual(h['Authorization'], correct)

    def test_invalid_method(self):
        client = Client('client_key', signature_method='invalid')
        self.assertRaises(ValueError, client.sign, 'http://example.com')


    def test_register_method(self):
        Client.register_signature_method('PIZZA',
            lambda base_string, client: 'PIZZA')

        self.assertTrue('PIZZA' in Client.SIGNATURE_METHODS)

        client = Client('client_key', signature_method='PIZZA',
            timestamp='1234567890', nonce='abc')

        u, h, b = client.sign('http://example.com')

        self.assertEquals(h['Authorization'], (
            'OAuth oauth_nonce="abc", oauth_timestamp="1234567890", '
            'oauth_version="1.0", oauth_signature_method="PIZZA", '
            'oauth_consumer_key="client_key", '
            'oauth_signature="PIZZA"'
        ))


class SignatureTypeTest(TestCase):

    def test_params_in_body(self):
        client = Client('client_key', signature_type=SIGNATURE_TYPE_BODY,
                timestamp='1378988215', nonce='14205877133089081931378988215')
        _, h, b = client.sign('http://i.b/path', http_method='POST', body='a=b',
                headers={'Content-Type': 'application/x-www-form-urlencoded'})
        self.assertEqual(h['Content-Type'], 'application/x-www-form-urlencoded')
        correct = ('a=b&oauth_nonce=14205877133089081931378988215&'
                   'oauth_timestamp=1378988215&'
                   'oauth_version=1.0&'
                   'oauth_signature_method=HMAC-SHA1&'
                   'oauth_consumer_key=client_key&'
                   'oauth_signature=2JAQomgbShqoscqKWBiYQZwWq94%3D')
        self.assertEqual(b, correct)

    def test_params_in_query(self):
        client = Client('client_key', signature_type=SIGNATURE_TYPE_QUERY,
                timestamp='1378988215', nonce='14205877133089081931378988215')
        u, _, _ = client.sign('http://i.b/path', http_method='POST')
        correct = ('http://i.b/path?oauth_nonce=14205877133089081931378988215&'
                   'oauth_timestamp=1378988215&'
                   'oauth_version=1.0&'
                   'oauth_signature_method=HMAC-SHA1&'
                   'oauth_consumer_key=client_key&'
                   'oauth_signature=08G5Snvw%2BgDAzBF%2BCmT5KqlrPKo%3D')
        self.assertEqual(u, correct)

    def test_invalid_signature_type(self):
        client = Client('client_key', signature_type='invalid')
        self.assertRaises(ValueError, client.sign, 'http://i.b/path')


class SigningTest(TestCase):

    def test_case_insensitive_headers(self):
        client = Client('client_key')
        # Uppercase
        _, h, _ = client.sign('http://i.b/path', http_method='POST', body='',
                headers={'Content-Type': 'application/x-www-form-urlencoded'})
        self.assertEqual(h['Content-Type'], 'application/x-www-form-urlencoded')

        # Lowercase
        _, h, _ = client.sign('http://i.b/path', http_method='POST', body='',
                headers={'content-type': 'application/x-www-form-urlencoded'})
        self.assertEqual(h['content-type'], 'application/x-www-form-urlencoded')

        # Capitalized
        _, h, _ = client.sign('http://i.b/path', http_method='POST', body='',
                headers={'Content-type': 'application/x-www-form-urlencoded'})
        self.assertEqual(h['Content-type'], 'application/x-www-form-urlencoded')

        # Random
        _, h, _ = client.sign('http://i.b/path', http_method='POST', body='',
                headers={'conTent-tYpe': 'application/x-www-form-urlencoded'})
        self.assertEqual(h['conTent-tYpe'], 'application/x-www-form-urlencoded')

    def test_sign_no_body(self):
        client = Client('client_key', decoding='utf-8')
        self.assertRaises(ValueError, client.sign, 'http://i.b/path',
                http_method='POST', body=None,
                headers={'Content-Type': 'application/x-www-form-urlencoded'})

    def test_sign_body(self):
        client = Client('client_key')
        _, h, b = client.sign('http://i.b/path', http_method='POST', body='',
                headers={'Content-Type': 'application/x-www-form-urlencoded'})
        self.assertEqual(h['Content-Type'], 'application/x-www-form-urlencoded')

    def test_sign_get_with_body(self):
        client = Client('client_key')
        for method in ('GET', 'HEAD'):
            self.assertRaises(ValueError, client.sign, 'http://a.b/path?query',
                    http_method=method, body='a=b',
                    headers={
                        'Content-Type': 'application/x-www-form-urlencoded'
                    })

    def test_sign_unicode(self):
        client = Client('client_key', nonce='abc', timestamp='abc')
        _, h, b = client.sign('http://i.b/path', http_method='POST',
                body='status=%E5%95%A6%E5%95%A6',
                headers={'Content-Type': 'application/x-www-form-urlencoded'})
        self.assertEqual(b, 'status=%E5%95%A6%E5%95%A6')
        self.assertIn('oauth_signature="yrtSqp88m%2Fc5UDaucI8BXK4oEtk%3D"', h['Authorization'])
        _, h, b = client.sign('http://i.b/path', http_method='POST',
                body='status=%C3%A6%C3%A5%C3%B8',
                headers={'Content-Type': 'application/x-www-form-urlencoded'})
        self.assertEqual(b, 'status=%C3%A6%C3%A5%C3%B8')
        self.assertIn('oauth_signature="oG5t3Eg%2FXO5FfQgUUlTtUeeZzvk%3D"', h['Authorization'])
