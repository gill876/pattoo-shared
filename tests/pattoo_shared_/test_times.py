#!/usr/bin/env python3
"""Test the times module."""

# Standard imports
import unittest
import os
import sys

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
from pattoo_shared import times
from tests.libraries.configuration import UnittestConfig


class TestBasicFunctions(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################
    def test_validate_timestamp(self):
        """Testing function validate_timestamp."""
        # Initialize key variables
        result = times.validate_timestamp(300, 300)
        self.assertEqual(result, True)
        result = times.validate_timestamp(400, 300)
        self.assertEqual(result, False)
        result = times.validate_timestamp(500, 300)
        self.assertEqual(result, False)
        result = times.validate_timestamp(500, '300')
        self.assertEqual(result, False)
        result = times.validate_timestamp('500', 300)
        self.assertEqual(result, False)
        result = times.validate_timestamp(500, 0)
        self.assertEqual(result, False)

    def test_normalized_timestamp(self):
        """Testing function normalized_timestamp."""
        # Initialize key variables
        polling_interval = 300

        timestamp = 31
        result = times.normalized_timestamp(
            polling_interval, timestamp=timestamp)
        self.assertEqual(result, 0)

        timestamp = 301
        result = times.normalized_timestamp(
            polling_interval, timestamp=timestamp)
        self.assertEqual(result, 300)

        timestamp = 900
        result = times.normalized_timestamp(
            polling_interval, timestamp=timestamp)
        self.assertEqual(result, 900)

        timestamp = 1000
        result = times.normalized_timestamp(
            polling_interval, timestamp=timestamp)
        self.assertEqual(result, 900)

        # Initialize key variables
        polling_interval = 30

        timestamp = 31
        result = times.normalized_timestamp(
            polling_interval, timestamp=timestamp)
        self.assertEqual(result, 30)

        timestamp = 301
        result = times.normalized_timestamp(
            polling_interval, timestamp=timestamp)
        self.assertEqual(result, 300)

        timestamp = 900
        result = times.normalized_timestamp(
            polling_interval, timestamp=timestamp)
        self.assertEqual(result, 900)

        timestamp = 1000
        result = times.normalized_timestamp(
            polling_interval, timestamp=timestamp)
        self.assertEqual(result, 990)

        # Test with boolean None values
        timestamp = 900001
        for polling_interval in [None, [], False, {}]:
            result = times.normalized_timestamp(
                polling_interval, timestamp=timestamp)
            self.assertEqual(result, 900000)

        # Test with non integer values
        timestamp = 300
        for polling_interval in ['1', [1]]:
            with self.assertRaises(SystemExit):
                times.normalized_timestamp(
                    polling_interval, timestamp=timestamp)

    def test_timestamps(self):
        """Testing function timestamps."""
        # Test
        ts_start = 0
        ts_stop = 100
        polling_interval = 10
        expected = list(range(
            ts_start, ts_stop + polling_interval, polling_interval))
        result = times.timestamps(ts_start, ts_stop, polling_interval)
        self.assertEqual(result, expected)

        # Test with more irregular values
        ts_start = 11
        ts_stop = 73
        polling_interval = 13
        expected = [0, 13, 26, 39, 52, 65]
        result = times.timestamps(ts_start, ts_stop, polling_interval)
        self.assertEqual(result, expected)


if __name__ == '__main__':
    # Make sure the environment is OK to run unittests
    UnittestConfig().create()

    # Do the unit test
    unittest.main()
