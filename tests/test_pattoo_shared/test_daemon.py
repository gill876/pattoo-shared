#!/usr/bin/env python3
"""Test the daemon module."""

# Standard imports
import unittest
import os
import subprocess
import sys
import shlex
from time import sleep
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
from tests.libraries import general


def _start(agent_name):
    """Start test daemon.

    Args:
        agent_name: Name of agent

    Return:
        None

    """
    # Run script
    arguments = '--start --agent_name={}'.format(agent_name)
    _daemonizer(arguments)


def _stop(agent_name):
    """Stop test daemon.

    Args:
        agent_name: Name of agent

    Return:
        None

    """
    # Run script
    arguments = '--stop --agent_name={}'.format(agent_name)
    _daemonizer(arguments)


def _restart(agent_name):
    """Restart test daemon.

    Args:
        agent_name: Name of agent

    Return:
        None

    """
    # Run script
    arguments = '--restart --agent_name={}'.format(agent_name)
    _daemonizer(arguments)


def _daemonizer(arguments):
    """Allows for the daemon start

    Args:
        arguments: CLI arguments

    Return:
        None

    """
    _path = os.path.join(ROOT_DIR, 'tests/bin/mock_daemon.py')
    script = 'python3 {} {}'.format(_path, arguments)
    args = shlex.split(script)

    # Spawn script
    process = subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutdata, stderrdata = process.communicate()
    returncode = process.returncode

    # Crash if the return code is not 0
    if returncode != 0:
        print('''\
Error Running: {0}
Return Code  : {1}
STDOUT       :
{2}
STDERR       :
{3}
'''.format(script, returncode, stdoutdata.decode(), stderrdata.decode()))


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
        print('Running')
        while loop:
            sleep(60)


class MockGracefulDaemon(_Run, GracefulDaemon):
    """Class to create graceful daemon for testing."""

    def __init__(self, agent_name):
        """Initialize the class.

        Args:
            agent_name: Name of agent

        Returns:
            None

        """
        # Setting up MockDaemon and starting process for testing
        config = Config()
        _agent = Agent(agent_name, config=config)
        GracefulDaemon.__init__(self, _agent)


class MockDaemon(_Run, Daemon):
    """Class to create daemon for testing."""

    def __init__(self, agent_name):
        """Initialize the class.

        Args:
            agent_name: Name of agent

        Returns:
            None

        """
        # Setting up MockDaemon and starting process for testing
        config = Config()
        _agent = Agent(agent_name, config=config)
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
        self._agent = general.random_agent_name()

        # Instantiation of test daemon
        self._daemon = MockDaemon(self._agent)

    def tearDown(self):
        """Test clean up"""
        _stop(self._agent)

    def test___init__(self):
        """Testing function __init__."""
        # Check daemon name matches agent name
        self.assertEqual(self._daemon.name, self._agent)

        # Checking daemon pid_file
        expected = files.pid_file(self._agent, self._config)
        self.assertEqual(self._daemon.pidfile, expected)

        # Checking daemon lock_file
        expected = files.lock_file(self._agent, self._config)
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

        # Test status while daemon is running
        expected = 'Daemon is running - {}\n'.format(self._agent)

        # Intercept output
        with patch('sys.stdout', new=StringIO()) as result:
            self._daemon.status()
            self.assertEqual(result.getvalue(), expected)

        # Test status when daemon has been stopped
        os.remove(self._daemon.pidfile)
        expected = 'Daemon is stopped - {}\n'.format(self._agent)

        with patch('sys.stdout', new=StringIO()) as result:
            self._daemon.status()
            self.assertEqual(result.getvalue(), expected)

    def test_run(self):
        """Testing function run."""
        expected = 'Running\n'
        with patch('sys.stdout', new=StringIO()) as result:
            self._daemon.run(loop=False)
            self.assertEqual(result.getvalue(), expected)


class TestGracefulDaemon(TestDaemon):
    """Test all GracefulDaemon class methods."""

    def setUp(self):
        """Test setup"""

        # Setup base config and agent
        self._config = Config()
        self._agent = general.random_agent_name()

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
