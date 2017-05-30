# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from ...unittest import TestCase

from oauthlib.oauth1 import RequestValidator


class RequestValidatorTests(TestCase):

    def test_not_implemented(self):
        v = RequestValidator()
        self.assertRaises(NotImplementedError, v.get_client_secret, None, None)
        self.assertRaises(NotImplementedError, v.get_request_token_secret,
                None, None, None)
        self.assertRaises(NotImplementedError, v.get_access_token_secret,
                None, None, None)
        self.assertRaises(NotImplementedError, lambda: v.dummy_client)
        self.assertRaises(NotImplementedError, lambda: v.dummy_request_token)
        self.assertRaises(NotImplementedError, lambda: v.dummy_access_token)
        self.assertRaises(NotImplementedError, v.get_rsa_key, None, None)
        self.assertRaises(NotImplementedError, v.get_default_realms, None, None)
        self.assertRaises(NotImplementedError, v.get_realms, None, None)
        self.assertRaises(NotImplementedError, v.get_redirect_uri, None, None)
        self.assertRaises(NotImplementedError, v.validate_client_key, None, None)
        self.assertRaises(NotImplementedError, v.validate_access_token,
                None, None, None)
        self.assertRaises(NotImplementedError, v.validate_request_token,
                None, None, None)
        self.assertRaises(NotImplementedError, v.verify_request_token,
                None, None)
        self.assertRaises(NotImplementedError, v.verify_realms,
                None, None, None)
        self.assertRaises(NotImplementedError, v.validate_timestamp_and_nonce,
            None, None, None, None)
        self.assertRaises(NotImplementedError, v.validate_redirect_uri,
                None, None, None)
        self.assertRaises(NotImplementedError, v.validate_realms,
                None, None, None, None, None)
        self.assertRaises(NotImplementedError, v.validate_requested_realms,
                None, None, None)
        self.assertRaises(NotImplementedError, v.validate_verifier,
                None, None, None, None)
        self.assertRaises(NotImplementedError, v.save_access_token, None, None)
        self.assertRaises(NotImplementedError, v.save_request_token, None, None)
        self.assertRaises(NotImplementedError, v.save_verifier,
                None, None, None)

    def test_check_length(self):
        v = RequestValidator()

        for method in (v.check_client_key, v.check_request_token,
                       v.check_access_token, v.check_nonce, v.check_verifier):
            for not_valid in ('tooshort', 'invalid?characters!',
                              'thisclientkeyisalittlebittoolong'):
                self.assertFalse(method(not_valid))
            for valid in ('itsjustaboutlongenough',):
                self.assertTrue(method(valid))

    def test_check_realms(self):
        v = RequestValidator()
        self.assertFalse(v.check_realms(['foo']))

        class FooRealmValidator(RequestValidator):
            @property
            def realms(self):
                return ['foo']

        v = FooRealmValidator()
        self.assertTrue(v.check_realms(['foo']))
