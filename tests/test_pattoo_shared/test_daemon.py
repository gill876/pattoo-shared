#!/usr/bin/env python3
"""Test the daemon module."""

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
from pattoo_shared import daemon
from pattoo_shared.configuration import Config
from tests.libraries.configuration import UnittestConfig


class TestDaemon(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test___init__(self):
        """Testing function __init__."""
        pass

    def test__daemonize(self):
        """Testing function _daemonize."""
        pass

    def test_delpid(self):
        """Testing function delpid."""
        pass

    def test_dellock(self):
        """Testing function dellock."""
        pass

    def test_start(self):
        """Testing function start."""
        pass

    def test_force(self):
        """Testing function force."""
        pass

    def test_stop(self):
        """Testing function stop."""
        pass

    def test_restart(self):
        """Testing function restart."""
        pass

    def test_status(self):
        """Testing function status."""
        pass

    def test_run(self):
        """Testing function run."""
        pass


if __name__ == '__main__':
    # Make sure the environment is OK to run unittests
    UnittestConfig().create()

    # Do the unit test
    unittest.main()
