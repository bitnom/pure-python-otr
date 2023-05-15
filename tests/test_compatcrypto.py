# pylint: disable=import-error
# pylint: disable=invalid-name
# pylint: disable=missing-docstring
# pylint: disable=wrong-import-position

from __future__ import unicode_literals

import os
import sys
import unittest

import potr

sys.path.append(os.path.join(os.path.dirname(__file__), 'helpers'))
from potr_test_helpers import to_hex

class CompatCryptoTest(unittest.TestCase):

    def test_SHA256(self):
        # echo -n 'this is a test' | shasum -a 256
        self.assertEqual(
            to_hex(potr.compatcrypto.SHA256(b'this is a test')),
            b'2e99758548972a8e8822ad47fa1017ff72f06f3ff6a016851f45c398732bc50c')

    def test_SHA1(self):
        # echo -n 'this is a test' | shasum
        self.assertEqual(
            to_hex(potr.compatcrypto.SHA1(b'this is a test')),
            b'fa26be19de6bff93f70bc2308434e4a440bbad02')

    def test_SHA1HMAC(self):
        # echo -n 'this is a test' | openssl dgst -sha1 -hmac key
        self.assertEqual(
            to_hex(potr.compatcrypto.SHA1HMAC(b'key', b'this is a test')),
            b'778d71b5ef5a446b2c1c39d1f289ede37bb4ba2e')

    def test_SHA256HMAC(self):
        # echo -n 'this is a test' | openssl dgst -sha56 -hmac key
        self.assertEqual(
            to_hex(potr.compatcrypto.SHA256HMAC(b'key', b'this is a test')),
            b'a85e8284b3aabd90add3da46176bce8e10eff8eafd7d096d8ba7d9396623b894')

    def test_AESCTR_default_counter(self):
        key = potr.utils.long_to_bytes(
            potr.compatcrypto.getrandbits(128), 16)

        aes_encrypter = potr.compatcrypto.AESCTR(key)
        ciphertext = aes_encrypter.encrypt(b'setec astronomy')

        aes_decrypter = potr.compatcrypto.AESCTR(key)
        self.assertEqual(aes_decrypter.decrypt(ciphertext), b'setec astronomy')

    def test_AESCTR_number_counter(self):
        key = potr.utils.long_to_bytes(
            potr.compatcrypto.getrandbits(128), 16)

        aes_encrypter = potr.compatcrypto.AESCTR(key, 2010)
        ciphertext = aes_encrypter.encrypt(b'setec astronomy')

        aes_decrypter = potr.compatcrypto.AESCTR(key, 2010)
        self.assertEqual(aes_decrypter.decrypt(ciphertext), b'setec astronomy')

    def test_AESCTR_counter_counter(self):
        key = potr.utils.long_to_bytes(
            potr.compatcrypto.getrandbits(128), 16)

        aes_encrypter = potr.compatcrypto.AESCTR(key, 2013)
        ciphertext = aes_encrypter.encrypt(b'setec astronomy')

        aes_decrypter = potr.compatcrypto.AESCTR(key, 2013)
        self.assertEqual(aes_decrypter.decrypt(ciphertext), b'setec astronomy')

    def test_getrandbits(self):
        bits = potr.compatcrypto.getrandbits(128)
        byts = potr.utils.long_to_bytes(bits, 16)
        self.assertEquals(len(byts), 16)

    def test_randrange(self):
        pick = potr.compatcrypto.randrange(7, 8)
        self.assertEqual(pick, 7)

        pick = potr.compatcrypto.randrange(0, 10000)
        self.assertGreaterEqual(pick, 0)
        self.assertLess(pick, 10000)
