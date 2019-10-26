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
from pattoo_shared.constants import PATTOO_AGENT_OS_SPOKED_API_PREFIX
from pattoo_shared.constants import PATTOO_AGENT_OS_SPOKED
from pattoo_shared.constants import PATTOO_AGENT_OS_SPOKED_PROXY
from pattoo_shared.constants import PATTOO_AGENT_OS_AUTONOMOUSD
from pattoo_shared.constants import PATTOO_AGENT_OS_HUBD
from pattoo_shared.constants import PATTOO_AGENT_SNMPD
from pattoo_shared.constants import PATTOO_API_SITE_PREFIX
from pattoo_shared.constants import PATTOO_API_AGENT_PREFIX
from pattoo_shared.constants import PATTOO_API_AGENT_EXECUTABLE
from pattoo_shared.constants import PATTOO_API_AGENT_GUNICORN_AGENT
from pattoo_shared.constants import PATTOO_AGENT_MODBUSTCPD


class TestConstants(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test_constants(self):
        """Testing constants."""
        # Test data type constants
        self.assertEqual(DATA_FLOAT, 1)
        self.assertEqual(DATA_INT, 0)
        self.assertEqual(DATA_COUNT64, 64)
        self.assertEqual(DATA_COUNT, 32)
        self.assertEqual(DATA_STRING, 2)
        self.assertEqual(DATA_NONE, None)

        # Test pattoo API constants
        self.assertEqual(
            PATTOO_API_SITE_PREFIX, '/pattoo')
        self.assertEqual(
            PATTOO_API_AGENT_PREFIX, '{}/agent'.format(PATTOO_API_SITE_PREFIX))
        self.assertEqual(
            PATTOO_API_AGENT_EXECUTABLE, 'pattoo-api-agentd')
        self.assertEqual(
            PATTOO_API_AGENT_GUNICORN_AGENT,
            '{}-gunicorn'.format(PATTOO_API_AGENT_EXECUTABLE))

        # Test agent constants
        self.assertEqual(
            PATTOO_AGENT_OS_SPOKED_API_PREFIX, '/pattoo-agent-os')
        self.assertEqual(
            PATTOO_AGENT_OS_SPOKED, 'pattoo-agent-os-spoked')
        self.assertEqual(
            PATTOO_AGENT_OS_SPOKED_PROXY,
            '{}-gunicorn'.format(PATTOO_AGENT_OS_SPOKED))
        self.assertEqual(
            PATTOO_AGENT_OS_AUTONOMOUSD, 'pattoo-agent-os-autonomousd')
        self.assertEqual(
            PATTOO_AGENT_OS_HUBD, 'pattoo-agent-os-hubd')
        self.assertEqual(
            PATTOO_AGENT_SNMPD, 'pattoo-agent-snmpd')
        self.assertEqual(
            PATTOO_AGENT_MODBUSTCPD, 'pattoo-agent-modbustcpd')


if __name__ == '__main__':
    # Make sure the environment is OK to run unittests
    UnittestConfig().create()

    # Do the unit test
    unittest.main()
