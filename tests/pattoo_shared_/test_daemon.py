#!/usr/bin/env python3
"""Test the daemon module."""

# Standard imports
import unittest
import os
import subprocess
import sys
import shlex
from time import sleep


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
from pattoo_shared import files
from pattoo_shared.daemon import Daemon, GracefulDaemon
from pattoo_shared.agent import Agent
from pattoo_shared.configuration import Config
from tests.libraries.configuration import UnittestConfig
from tests.libraries import general


def _create_agent():
    """Creates new test agent.

    Args:
        None

    Return:
        result: new agent for testing

    """
    # Return
    config = Config()
    name = general.random_agent_name()
    result = Agent(name, config=config)
    return result


def _script(_agent, action):
    """Start test daemon.

    Args:
        _agent: Agent object
        action: Action to take

    Return:
        result: Script to run

    """
    # Run script
    _path = os.path.join(ROOT_DIR, 'tests/bin/mock_daemon.py')
    result = 'python3 {} --{} --agent_name={}'.format(
        _path, action, _agent.name())
    return result


def _start(_agent):
    """Start test daemon.

    Args:
        _agent: Agent object

    Return:
        None

    """
    # Run script
    _daemonizer(_script(_agent, 'start'))


def _stop(_agent):
    """Stop test daemon.

    Args:
        _agent: Agent object

    Return:
        None

    """
    # Run script
    _daemonizer(_script(_agent, 'stop'))


def _restart(_agent):
    """Restart test daemon.

    Args:
        _agent: Agent object

    Return:
        None

    """
    # Run script
    _daemonizer(_script(_agent, 'restart'))


def _status(_agent):
    """Get daemon status.

    Args:
        _agent: Agent object

    Return:
        None

    """
    # Run script
    _daemonizer(_script(_agent, 'status'))


def _daemonizer(arguments):
    """Allows for the daemon start

    Args:
        arguments: CLI arguments

    Return:
        None

    """
    # Execute
    subprocess.call(shlex.split(arguments))


class _Run():
    """Class for creating a run method."""

    def run(self, loop=True):
        """Overriding Daemon run method

        Prints to standard output

        Args:
            loop: True when looping functionality is needed. Looping must be
                disabled when testing the run function, to avoid waiting for
                an infinite loop to end.

        Return:
            None

        """
        # Loop
        while loop:
            sleep(60)
        return True


class MockGracefulDaemon(_Run, GracefulDaemon):
    """Class to create graceful daemon for testing."""

    def __init__(self, _agent):
        """Initialize the class.

        Args:
            _agent: Agent

        Returns:
            None

        """
        # Setting up MockDaemon and starting process for testing
        GracefulDaemon.__init__(self, _agent)


class MockDaemon(_Run, Daemon):
    """Class to create daemon for testing."""

    def __init__(self, _agent):
        """Initialize the class.

        Args:
            _agent: Agent

        Returns:
            None

        """
        # Setting up MockDaemon and starting process for testing
        Daemon.__init__(self, _agent)


class TestDaemon(unittest.TestCase):
    """Test all Daemon class methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def setUp(self):
        """Test setup"""
        # Setup base config and agent
        self._config = Config()
        self._agent = _create_agent()

        # Instantiation of test daemon
        self._daemon = MockDaemon(self._agent)

    def tearDown(self):
        """Test clean up"""
        _stop(self._agent)

    def test___init__(self):
        """Testing function __init__."""
        # Check daemon name matches agent name
        self.assertEqual(self._daemon.name, self._agent.name())

        # Checking daemon pid_file
        expected = files.pid_file(self._agent.name(), self._config)
        self.assertEqual(self._daemon.pidfile, expected)

        # Checking daemon lock_file
        expected = files.lock_file(self._agent.name(), self._config)
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
        # Test starting
        self.assertFalse(os.path.exists(self._daemon.pidfile))
        _start(self._agent)
        self.assertTrue(os.path.exists(self._daemon.pidfile))

    def test_force(self):
        """Testing function force."""
        # Test starting
        self.assertFalse(os.path.exists(self._daemon.pidfile))
        _start(self._agent)
        self.assertTrue(os.path.exists(self._daemon.pidfile))

        # Calling force stop
        self._daemon.force()
        self.assertFalse(os.path.exists(self._daemon.pidfile))

    def test_stop(self):
        """Testing function stop."""
        # Test starting
        self.assertFalse(os.path.exists(self._daemon.pidfile))
        _start(self._agent)
        self.assertTrue(os.path.exists(self._daemon.pidfile))

        # Calling stop
        os.mknod(self._daemon.lockfile)
        self._daemon.stop()
        self.assertFalse(os.path.exists(self._daemon.pidfile))
        self.assertFalse(os.path.exists(self._daemon.lockfile))

    def test_restart(self):
        """Testing function restart."""
        # Initialize key variables
        sleep_time = 0.1

        # Test restarting from stop
        self.assertFalse(os.path.exists(self._daemon.pidfile))
        _restart(self._agent)
        self.assertTrue(os.path.exists(self._daemon.pidfile))

        # Sleep
        _start = os.stat(self._daemon.pidfile).st_mtime
        sleep(sleep_time)

        # Test restarting from start
        _restart(self._agent)
        self.assertTrue(os.path.exists(self._daemon.pidfile))

        # Test age of PID file
        _stop = os.stat(self._daemon.pidfile).st_mtime
        self.assertTrue(_stop > _start)
        self.assertTrue(_stop - _start >= sleep_time)

    def test_status(self):
        """Testing function status."""
        # Test starting
        self.assertFalse(os.path.exists(self._daemon.pidfile))
        _start(self._agent)
        self.assertTrue(os.path.exists(self._daemon.pidfile))

        # Test stopping
        # Test start
        result = self._daemon.status()
        self.assertTrue(result)

        _stop(self._agent)
        self.assertFalse(os.path.exists(self._daemon.pidfile))

        # Test start
        result = self._daemon.status()
        self.assertFalse(result)

    def test_run(self):
        """Testing function run."""
        # Test
        result = self._daemon.run(loop=False)
        self.assertTrue(result)


class TestGracefulDaemon(TestDaemon):
    """Test all GracefulDaemon class methods."""

    def setUp(self):
        """Test setup"""
        # Setup base config and agent
        self._config = Config()
        self._agent = _create_agent()

        # Instantiation of test daemon
        self._daemon = MockGracefulDaemon(self._agent)

    def graceful_fn(self, callback):
        """Set up and execute test callback to implement graceful shutdown.

        Args:
            callback: function that implements graceful shutdown functionality

        Return:
            wrapper: Implements setup before using callback and making
            assertions

        """
        def wrapper():
            """Wrapper function to be returned by graceful_fn"""
            # Testing proper graceful shutdown by creating lock file to
            # simulate that a process is currently handling data.
            _start(self._agent)
            os.mknod(self._daemon.lockfile)
            self.assertTrue(os.path.exists(self._daemon.lockfile))
            callback()

            # Checking that both daemon pidfile and lockfile do not exist,
            # which indicates successful stoppage of daemon.
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
        self.graceful_fn(_restart(self._agent))


if __name__ == '__main__':
    # Make sure the environment is OK to run unittests
    UnittestConfig().create()

    # Do the unit test
    unittest.main()
