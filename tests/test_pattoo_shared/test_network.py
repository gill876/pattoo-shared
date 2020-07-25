#!/usr/bin/env python3
"""Test the files module."""

# Standard imports
import unittest
import os
import sys


# Try to create a working PYTHONPATH
EXEC_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(
    os.path.abspath(os.path.join(EXEC_DIR, os.pardir)), os.pardir))
_EXPECTED = '{0}pattoo-shared{0}tests{0}test_pattoo_shared'.format(os.sep)
if EXEC_DIR.endswith(_EXPECTED) is True:
    # We need to prepend the path in case PattooShared has been installed
    # elsewhere on the system using PIP. This could corrupt expected results
    sys.path.insert(0, ROOT_DIR)
else:
    print('''This script is not installed in the "{0}" directory. Please fix.\
'''.format(_EXPECTED))
    sys.exit(2)

# Pattoo imports
from pattoo_shared import network
from tests.libraries.configuration import UnittestConfig


class TestBasicFunctions(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test_get_ipaddress(self):
        """Testing method or function named get_ip_address."""
        # Test bad addresses
        bad_addresses = [123, 'koala_bear', None, True, False, {}, []]
        for item in bad_addresses:
            result = network.get_ipaddress(item)
            self.assertIsNone(result)

        # Test good addresses
        good_addresses = ['127.0.0.1', '::1', 'localhost', 'www.google.com']
        for item in good_addresses:
            result = network.get_ipaddress(item)
            self.assertTrue(bool(result))


if __name__ == '__main__':
    # Make sure the environment is OK to run unittests
    UnittestConfig().create()

    # Do the unit test
    unittest.main()
