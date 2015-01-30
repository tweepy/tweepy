# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote

from oauthlib.oauth1.rfc5849.signature import collect_parameters
from oauthlib.oauth1.rfc5849.signature import construct_base_string
from oauthlib.oauth1.rfc5849.signature import normalize_base_string_uri
from oauthlib.oauth1.rfc5849.signature import normalize_parameters
from oauthlib.oauth1.rfc5849.signature import sign_hmac_sha1, sign_hmac_sha1_with_client
from oauthlib.oauth1.rfc5849.signature import sign_rsa_sha1, sign_rsa_sha1_with_client
from oauthlib.oauth1.rfc5849.signature import sign_plaintext, sign_plaintext_with_client
from oauthlib.common import unicode_type
from ...unittest import TestCase


class SignatureTests(TestCase):
    class MockClient(dict):
        def __getattr__(self, name):
            return self[name]

        def __setattr__(self, name, value):
            self[name] = value

        def decode(self):
            for k, v in self.items():
                self[k] = v.decode('utf-8')

    uri_query = "b5=%3D%253D&a3=a&c%40=&a2=r%20b&c2=&a3=2+q"
    authorization_header = """OAuth realm="Example",
    oauth_consumer_key="9djdj82h48djs9d2",
    oauth_token="kkk9d7dh3k39sjv7",
    oauth_signature_method="HMAC-SHA1",
    oauth_timestamp="137131201",
    oauth_nonce="7d8f3e4a",
    oauth_signature="djosJKDKJSD8743243%2Fjdk33klY%3D" """.strip()
    body = "content=This+is+being+the+body+of+things"
    http_method = b"post"
    base_string_url = quote("http://example.com/request?b5=%3D%253D"
                            "&a3=a&c%40=&a2=r%20b").encode('utf-8')
    normalized_encoded_request_parameters = quote(
        'OAuth realm="Example",'
        'oauth_consumer_key="9djdj82h48djs9d2",'
        'oauth_token="kkk9d7dh3k39sjv7",'
        'oauth_signature_method="HMAC-SHA1",'
        'oauth_timestamp="137131201",'
        'oauth_nonce="7d8f3e4a",'
        'oauth_signature="bYT5CMsGcbgUdFHObYMEfcx6bsw%3D"'
    ).encode('utf-8')
    client_secret = b"ECrDNoq1VYzzzzzzzzzyAK7TwZNtPnkqatqZZZZ"
    resource_owner_secret = b"just-a-string    asdasd"
    control_base_string = (
        "POST&http%253A%2F%2Fexample.com%2Frequest%253F"
        "b5%253D%25253D%2525253D%2526"
        "a3%253D"
        "a%2526"
        "c%252540%253D%2526"
        "a2%253D"
        "r%252520b&"
        "OAuth%2520realm%253D%2522Example%2522%252C"
        "oauth_consumer_key%253D%25229djdj82h48djs9d2%2522%252C"
        "oauth_token%253D%2522kkk9d7dh3k39sjv7%2522%252C"
        "oauth_signature_method%253D%2522HMAC-SHA1%2522%252C"
        "oauth_timestamp%253D%2522137131201%2522%252C"
        "oauth_nonce%253D%25227d8f3e4a%2522%252C"
        "oauth_signature%253D%2522bYT5CMsGcbgUdFHObYMEfcx6bsw%25253D%2522")

    def setUp(self):
        self.client = self.MockClient(
            client_secret = self.client_secret,
            resource_owner_secret = self.resource_owner_secret
        )

    def test_construct_base_string(self):
        """
        Example text to be turned into a base string::

            POST /request?b5=%3D%253D&a3=a&c%40=&a2=r%20b HTTP/1.1
            Host: example.com
            Content-Type: application/x-www-form-urlencoded
            Authorization: OAuth realm="Example",
                           oauth_consumer_key="9djdj82h48djs9d2",
                           oauth_token="kkk9d7dh3k39sjv7",
                           oauth_signature_method="HMAC-SHA1",
                           oauth_timestamp="137131201",
                           oauth_nonce="7d8f3e4a",
                           oauth_signature="bYT5CMsGcbgUdFHObYMEfcx6bsw%3D"

        Sample Base string generated and tested against::

            POST&http%253A%2F%2Fexample.com%2Frequest%253Fb5%253D%25253D%252525
            3D%2526a3%253Da%2526c%252540%253D%2526a2%253Dr%252520b&OAuth%2520re
            alm%253D%2522Example%2522%252Coauth_consumer_key%253D%25229djdj82h4
            8djs9d2%2522%252Coauth_token%253D%2522kkk9d7dh3k39sjv7%2522%252Coau
            th_signature_method%253D%2522HMAC-SHA1%2522%252Coauth_timestamp%253
            D%2522137131201%2522%252Coauth_nonce%253D%25227d8f3e4a%2522%252Coau
            th_signature%253D%2522bYT5CMsGcbgUdFHObYMEfcx6bsw%25253D%2522
        """
        self.assertRaises(ValueError, construct_base_string,
                          self.http_method,
                          self.base_string_url,
                          self.normalized_encoded_request_parameters)
        self.assertRaises(ValueError, construct_base_string,
                          self.http_method.decode('utf-8'),
                          self.base_string_url,
                          self.normalized_encoded_request_parameters)
        self.assertRaises(ValueError, construct_base_string,
                          self.http_method.decode('utf-8'),
                          self.base_string_url.decode('utf-8'),
                          self.normalized_encoded_request_parameters)

        base_string = construct_base_string(
            self.http_method.decode('utf-8'),
            self.base_string_url.decode('utf-8'),
            self.normalized_encoded_request_parameters.decode('utf-8')
        )

        self.assertEqual(self.control_base_string, base_string)

    def test_normalize_base_string_uri(self):
        """
        Example text to be turned into a normalized base string uri::

            GET /?q=1 HTTP/1.1
            Host: www.example.net:8080

        Sample string generated::

            https://www.example.net:8080/
        """

        # test for unicode failure
        uri = b"www.example.com:8080"
        self.assertRaises(ValueError, normalize_base_string_uri, uri)

        # test for missing scheme
        uri = "www.example.com:8080"
        self.assertRaises(ValueError, normalize_base_string_uri, uri)

        # test a URI with the default port
        uri = "http://www.example.com:80/"
        self.assertEquals(normalize_base_string_uri(uri),
                          "http://www.example.com/")

        # test a URI missing a path
        uri = "http://www.example.com"
        self.assertEquals(normalize_base_string_uri(uri),
                          "http://www.example.com/")

        # test a relative URI
        uri = "/a-host-relative-uri"
        host = "www.example.com"
        self.assertRaises(ValueError, normalize_base_string_uri, (uri, host))

        # test overriding the URI's netloc with a host argument
        uri = "http://www.example.com/a-path"
        host = "alternatehost.example.com"
        self.assertEquals(normalize_base_string_uri(uri, host),
                          "http://alternatehost.example.com/a-path")

    def test_collect_parameters(self):
        """We check against parameters multiple times in case things change
        after more parameters are added.
        """
        self.assertEquals(collect_parameters(), [])

        # Check against uri_query
        parameters = collect_parameters(uri_query=self.uri_query)
        correct_parameters = [('b5', '=%3D'),
                              ('a3', 'a'),
                              ('c@', ''),
                              ('a2', 'r b'),
                              ('c2', ''),
                              ('a3', '2 q')]
        self.assertEqual(sorted(parameters), sorted(correct_parameters))

        headers = {'Authorization': self.authorization_header}
        # check against authorization header as well
        parameters = collect_parameters(
            uri_query=self.uri_query, headers=headers)
        parameters_with_realm = collect_parameters(
            uri_query=self.uri_query, headers=headers, with_realm=True)
        # Redo the checks against all the parameters. Duplicated code but
        # better safety
        correct_parameters += [
            ('oauth_nonce', '7d8f3e4a'),
            ('oauth_timestamp', '137131201'),
            ('oauth_consumer_key', '9djdj82h48djs9d2'),
            ('oauth_signature_method', 'HMAC-SHA1'),
            ('oauth_token', 'kkk9d7dh3k39sjv7')]
        correct_parameters_with_realm = (
            correct_parameters + [('realm', 'Example')])
        self.assertEqual(sorted(parameters), sorted(correct_parameters))
        self.assertEqual(sorted(parameters_with_realm),
                         sorted(correct_parameters_with_realm))

        # Add in the body.
        # TODO: Add more content for the body. Daniel Greenfeld 2012/03/12
        # Redo again the checks against all the parameters. Duplicated code
        # but better safety
        parameters = collect_parameters(
            uri_query=self.uri_query, body=self.body, headers=headers)
        correct_parameters += [
            ('content', 'This is being the body of things')]
        self.assertEqual(sorted(parameters), sorted(correct_parameters))

    def test_normalize_parameters(self):
        """ We copy some of the variables from the test method above."""

        headers = {'Authorization': self.authorization_header}
        parameters = collect_parameters(
            uri_query=self.uri_query, body=self.body, headers=headers)
        normalized = normalize_parameters(parameters)

        # Unicode everywhere and always
        self.assertIsInstance(normalized, unicode_type)

        # Lets see if things are in order
        # check to see that querystring keys come in alphanumeric order:
        querystring_keys = ['a2', 'a3', 'b5', 'content', 'oauth_consumer_key',
                            'oauth_nonce', 'oauth_signature_method',
                            'oauth_timestamp', 'oauth_token']
        index = -1  # start at -1 because the 'a2' key starts at index 0
        for key in querystring_keys:
            self.assertGreater(normalized.index(key), index)
            index = normalized.index(key)

    # Control signature created using openssl:
    # echo -n $(cat <message>) | openssl dgst -binary -hmac <key> | base64
    control_signature = "Uau4O9Kpd2k6rvh7UZN/RN+RG7Y="

    def test_sign_hmac_sha1(self):
        """Verifying HMAC-SHA1 signature against one created by OpenSSL."""

        self.assertRaises(ValueError, sign_hmac_sha1, self.control_base_string,
                          self.client_secret, self.resource_owner_secret)

        sign = sign_hmac_sha1(self.control_base_string,
                              self.client_secret.decode('utf-8'),
                              self.resource_owner_secret.decode('utf-8'))
        self.assertEquals(len(sign), 28)
        self.assertEquals(sign, self.control_signature)

    def test_sign_hmac_sha1_with_client(self):
        self.assertRaises(ValueError,
            sign_hmac_sha1_with_client,
            self.control_base_string,
            self.client)

        self.client.decode()
        sign = sign_hmac_sha1_with_client(
            self.control_base_string, self.client)

        self.assertEquals(len(sign), 28)
        self.assertEquals(sign, self.control_signature)


    control_base_string_rsa_sha1 = (
        b"POST&http%253A%2F%2Fexample.com%2Frequest%253Fb5%253D"
        b"%25253D%2525253D%2526a3%253Da%2526c%252540%253D%2526"
        b"a2%253Dr%252520b&OAuth%2520realm%253D%2522Example%25"
        b"22%252Coauth_consumer_key%253D%25229djdj82h48djs9d2"
        b"%2522%252Coauth_token%253D%2522kkk9d7dh3k39sjv7%2522"
        b"%252Coauth_signature_method%253D%2522HMAC-SHA1%2522"
        b"%252Coauth_timestamp%253D%2522137131201%2522%252Coau"
        b"th_nonce%253D%25227d8f3e4a%2522%252Coauth_signature"
        b"%253D%2522bYT5CMsGcbgUdFHObYMEfcx6bsw%25253D%2522")

    @property
    def rsa_private_key(self):
        # Generated using: $ openssl genrsa -out <key>.pem 1024
        # PyCrypto / python-rsa requires the key to be concatenated with
        # linebreaks.
        return (
            b"-----BEGIN RSA PRIVATE KEY-----\nMIICXgIBAAKBgQDk1/bxy"
            b"S8Q8jiheHeYYp/4rEKJopeQRRKKpZI4s5i+UPwVpupG\nAlwXWfzXw"
            b"SMaKPAoKJNdu7tqKRniqst5uoHXw98gj0x7zamu0Ck1LtQ4c7pFMVa"
            b"h\n5IYGhBi2E9ycNS329W27nJPWNCbESTu7snVlG8V8mfvGGg3xNjT"
            b"MO7IdrwIDAQAB\nAoGBAOQ2KuH8S5+OrsL4K+wfjoCi6MfxCUyqVU9"
            b"GxocdM1m30WyWRFMEz2nKJ8fR\np3vTD4w8yplTOhcoXdQZl0kRoaD"
            b"zrcYkm2VvJtQRrX7dKFT8dR8D/Tr7dNQLOXfC\nDY6xveQczE7qt7V"
            b"k7lp4FqmxBsaaEuokt78pOOjywZoInjZhAkEA9wz3zoZNT0/i\nrf6"
            b"qv2qTIeieUB035N3dyw6f1BGSWYaXSuerDCD/J1qZbAPKKhyHZbVaw"
            b"Ft3UMhe\n542UftBaxQJBAO0iJy1I8GQjGnS7B3yvyH3CcLYGy296+"
            b"XO/2xKp/d/ty1OIeovx\nC60pLNwuFNF3z9d2GVQAdoQ89hUkOtjZL"
            b"eMCQQD0JO6oPHUeUjYT+T7ImAv7UKVT\nSuy30sKjLzqoGw1kR+wv7"
            b"C5PeDRvscs4wa4CW9s6mjSrMDkDrmCLuJDtmf55AkEA\nkmaMg2PNr"
            b"jUR51F0zOEFycaaqXbGcFwe1/xx9zLmHzMDXd4bsnwt9kk+fe0hQzV"
            b"S\nJzatanQit3+feev1PN3QewJAWv4RZeavEUhKv+kLe95Yd0su7lT"
            b"LVduVgh4v5yLT\nGa6FHdjGPcfajt+nrpB1n8UQBEH9ZxniokR/IPv"
            b"dMlxqXA==\n-----END RSA PRIVATE KEY-----"
        )

    @property
    def control_signature_rsa_sha1(self):
        # Base string saved in "<message>". Signature obtained using:
        # $ echo -n $(cat <message>) | openssl dgst -sign <key>.pem | base64
        # where echo -n suppresses the last linebreak.
        return (
            "zV5g8ArdMuJuOXlH8XOqfLHS11XdthfIn4HReDm7jz8JmgLabHGmVBqCkCfZoFJPH"
            "dka7tLvCplK/jsV4FUOnftrJOQhbXguuBdi87/hmxOFKLmQYqqlEW7BdXmwKLZcki"
            "qq3qE5XziBgKSAFRkxJ4gmJAymvJBtrJYN9728rK8="
        )


    def test_sign_rsa_sha1(self):
        """Verify RSA-SHA1 signature against one created by OpenSSL."""
        base_string = self.control_base_string_rsa_sha1

        private_key = self.rsa_private_key

        control_signature = self.control_signature_rsa_sha1

        sign = sign_rsa_sha1(base_string, private_key)
        self.assertEquals(sign, control_signature)
        sign = sign_rsa_sha1(base_string.decode('utf-8'), private_key)
        self.assertEquals(sign, control_signature)


    def test_sign_rsa_sha1_with_client(self):
        base_string = self.control_base_string_rsa_sha1

        self.client.rsa_key = self.rsa_private_key

        control_signature = self.control_signature_rsa_sha1

        sign = sign_rsa_sha1_with_client(base_string, self.client)

        self.assertEquals(sign, control_signature)

        self.client.decode() ## Decode `rsa_private_key` from UTF-8

        sign = sign_rsa_sha1_with_client(base_string, self.client)

        self.assertEquals(sign, control_signature)


    control_signature_plaintext = (
        "ECrDNoq1VYzzzzzzzzzyAK7TwZNtPnkqatqZZZZ&"
        "just-a-string%20%20%20%20asdasd")

    def test_sign_plaintext(self):
        """ """

        self.assertRaises(ValueError, sign_plaintext, self.client_secret,
                          self.resource_owner_secret)
        sign = sign_plaintext(self.client_secret.decode('utf-8'),
                              self.resource_owner_secret.decode('utf-8'))
        self.assertEquals(sign, self.control_signature_plaintext)


    def test_sign_plaintext_with_client(self):
        self.assertRaises(ValueError, sign_plaintext_with_client,
                          None, self.client)

        self.client.decode()

        sign = sign_plaintext_with_client(None, self.client)

        self.assertEquals(sign, self.control_signature_plaintext)

