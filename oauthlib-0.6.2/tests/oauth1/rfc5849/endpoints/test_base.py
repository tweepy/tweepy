from __future__ import unicode_literals, absolute_import

from mock import MagicMock
from re import sub
from ....unittest import TestCase

from oauthlib.common import safe_string_equals
from oauthlib.oauth1 import Client, RequestValidator
from oauthlib.oauth1.rfc5849 import errors, SIGNATURE_RSA, SIGNATURE_HMAC
from oauthlib.oauth1.rfc5849 import SIGNATURE_PLAINTEXT
from oauthlib.oauth1.rfc5849.endpoints import RequestTokenEndpoint, BaseEndpoint


URLENCODED = {"Content-Type": "application/x-www-form-urlencoded"}


class BaseEndpointTest(TestCase):

    def setUp(self):
        self.validator = MagicMock(spec=RequestValidator)
        self.validator.allowed_signature_methods = ['HMAC-SHA1']
        self.validator.timestamp_lifetime = 600
        self.endpoint = RequestTokenEndpoint(self.validator)
        self.client = Client('foo', callback_uri='https://c.b/cb')
        self.uri, self.headers, self.body = self.client.sign(
                'https://i.b/request_token')

    def test_ssl_enforcement(self):
        uri, headers, _ = self.client.sign('http://i.b/request_token')
        h, b, s = self.endpoint.create_request_token_response(
                uri, headers=headers)
        self.assertEqual(s, 400)
        self.assertIn('insecure_transport_protocol', b)

    def test_missing_parameters(self):
        h, b, s = self.endpoint.create_request_token_response(self.uri)
        self.assertEqual(s, 400)
        self.assertIn('invalid_request', b)

    def test_signature_methods(self):
        headers = {}
        headers['Authorization'] = self.headers['Authorization'].replace(
                'HMAC', 'RSA')
        h, b, s = self.endpoint.create_request_token_response(
                self.uri, headers=headers)
        self.assertEqual(s, 400)
        self.assertIn('invalid_signature_method', b)

    def test_invalid_version(self):
        headers = {}
        headers['Authorization'] = self.headers['Authorization'].replace(
                '1.0', '2.0')
        h, b, s = self.endpoint.create_request_token_response(
                self.uri, headers=headers)
        self.assertEqual(s, 400)
        self.assertIn('invalid_request', b)

    def test_expired_timestamp(self):
        headers = {}
        for pattern in ('12345678901', '4567890123', '123456789K'):
            headers['Authorization'] = sub('timestamp="\d*k?"',
                    'timestamp="%s"' % pattern,
                     self.headers['Authorization'])
            h, b, s = self.endpoint.create_request_token_response(
                    self.uri, headers=headers)
            self.assertEqual(s, 400)
            self.assertIn('invalid_request', b)

    def test_client_key_check(self):
        self.validator.check_client_key.return_value = False
        h, b, s = self.endpoint.create_request_token_response(
                self.uri, headers=self.headers)
        self.assertEqual(s, 400)
        self.assertIn('invalid_request', b)

    def test_noncecheck(self):
        self.validator.check_nonce.return_value = False
        h, b, s = self.endpoint.create_request_token_response(
                self.uri, headers=self.headers)
        self.assertEqual(s, 400)
        self.assertIn('invalid_request', b)

    def test_enforce_ssl(self):
        """Ensure SSL is enforced by default."""
        v = RequestValidator()
        e = BaseEndpoint(v)
        c = Client('foo')
        u, h, b = c.sign('http://example.com')
        r = e._create_request(u, 'GET', b, h)
        self.assertRaises(errors.InsecureTransportError,
                e._check_transport_security, r)

    def test_multiple_source_params(self):
        """Check for duplicate params"""
        v = RequestValidator()
        e = BaseEndpoint(v)
        self.assertRaises(errors.InvalidRequestError, e._create_request,
                'https://a.b/?oauth_signature_method=HMAC-SHA1',
                'GET', 'oauth_version=foo', URLENCODED)
        headers = {'Authorization': 'OAuth oauth_signature="foo"'}
        headers.update(URLENCODED)
        self.assertRaises(errors.InvalidRequestError, e._create_request,
                'https://a.b/?oauth_signature_method=HMAC-SHA1',
                'GET',
                'oauth_version=foo',
                headers)
        headers = {'Authorization': 'OAuth oauth_signature_method="foo"'}
        headers.update(URLENCODED)
        self.assertRaises(errors.InvalidRequestError, e._create_request,
                'https://a.b/',
                'GET',
                'oauth_signature=foo',
                headers)

    def test_duplicate_params(self):
        """Ensure params are only supplied once"""
        v = RequestValidator()
        e = BaseEndpoint(v)
        self.assertRaises(errors.InvalidRequestError, e._create_request,
                'https://a.b/?oauth_version=a&oauth_version=b',
                'GET', None, URLENCODED)
        self.assertRaises(errors.InvalidRequestError, e._create_request,
                'https://a.b/', 'GET', 'oauth_version=a&oauth_version=b',
                URLENCODED)

    def test_mandated_params(self):
        """Ensure all mandatory params are present."""
        v = RequestValidator()
        e = BaseEndpoint(v)
        r = e._create_request('https://a.b/', 'GET',
                'oauth_signature=a&oauth_consumer_key=b&oauth_nonce',
                URLENCODED)
        self.assertRaises(errors.InvalidRequestError,
                e._check_mandatory_parameters, r)

    def test_oauth_version(self):
        """OAuth version must be 1.0 if present."""
        v = RequestValidator()
        e = BaseEndpoint(v)
        r = e._create_request('https://a.b/', 'GET',
                ('oauth_signature=a&oauth_consumer_key=b&oauth_nonce=c&'
                 'oauth_timestamp=a&oauth_signature_method=RSA-SHA1&'
                 'oauth_version=2.0'),
                URLENCODED)
        self.assertRaises(errors.InvalidRequestError,
                e._check_mandatory_parameters, r)

    def test_oauth_timestamp(self):
        """Check for a valid UNIX timestamp."""
        v = RequestValidator()
        e = BaseEndpoint(v)

        # Invalid timestamp length, must be 10
        r = e._create_request('https://a.b/', 'GET',
                ('oauth_signature=a&oauth_consumer_key=b&oauth_nonce=c&'
                 'oauth_version=1.0&oauth_signature_method=RSA-SHA1&'
                 'oauth_timestamp=123456789'),
                URLENCODED)
        self.assertRaises(errors.InvalidRequestError,
                e._check_mandatory_parameters, r)

        # Invalid timestamp age, must be younger than 10 minutes
        r = e._create_request('https://a.b/', 'GET',
                ('oauth_signature=a&oauth_consumer_key=b&oauth_nonce=c&'
                 'oauth_version=1.0&oauth_signature_method=RSA-SHA1&'
                 'oauth_timestamp=1234567890'),
                URLENCODED)
        self.assertRaises(errors.InvalidRequestError,
                e._check_mandatory_parameters, r)

        # Timestamp must be an integer
        r = e._create_request('https://a.b/', 'GET',
                ('oauth_signature=a&oauth_consumer_key=b&oauth_nonce=c&'
                 'oauth_version=1.0&oauth_signature_method=RSA-SHA1&'
                 'oauth_timestamp=123456789a'),
                URLENCODED)
        self.assertRaises(errors.InvalidRequestError,
                e._check_mandatory_parameters, r)

    def test_signature_method_validation(self):
        """Ensure valid signature method is used."""

        body = ('oauth_signature=a&oauth_consumer_key=b&oauth_nonce=c&'
                'oauth_version=1.0&oauth_signature_method=%s&'
                'oauth_timestamp=1234567890')

        uri = 'https://example.com/'

        class HMACValidator(RequestValidator):

            @property
            def allowed_signature_methods(self):
                return (SIGNATURE_HMAC,)

        v = HMACValidator()
        e = BaseEndpoint(v)
        r = e._create_request(uri, 'GET', body % 'RSA-SHA1', URLENCODED)
        self.assertRaises(errors.InvalidSignatureMethodError,
                e._check_mandatory_parameters, r)
        r = e._create_request(uri, 'GET', body % 'PLAINTEXT', URLENCODED)
        self.assertRaises(errors.InvalidSignatureMethodError,
                e._check_mandatory_parameters, r)
        r = e._create_request(uri, 'GET', body % 'shibboleth', URLENCODED)
        self.assertRaises(errors.InvalidSignatureMethodError,
                e._check_mandatory_parameters, r)

        class RSAValidator(RequestValidator):

            @property
            def allowed_signature_methods(self):
                return (SIGNATURE_RSA,)

        v = RSAValidator()
        e = BaseEndpoint(v)
        r = e._create_request(uri, 'GET', body % 'HMAC-SHA1', URLENCODED)
        self.assertRaises(errors.InvalidSignatureMethodError,
                e._check_mandatory_parameters, r)
        r = e._create_request(uri, 'GET', body % 'PLAINTEXT', URLENCODED)
        self.assertRaises(errors.InvalidSignatureMethodError,
                e._check_mandatory_parameters, r)
        r = e._create_request(uri, 'GET', body % 'shibboleth', URLENCODED)
        self.assertRaises(errors.InvalidSignatureMethodError,
                e._check_mandatory_parameters, r)

        class PlainValidator(RequestValidator):

            @property
            def allowed_signature_methods(self):
                return (SIGNATURE_PLAINTEXT,)

        v = PlainValidator()
        e = BaseEndpoint(v)
        r = e._create_request(uri, 'GET', body % 'HMAC-SHA1', URLENCODED)
        self.assertRaises(errors.InvalidSignatureMethodError,
                e._check_mandatory_parameters, r)
        r = e._create_request(uri, 'GET', body % 'RSA-SHA1', URLENCODED)
        self.assertRaises(errors.InvalidSignatureMethodError,
                e._check_mandatory_parameters, r)
        r = e._create_request(uri, 'GET', body % 'shibboleth', URLENCODED)
        self.assertRaises(errors.InvalidSignatureMethodError,
                e._check_mandatory_parameters, r)


