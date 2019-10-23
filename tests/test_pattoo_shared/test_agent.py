#!/usr/bin/env python3
"""Test the daemon module."""

# Standard imports
import unittest
import os
import sys
import multiprocessing
from random import random


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
from pattoo_shared import agent, daemon
from pattoo_shared.configuration import Config
from pattoo_shared.variables import AgentAPIVariable
from tests.libraries.configuration import UnittestConfig


class TestAgent(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test___init__(self):
        """Testing method / function __init__."""
        # Initialize key variables
        parent = 'parent'
        child = 'child'

        # Test - No Child
        tester = agent.Agent(parent)
        self.assertEqual(tester.parent, parent)
        expected = daemon.pid_file(parent)
        self.assertEqual(tester.pidfile_parent, expected)
        expected = daemon.lock_file(parent)
        self.assertEqual(tester.lockfile_parent, expected)
        expected = daemon.pid_file(None)
        self.assertEqual(tester._pidfile_child, expected)

        # Test - With Child
        tester = agent.Agent(parent, child=child)
        self.assertEqual(tester.parent, parent)
        expected = daemon.pid_file(parent)
        self.assertEqual(tester.pidfile_parent, expected)
        expected = daemon.lock_file(parent)
        self.assertEqual(tester.lockfile_parent, expected)
        expected = daemon.pid_file(child)
        self.assertEqual(tester._pidfile_child, expected)

    def test_name(self):
        """Testing method / function name."""
        # Initialize key variables
        parent = 'parent'

        # Test
        tester = agent.Agent(parent)
        self.assertEqual(tester.name(), parent)

    def test_query(self):
        """Testing method / function query."""
        pass


class TestAgentDaemon(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test___init__(self):
        """Testing method / function __init__."""
        pass

    def test_run(self):
        """Testing method / function run."""
        pass


class TestAgentCLI(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test___init__(self):
        """Testing method / function __init__."""
        pass

    def test_process(self):
        """Testing method / function process."""
        pass

    def test_control(self):
        """Testing method / function control."""
        pass


class TestAgentAPI(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test___init__(self):
        """Testing method / function __init__."""
        pass

    def test_query(self):
        """Testing method / function query."""
        pass


class Test_StandaloneApplication(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test___init__(self):
        """Testing method / function __init__."""
        pass

    def test_load_config(self):
        """Testing method / function load_config."""
        pass

    def test_load(self):
        """Testing method / function load."""
        pass


class TestBasicFunctions(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test__number_of_workers(self):
        """Testing method / function _number_of_workers."""
        # Test
        expected = (multiprocessing.cpu_count() * 2) + 1
        result = agent._number_of_workers()
        self.assertEqual(result, expected)

    def test__ip_binding(self):
        """Testing method / function _ip_binding."""
        # Test with Hostname
        listen_address = 'localhost'
        ip_bind_port = '1000'
        agent_api_variable = AgentAPIVariable(
            ip_bind_port=ip_bind_port, listen_address=listen_address)
        result = agent._ip_binding(agent_api_variable)
        expected = 'localhost:1000'
        self.assertEqual(result, expected)

        # Test with IPv4
        listen_address = '1.2.3.4'
        ip_bind_port = '5678'
        agent_api_variable = AgentAPIVariable(
            ip_bind_port=ip_bind_port, listen_address=listen_address)
        result = agent._ip_binding(agent_api_variable)
        expected = '1.2.3.4:5678'
        self.assertEqual(result, expected)

        # Test with IPv6
        listen_address = '1::1'
        ip_bind_port = '91011'
        agent_api_variable = AgentAPIVariable(
            ip_bind_port=ip_bind_port, listen_address=listen_address)
        result = agent._ip_binding(agent_api_variable)
        expected = '[1::1]:91011'
        self.assertEqual(result, expected)

    def test_get_agent_id(self):
        """Testing method / function get_agent_id."""
        # Test. Agent_id shouldn't change
        agent_name = random()
        agent_hostname = random()
        expected = agent.get_agent_id(agent_name, agent_hostname)
        result = agent.get_agent_id(agent_name, agent_hostname)
        self.assertEqual(result, expected)

    def test__generate_agent_id(self):
        """Testing method / function _generate_agent_id."""
        pass


if __name__ == '__main__':
    # Make sure the environment is OK to run unittests
    UnittestConfig().create()

    # Do the unit test
    unittest.main()
