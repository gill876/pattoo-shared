#!/usr/bin/env python3
"""Test the daemon module."""

# Standard imports
import unittest
import os
import subprocess
import sys
from io import StringIO
from unittest.mock import patch


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
from pattoo_shared import files
from pattoo_shared.daemon import Daemon, GracefulDaemon
from pattoo_shared.agent import Agent
from pattoo_shared.configuration import Config
from tests.libraries.configuration import UnittestConfig

# TEST CONSTANTS
AGENT_NAME = 'parent'
_config = Config()

def handle_daemon(command):
    """Allows for the daemon start

    Args:
        command: either --start/--restart to test

    Return:
        None

    """
    daemon_start_script_path = os.path.join(EXEC_DIR, 'daemon_start_test_script.py')
    subprocess.call(['python', daemon_start_script_path, command])

def create_agent():
    """Creates new agent for use in testing start and restart

    Args:
        None

    Return:
        _agent: new agent for testing

    """
    _agent = Agent(parent=AGENT_NAME, config=_config)
    return _agent

class MockDaemonMixin():
    """Mixin definging run functoin for MockDaemon and MockGracefulDaemon"""

    def run(self, loop=True):
        """Overriding Daemon run method

        Prints to standard output

        Args:
            loop: determines looping functionality is needed, used to test
            daemon start

        Return:
            None

        """
        print('Running')
        while loop:
            pass


class MockDaemon(MockDaemonMixin, Daemon):
    """Mock Daemon used to test Daemon class

    Built to provide minimal functionality to test Daemon run method

    """

class MockGracefulDaemon(MockDaemonMixin, GracefulDaemon):
    """Mock Graceful Daemon used to test Graceful Daemon class

    Built to provide minimal functionality to test Graceful Daemon run method

    """