class ClientValidator(RequestValidator):
        clients = ['foo']
        nonces = [('foo', 'once', '1234567891', 'fez')]
        owners = {'foo': ['abcdefghijklmnopqrstuvxyz', 'fez']}
        assigned_realms = {('foo', 'abcdefghijklmnopqrstuvxyz'): 'photos'}
        verifiers = {('foo', 'fez'): 'shibboleth'}

        @property
        def client_key_length(self):
            return 1, 30

        @property
        def request_token_length(self):
            return 1, 30

        @property
        def access_token_length(self):
            return 1, 30

        @property
        def nonce_length(self):
            return 2, 30

        @property
        def verifier_length(self):
            return 2, 30

        @property
        def realms(self):
            return ['photos']

        @property
        def timestamp_lifetime(self):
            # Disabled check to allow hardcoded verification signatures
            return 1000000000

        @property
        def dummy_client(self):
            return 'dummy'

        @property
        def dummy_request_token(self):
            return 'dumbo'

        @property
        def dummy_access_token(self):
            return 'dumbo'

        def validate_timestamp_and_nonce(self, client_key, timestamp, nonce,
                request, request_token=None, access_token=None):
            resource_owner_key = request_token if request_token else access_token
            return not (client_key, nonce, timestamp, resource_owner_key) in self.nonces

        def validate_client_key(self, client_key):
            return client_key in self.clients

        def validate_access_token(self, client_key, access_token, request):
            return (self.owners.get(client_key) and
                    access_token in self.owners.get(client_key))

        def validate_request_token(self, client_key, request_token, request):
            return (self.owners.get(client_key) and
                    request_token in self.owners.get(client_key))

        def validate_requested_realm(self, client_key, realm, request):
            return True

        def validate_realm(self, client_key, access_token, request, uri=None,
                required_realm=None):
            return (client_key, access_token) in self.assigned_realms

        def validate_verifier(self, client_key, request_token, verifier,
                request):
            return ((client_key, request_token) in self.verifiers and
                     safe_string_equals(verifier, self.verifiers.get(
                        (client_key, request_token))))

        def validate_redirect_uri(self, client_key, redirect_uri, request):
            return redirect_uri.startswith('http://client.example.com/')

        def get_client_secret(self, client_key, request):
            return 'super secret'

        def get_access_token_secret(self, client_key, access_token, request):
            return 'even more secret'

        def get_request_token_secret(self, client_key, request_token, request):
            return 'even more secret'

        def get_rsa_key(self, client_key, request):
            return ("-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNA"
                    "DCBiQKBgQDVLQCATX8iK+aZuGVdkGb6uiar\nLi/jqFwL1dYj0JLIsdQc"
                    "KaMWtPC06K0+vI+RRZcjKc6sNB9/7kJcKN9Ekc9BUxyT\n/D09Cz47cmC"
                    "YsUoiW7G8NSqbE4wPiVpGkJRzFAxaCWwOSSQ+lpC9vwxnvVQfOoZ1\nnp"
                    "mWbCdA0iTxsMahwQIDAQAB\n-----END PUBLIC KEY-----")


