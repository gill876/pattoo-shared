#!/usr/bin/env python3
"""Test the encrypt module."""

# Standard imports
import unittest
import os
import sys
import shutil
import tempfile
from random import random, randint
import hashlib
from collections import defaultdict

# Try to create a working PYTHONPATH
EXEC_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(
    os.path.abspath(os.path.join(EXEC_DIR, os.pardir)), os.pardir))
_EXPECTED = '{0}pattoo-shared{0}tests{0}pattoo_shared_'.format(os.sep)
if EXEC_DIR.endswith(_EXPECTED) is True:
    # We need to prepend the path in case PattooShared has been installed
    # elsewhere on the system using PIP. This could corrupt expected results
    sys.path.insert(0, ROOT_DIR)
else:
    print('''This script is not installed in the "{0}" directory. Please fix.\
'''.format(_EXPECTED))
    sys.exit(2)

# Pattoo imports
from pattoo_shared import encrypt
from pattoo_shared import configuration
from pattoo_shared import files
from tests.libraries.configuration import UnittestConfig


class TestKeyRing(unittest.TestCase):
    """Test all methods of KeyRing class."""

    def test___init__(self):
        """Testing function __init__."""
        pass

    def test__import(self):
        """Testing function _import."""
        pass

    def test__export(self):
        """Testing function _export."""
        pass

    def test__generate(self):
        """Testing function _generate."""
        pass

    def test__get_public_keyid(self):
        """Testing function _get_public_keyid."""
        pass


class TestEncrypt(unittest.TestCase):
    """Test all methods of KeyRing class."""

    def setUp(self):
        """Run these steps before each test is performed."""
        # Initialize key variables
        config = configuration.BaseConfig()

        # Setup encryption instances
        self.instances = defaultdict(lambda: defaultdict(dict))

        directory = tempfile.mkdtemp()
        for item in range(2):
            agent = hashlib.md5('{}'.format(random()).encode()).hexdigest()
            email = files.get_agent_id(agent, config)
            self.instances[item]['directory'] = directory
            self.instances[item]['agent'] = agent
            self.instances[item]['email'] = email
            self.instances[item]['instance'] = encrypt.Encryption(
                agent, directory)

    def tearDown(self):
        """Run these steps after each test is performed."""
        for _, data_ in self.instances.items():
            for key, value in data_.items():
                if key == 'directory':
                    if os.path.isdir(value) is True:
                        shutil.rmtree(value)

    def test___init__(self):
        """Testing function __init__."""
        pass

    def test_decrypt(self):
        """Testing function decrypt."""
        # Initialize key Variable
        expected = '{}'.format(random())

        # Decrypting with own fingerprint
        for _, data_ in self.instances.items():
            instance = data_['instance']
            email = data_['email']

            # Encrypt with internal fingerprint
            encrypted = instance.encrypt(expected)

            # Decrypt
            result = instance.decrypt(encrypted)
            self.assertEqual(result, expected)

            # Encrypt with external fingerprint that is the same as the
            # internal instance fingerprint
            fingerprint = instance.fingerprint(email)
            fingerprint_ = instance.fingerprint()
            self.assertEqual(fingerprint, fingerprint_)
            instance.trust(fingerprint)
            encrypted = instance.encrypt(expected)

            # Decrypt
            result = instance.decrypt(encrypted)
            self.assertEqual(result, expected)

        # Decrypting with a random existing fingerprint
        for _ in range(25):
            # Chose a random instance
            offset = randint(0, len(self.instances) - 1)
            data_ = self.instances[offset]
            email = data_['email']

            # Encrypt with external fingerprint that is the same as the
            # internal instance fingerprint
            new_offset = randint(0, len(self.instances) - 1)
            data_ = self.instances[new_offset]
            instance = data_['instance']
            fingerprint = instance.fingerprint(email)
            instance.trust(fingerprint)
            encrypted = instance.encrypt(expected)

            # Decrypt
            result = instance.decrypt(encrypted)
            self.assertEqual(result, expected)

    def test_sdecrypt(self):
        """Testing function sdecrypt."""
        # Initialize key Variable
        expected = '{}'.format(random())

        # Decrypting with own fingerprint
        for _, data_ in self.instances.items():
            passphrase = '{}'.format(random())
            instance = data_['instance']

            # Encrypt with internal fingerprint
            encrypted = instance.sencrypt(expected, passphrase)

            # Decrypt
            result = instance.sdecrypt(encrypted, passphrase)
            self.assertEqual(result, expected)

    def test__decrypt(self):
        """Testing function _decrypt."""
        # Tested by test_decrypt
        pass

    def test_encrypt(self):
        """Testing function encrypt."""
        # Tested by test_decrypt
        pass

    def test_sencrypt(self):
        """Testing function sencrypt."""
        # Tested by test_sdecrypt
        pass

    def fingerpint(self):
        """Testing function fingerpint."""
        # Tested by test_decrypt
        pass

    def test_trust(self):
        """Testing function trust."""
        # Tested by test_decrypt
        pass

    def test_pdelete(self):
        """Testing function pdelete."""
        # Tested by test_pexport
        pass

    def test_pexport(self):
        """Testing function pexport."""
        # Initialize key variables
        config = configuration.BaseConfig()

        # Test
        for _, data_ in self.instances.items():
            # Get instance information
            instance = data_['instance']
            email = data_['email']
            fingerprint = instance.fingerprint(email)

            # Create a new instance
            new_agent = hashlib.md5('{}'.format(random()).encode()).hexdigest()
            new_email = files.get_agent_id(new_agent, config)
            new_directory = tempfile.mkdtemp()
            new_instance = encrypt.Encryption(new_agent, new_directory)
            new_public_key = new_instance.pexport()
            new_fingerprint = new_instance.fingerprint(new_email)

            # There should be only one public key
            public_key = instance.pexport()

            # Import public key
            instance.pimport(new_public_key)
            result = instance.pexport(new_fingerprint)

            # There should be a match
            self.assertEqual(new_public_key, result)
            self.assertNotEqual(result, public_key)

            # Test deletion of nonexistent fingerprint
            status = instance.pdelete('foo')
            self.assertFalse(status)

            # Test deletion of primary fingerprint
            status = instance.pdelete(fingerprint)
            self.assertFalse(status)

            # Test deletion of primary fingerprint
            status = instance.pdelete(new_fingerprint)
            self.assertTrue(status)
            result = instance.pexport(new_fingerprint)
            self.assertIsNone(result)

            # Delete directory
            shutil.rmtree(new_directory)

    def test_pimport(self):
        """Testing function pimport."""
        # Tested by test_pexport
        pass


class TestFunctions(unittest.TestCase):
    """Test all methods of KeyRing class."""

    def test_generate_key(self):
        """Testing function generate_key."""
        # Test
        result = encrypt.generate_key()
        self.assertTrue(isinstance(result, str))
        self.assertEqual(len(result), 70)


if __name__ == '__main__':
    # Make sure the environment is OK to run unittests
    UnittestConfig().create()

    # Do the unit test
    unittest.main()
