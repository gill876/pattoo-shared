#!/usr/bin/env python3
"""Test the daemon module."""

# Standard imports
import unittest
import os
import sys
import multiprocessing


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
from pattoo_shared import agent, files
from pattoo_shared.configuration import Config
from pattoo_shared.variables import AgentAPIVariable
from tests.libraries.configuration import UnittestConfig

# Test Daemon importation
from tests.test_pattoo_shared.test_daemon import  TestDaemon, TestGracefulDaemon, AGENT_NAME

class TestAgent(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    config = Config()

    def test___init__(self):
        """Testing method or function named __init__."""
        # Initialize key variables
        parent = 'parent'
        child = 'child'

        # Test - No Child
        tester = agent.Agent(parent)
        self.assertEqual(tester.parent, parent)
        expected = files.pid_file(parent, self.config)
        self.assertEqual(tester.pidfile_parent, expected)
        expected = files.lock_file(parent, self.config)
        self.assertEqual(tester.lockfile_parent, expected)
        expected = files.pid_file(None, self.config)
        self.assertEqual(tester._pidfile_child, expected)

        # Test - With Child
        tester = agent.Agent(parent, child=child)
        self.assertEqual(tester.parent, parent)
        expected = files.pid_file(parent, self.config)
        self.assertEqual(tester.pidfile_parent, expected)
        expected = files.lock_file(parent, self.config)
        self.assertEqual(tester.lockfile_parent, expected)
        expected = files.pid_file(child, self.config)
        self.assertEqual(tester._pidfile_child, expected)

    def test_name(self):
        """Testing method or function named name."""
        # Initialize key variables
        parent = 'parent'

        # Test
        tester = agent.Agent(parent)
        self.assertEqual(tester.name(), parent)

    def test_query(self):
        """Testing method or function named query."""
        pass


class TestBaseAgentDaemon(TestDaemon):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def setUp(self):
        """Test setup"""

        # Setup base config and agent
        self._config = Config()
        self._agent = agent.Agent(parent=AGENT_NAME, config=self._config)

        # Instantiation of test daemon
        self._daemon = agent.BaseAgentDaemon(self._agent)

    def test_run(self):
        """Testing method or function named run."""
        pass

class TestGracefulAgentDaemon(TestGracefulDaemon):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def setUp(self):
        """Test setup"""

        # Setup base config and agent
        self._config = Config()
        self._agent = agent.Agent(parent=AGENT_NAME, config=self._config)

        # Instantiation of test daemon
        self._daemon = agent.GracefulAgentDaemon(self._agent)

    def test_run(self):
        """Testing method or function named run."""
        pass

class TestAgentCLI(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test___init__(self):
        """Testing method or function named __init__."""
        pass

    def test_process(self):
        """Testing method or function named process."""
        pass

    def test_control(self):
        """Testing method or function named control."""
        pass


class TestAgentAPI(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test___init__(self):
        """Testing method or function named __init__."""
        pass

    def test_query(self):
        """Testing method or function named query."""
        pass


class Test_StandaloneApplication(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test___init__(self):
        """Testing method or function named __init__."""
        pass

    def test_load_config(self):
        """Testing method or function named load_config."""
        pass

    def test_load(self):
        """Testing method or function named load."""
        pass


class TestBasicFunctions(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test__number_of_workers(self):
        """Testing method or function named _number_of_workers."""
        # Test
        expected = (multiprocessing.cpu_count() * 2) + 1
        result = agent._number_of_workers()
        self.assertEqual(result, expected)

    def test__ip_binding(self):
        """Testing method or function named _ip_binding."""
        # Test with Hostname
        ip_listen_address = 'localhost'
        ip_bind_port = '1000'
        agent_api_variable = AgentAPIVariable(
            ip_bind_port=ip_bind_port, ip_listen_address=ip_listen_address)
        result = agent._ip_binding(agent_api_variable)
        expected = 'localhost:1000'
        self.assertEqual(result, expected)

        # Test with IPv4
        ip_listen_address = '1.2.3.4'
        ip_bind_port = '5678'
        agent_api_variable = AgentAPIVariable(
            ip_bind_port=ip_bind_port, ip_listen_address=ip_listen_address)
        result = agent._ip_binding(agent_api_variable)
        expected = '1.2.3.4:5678'
        self.assertEqual(result, expected)

        # Test with IPv6
        ip_listen_address = '1::1'
        ip_bind_port = '91011'
        agent_api_variable = AgentAPIVariable(
            ip_bind_port=ip_bind_port, ip_listen_address=ip_listen_address)
        result = agent._ip_binding(agent_api_variable)
        expected = '[1::1]:91011'
        self.assertEqual(result, expected)


if __name__ == '__main__':
    # Make sure the environment is OK to run unittests
    UnittestConfig().create()

    # Do the unit test
    unittest.main()