class SignatureVerificationTest(TestCase):

    def setUp(self):
        v = ClientValidator()
        self.e = BaseEndpoint(v)

        self.uri = 'https://example.com/'
        self.sig = ('oauth_signature=%s&'
                    'oauth_timestamp=1234567890&'
                    'oauth_nonce=abcdefghijklmnopqrstuvwxyz&'
                    'oauth_version=1.0&'
                    'oauth_signature_method=%s&'
                    'oauth_token=abcdefghijklmnopqrstuvxyz&'
                    'oauth_consumer_key=foo')

    def test_signature_too_short(self):
        short_sig = ('oauth_signature=fmrXnTF4lO4o%2BD0%2FlZaJHP%2FXqEY&'
              'oauth_timestamp=1234567890&'
              'oauth_nonce=abcdefghijklmnopqrstuvwxyz&'
              'oauth_version=1.0&oauth_signature_method=HMAC-SHA1&'
              'oauth_token=abcdefghijklmnopqrstuvxyz&'
              'oauth_consumer_key=foo')
        r = self.e._create_request(self.uri, 'GET', short_sig, URLENCODED)
        self.assertFalse(self.e._check_signature(r))

        plain = ('oauth_signature=correctlengthbutthewrongcontent1111&'
              'oauth_timestamp=1234567890&'
              'oauth_nonce=abcdefghijklmnopqrstuvwxyz&'
              'oauth_version=1.0&oauth_signature_method=PLAINTEXT&'
              'oauth_token=abcdefghijklmnopqrstuvxyz&'
              'oauth_consumer_key=foo')
        r = self.e._create_request(self.uri, 'GET', plain, URLENCODED)
        self.assertFalse(self.e._check_signature(r))

    def test_hmac_signature(self):
        hmac_sig = "fmrXnTF4lO4o%2BD0%2FlZaJHP%2FXqEY%3D"
        sig = self.sig % (hmac_sig, "HMAC-SHA1")
        r = self.e._create_request(self.uri, 'GET', sig, URLENCODED)
        self.assertTrue(self.e._check_signature(r))

    def test_rsa_signature(self):
        rsa_sig = ("fxFvCx33oKlR9wDquJ%2FPsndFzJphyBa3RFPPIKi3flqK%2BJ7yIrMVbH"
                   "YTM%2FLHPc7NChWz4F4%2FzRA%2BDN1k08xgYGSBoWJUOW6VvOQ6fbYhMA"
                   "FkOGYbuGDbje487XMzsAcv6ZjqZHCROSCk5vofgLk2SN7RZ3OrgrFzf4in"
                   "xetClqA%3D")
        sig = self.sig % (rsa_sig, "RSA-SHA1")
        r = self.e._create_request(self.uri, 'GET', sig, URLENCODED)
        self.assertTrue(self.e._check_signature(r))

    def test_plaintext_signature(self):
        plain_sig = "super%252520secret%26even%252520more%252520secret"
        sig = self.sig % (plain_sig, "PLAINTEXT")
        r = self.e._create_request(self.uri, 'GET', sig, URLENCODED)
        self.assertTrue(self.e._check_signature(r))
