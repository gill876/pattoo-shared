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
if EXEC_DIR.endswith('/pattoo-shared/tests/test_pattoo_shared') is True:
    # We need to prepend the path in case PattooShared has been installed
    # elsewhere on the system using PIP. This could corrupt expected results
    sys.path.insert(0, ROOT_DIR)
else:
    print('''\
This script is not installed in the "pattoo-shared/tests/test_pattoo_shared" \
directory. Please fix.''')
    sys.exit(2)

# Pattoo imports
from tests.libraries.configuration import UnittestConfig

from pattoo_shared.constants import DATA_FLOAT
from pattoo_shared.constants import DATA_INT
from pattoo_shared.constants import DATA_COUNT64
from pattoo_shared.constants import DATA_COUNT
from pattoo_shared.constants import DATA_STRING
from pattoo_shared.constants import DATA_NONE
from pattoo_shared.constants import MAX_KEYPAIR_LENGTH
from pattoo_shared.constants import DATAPOINT_KEYS
from pattoo_shared.constants import NON_DATAPOINT_KEYS
from pattoo_shared.constants import RESERVED_KEYS
from pattoo_shared.constants import CACHE_KEYS


from pattoo_shared.constants import PATTOO_API_SITE_PREFIX
from pattoo_shared.constants import PATTOO_API_AGENT_PREFIX
from pattoo_shared.constants import PATTOO_API_AGENT_EXECUTABLE
from pattoo_shared.constants import PATTOO_API_AGENT_PROXY


class TestConstants(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test_constants(self):
        """Testing constants."""
        # Test data type constants
        self.assertEqual(DATA_FLOAT, 101)
        self.assertEqual(DATA_INT, 99)
        self.assertEqual(DATA_COUNT64, 64)
        self.assertEqual(DATA_COUNT, 32)
        self.assertEqual(DATA_STRING, 2)
        self.assertEqual(DATA_NONE, None)
        self.assertEqual(MAX_KEYPAIR_LENGTH, 512)
        self.assertEqual(
            DATAPOINT_KEYS,
            ('pattoo_checksum', 'pattoo_metadata', 'pattoo_data_type',
             'pattoo_key', 'pattoo_value', 'pattoo_timestamp'))
        self.assertEqual(
            NON_DATAPOINT_KEYS, ['pattoo_source', 'pattoo_polling_interval'])
        self.assertEqual(
            RESERVED_KEYS,
            ('pattoo_checksum', 'pattoo_metadata', 'pattoo_data_type',
             'pattoo_key', 'pattoo_value', 'pattoo_timestamp',
             'pattoo_source', 'pattoo_polling_interval'))
        self.assertEqual(
            CACHE_KEYS,
            ('pattoo_source', 'pattoo_datapoints', 'pattoo_polling_interval',
             'pattoo_source_timestamp'))

        # Test pattoo API constants
        self.assertEqual(
            PATTOO_API_SITE_PREFIX, '/pattoo/api/v1')
        self.assertEqual(
            PATTOO_API_AGENT_PREFIX, '{}/agent'.format(PATTOO_API_SITE_PREFIX))
        self.assertEqual(
            PATTOO_API_AGENT_EXECUTABLE, 'pattoo-api-agentd')
        self.assertEqual(
            PATTOO_API_AGENT_PROXY,
            '{}-gunicorn'.format(PATTOO_API_AGENT_EXECUTABLE))


if __name__ == '__main__':
    # Make sure the environment is OK to run unittests
    UnittestConfig().create()

    # Do the unit test
    unittest.main()
