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
from pattoo_shared import log
from tests.libraries.configuration import UnittestConfig


class Test_GetLog(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################
    def test_check_environment(self):
        """Testing function check_environment."""
        pass

    def test_logfile(self):
        """Testing function logfile."""
        pass

    def test_stdout(self):
        """Testing function stdout."""
        pass


class TestBasicFunctions(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    message = 'PATTOOs are Jamaican Owls'
    code = 99

    def test_check_environment(self):
        """Testing function check_environment."""
        pass

    def test_log2console(self):
        """Testing function log2console."""
        # Test should not cause script to crash
        log.log2console(self.code, self.message)

    def test_log2die_safe(self):
        """Testing function log2die_safe."""
        # Test
        with self.assertRaises(SystemExit):
            log.log2die_safe(self.code, self.message)

    def test_log2warning(self):
        """Testing function log2warning."""
        # Test should not cause script to crash
        log.log2warning(self.code, self.message)

    def test_log2debug(self):
        """Testing function log2debug."""
        # Test should not cause script to crash
        log.log2debug(self.code, self.message)

    def test_log2info(self):
        """Testing function log2info."""
        # Test should not cause script to crash
        log.log2info(self.code, self.message)

    def test_log2see(self):
        """Testing function log2see."""
        # Test should not cause script to crash
        log.log2see(self.code, self.message)

    def test_log2die(self):
        """Testing function log2die."""
        # Test
        with self.assertRaises(SystemExit):
            log.log2die(self.code, self.message)

    def test__logit(self):
        """Testing function _logit."""
        pass

    def test__logger_file(self):
        """Testing function _logger_file."""
        pass

    def test__logger_stdout(self):
        """Testing function _logger_stdout."""
        pass

    def test__message(self):
        """Testing function _message."""
        # Test message for errors
        result = log._message(self.code, self.message, error=True)
        self.assertEqual(result.endswith(
            ' - ERROR - [99] PATTOOs are Jamaican Owls'), True)

        # Test message for non-errors
        result = log._message(self.code, self.message, error=False)
        self.assertEqual(result.endswith(
            ' - STATUS - [99] PATTOOs are Jamaican Owls'), True)


if __name__ == '__main__':
    # Make sure the environment is OK to run unittests
    UnittestConfig().create()

    # Do the unit test
    unittest.main()
