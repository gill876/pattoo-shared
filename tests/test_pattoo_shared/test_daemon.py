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


class Test_Directory(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test___init__(self):
        """Testing function __init__."""
        # Test
        directory = daemon._Directory()
        config = Config()
        expected = config.daemon_directory()
        result = directory._root
        self.assertEqual(result, expected)

    def test_pid(self):
        """Testing function pid."""
        # Test
        directory = daemon._Directory()
        config = Config()
        expected = '{}/pid'.format(config.daemon_directory())
        result = directory.pid()
        self.assertEqual(result, expected)

    def test_lock(self):
        """Testing function lock."""
        # Test
        directory = daemon._Directory()
        config = Config()
        expected = '{}/lock'.format(config.daemon_directory())
        result = directory.lock()
        self.assertEqual(result, expected)

    def test_agent_id(self):
        """Testing function agent_id."""
        # Test
        directory = daemon._Directory()
        config = Config()
        expected = '{}/agent_id'.format(config.daemon_directory())
        result = directory.agent_id()
        self.assertEqual(result, expected)


class Test_File(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    prefix = 'unittest'
    agent_hostname = 'pattoo_host'

    def test___init__(self):
        """Testing function __init__."""
        pass

    def test_pid(self):
        """Testing function pid."""
        # Test
        filename = daemon._File()
        result = filename.pid(self.prefix)
        self.assertTrue(os.path.isdir(os.path.dirname(result)))

    def test_lock(self):
        """Testing function lock."""
        # Test
        filename = daemon._File()
        result = filename.lock(self.prefix)
        self.assertTrue(os.path.isdir(os.path.dirname(result)))

    def test_agent_id(self):
        """Testing function agent_id."""
        filename = daemon._File()
        result = filename.agent_id(self.prefix, self.agent_hostname)
        self.assertTrue(os.path.isdir(os.path.dirname(result)))


class TestBasicFunctions(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    prefix = 'unittest'
    agent_hostname = 'pattoo_host'

    def test_pid_file(self):
        """Testing function pid_file."""
        # Test
        filename = daemon._File()
        expected = filename.pid(self.prefix)
        result = daemon.pid_file(self.prefix)
        self.assertEqual(result, expected)

    def test_lock_file(self):
        """Testing function lock_file."""
        # Test
        filename = daemon._File()
        expected = filename.lock(self.prefix)
        result = daemon.lock_file(self.prefix)
        self.assertEqual(result, expected)

    def test_agent_id_file(self):
        """Testing function agent_id_file."""
        # Test
        filename = daemon._File()
        expected = filename.agent_id(self.prefix, self.agent_hostname)
        result = daemon.agent_id_file(self.prefix, self.agent_hostname)
        self.assertEqual(result, expected)


if __name__ == '__main__':
    # Make sure the environment is OK to run unittests
    UnittestConfig().create()

    # Do the unit test
    unittest.main()