class TestDaemon(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def setUp(self):
        """Test setup"""

        # Setup base config and agent
        self._agent = create_agent()
        self._config = _config

        # Instantiation of test daemon
        self._daemon = MockDaemon(self._agent)

    def tearDown(self):
        """Test clean up"""
        self._config = None
        self._agent = None

        # Removing any relate lock file
        if os.path.exists(self._daemon.lockfile):
            os.remove(self._daemon.lockfile)
        if os.path.exists(self._daemon.pidfile):
            os.remove(self._daemon.pidfile)

        self._daemon = None

    def test___init__(self):
        """Testing function __init__."""
        # Check daemon name matches agent name
        self.assertEqual(self._daemon.name, AGENT_NAME)

        # Checking daemon config
        self.assertEqual(self._daemon._config, self._config)
        self.assertEqual(self._daemon._config, self._config)

        # Checking daemon pid_file
        expected = files.pid_file(AGENT_NAME, self._config)
        self.assertEqual(self._daemon.pidfile, expected)

        # Checking daemon lock_file
        expected = files.lock_file(AGENT_NAME, self._config)
        self.assertEqual(self._daemon.lockfile, expected)

    def test__daemonize(self):
        """Testing function _daemonize."""
        pass

    def test_delpid(self):
        """Testing function delpid."""

        # Creating daemon Process ID file(pidfile)
        os.mknod(self._daemon.pidfile)

        # Checking that pid file has been created
        self.assertTrue(os.path.exists(self._daemon.pidfile))

        # Delete pid file
        self._daemon.delpid()

        # Check that pidfile of the daemon has been deleted
        self.assertFalse(os.path.exists(self._daemon.pidfile))

    def test_dellock(self):
        """Testing function dellock."""

        # Creating daemon Process ID file(pidfile)
        os.mknod(self._daemon.lockfile)

        # Checking that pid file has been created
        self.assertTrue(os.path.exists(self._daemon.lockfile))

        # Delete pid file
        self._daemon.dellock()

        # Check that pidfile of the daemon has been deleted
        self.assertFalse(os.path.exists(self._daemon.lockfile))

    def test_start(self):
        """Testing function start."""
        handle_daemon('--start')
        self.assertTrue(os.path.exists(self._daemon.pidfile))

    def test_force(self):
        """Testing function force."""

        # Staring Daemon
        handle_daemon('--start')
        self.assertTrue(os.path.exists(self._daemon.pidfile))

        # Calling force stop
        self._daemon.force()
        self.assertFalse(os.path.exists(self._daemon.pidfile))

    def test_stop(self):
        """Testing function stop."""

        # Staring Daemon
        handle_daemon('--start')
        self.assertTrue(os.path.exists(self._daemon.pidfile))
        os.mknod(self._daemon.lockfile)

        # Calling force stop
        self._daemon.stop()
        self.assertFalse(os.path.exists(self._daemon.pidfile))
        self.assertFalse(os.path.exists(self._daemon.lockfile))

    def test_restart(self):
        """Testing function restart."""

        # Creating daemon pidfile
        with open(self._daemon.pidfile, 'w') as f:
            f.write('99999')
        self.assertTrue(os.path.exists(self._daemon.pidfile))

        # Checking daemon restarting, pidfile should exist
        handle_daemon('--restart')
        self.assertTrue(os.path.exists(self._daemon.pidfile))

    def test_status(self):
        """Testing function status."""

        # Test status while daemon is running
        handle_daemon('--start')
        expected = 'Daemon is running - {}\n'.format(AGENT_NAME)

        with patch('sys.stdout', new = StringIO()) as result:
            self._daemon.status()
            self.assertEqual(result.getvalue(), expected)

        # Test status when daemon has been stopped
        os.remove(self._daemon.pidfile)
        expected = 'Daemon is stopped - {}\n'.format(AGENT_NAME)

        with patch('sys.stdout', new = StringIO()) as result:
            self._daemon.status()
            self.assertEqual(result.getvalue(), expected)

    def test_run(self):
        """Testing function run."""
        expected = 'Running\n'
        with patch('sys.stdout', new = StringIO()) as result:
            self._daemon.run(loop=False)
            self.assertEqual(result.getvalue(), expected)

class TestGracefulDaemon(TestDaemon):
    """

    Checks that daemon start/stop commands confirm to graceful shutdown

    """

    def setUp(self):
        """Test setup"""

        # Setup base config and agent
        self._agent = create_agent()
        self._config = _config

        # Instantiation of test daemon
        self._daemon = MockGracefulDaemon(self._agent)

    def graceful_fn(self, callback):
        """Sets up and executes test callback that should implement graceful
        shutdown

        Args:
            callback: function that implements graceful shutdown functionality

        Return:
            wrapper: implements setup before using callback and making
            assertions

        """
        def wrapper():
            """Wrapper function to be returned by graceful_fn"""
            # Testing proper graceful shutdown by creating lock file to simulate
            # that a process is currently handling data.
            handle_daemon('--start')
            os.mknod(self._daemon.lockfile)
            self.assertTrue(os.path.exists(self._daemon.lockfile))
            callback()

            # Checking that both daemon pidfile and lockfile do not exist, which
            # indicates successful stoppage of daemon.
            self.assertFalse(os.path.exists(self._daemon.lockfile))
            self.assertFalse(os.path.exists(self._daemon.pidfile))

        return wrapper

    def test_stop(self):
        """Testing graceful stop function"""

        # Test base Daemon stop functionality
        # When lock file does not exist
        super(TestGracefulDaemon, self).test_stop()

        # Graceful stop testing
        self.graceful_fn(self._daemon.stop())

    def test_restart(self):
        """Testing graceful restart function"""

        # Test base Daemon restart functionality
        # When lock file does not exist
        super(TestGracefulDaemon, self).test_restart()

        # Graceful stop testing
        self.graceful_fn(handle_daemon('--restart'))

if __name__ == '__main__':
    # Make sure the environment is OK to run unittests
    UnittestConfig().create()

    # Do the unit test
    unittest.main()
