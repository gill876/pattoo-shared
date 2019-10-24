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
from pattoo_shared import variables
from pattoo_shared.constants import DATA_INT, DATA_STRING
from pattoo_shared.variables import (
    DataVariable, DataVariablesHost, AgentPolledData, AgentAPIVariable)
from tests.libraries.configuration import UnittestConfig


class TestDataVariable(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test___init__(self):
        """Testing function __init__."""
        # Setup DataVariable
        value = 1093454
        data_label = 'testing'
        data_index = 98766
        data_type = DATA_INT
        variable = DataVariable(
            value=value, data_label=data_label, data_index=data_index,
            data_type=data_type)

        # Test each variable
        self.assertEqual(variable.data_type, data_type)
        self.assertEqual(variable.value, value)
        self.assertEqual(variable.data_label, data_label)
        self.assertEqual(variable.data_index, data_index)

    def test___repr__(self):
        """Testing function __repr__."""
        # Setup DataVariable
        value = 10
        data_label = 'testing'
        data_index = 10
        data_type = DATA_INT
        variable = DataVariable(
            value=value, data_label=data_label, data_index=data_index,
            data_type=data_type)

        # Test
        expected = ('''\
<DataVariable value=10 data_label='testing', data_index=10, data_type=0>''')
        result = variable.__repr__()
        self.assertEqual(result, expected)


class TestDataVariablesHost(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test___init__(self):
        """Testing function __init__."""
        # Setup DataVariablesHost
        device = 'localhost'
        variableshost = DataVariablesHost(device)

        # Test initial vlues
        self.assertEqual(variableshost.device, device)
        self.assertFalse(variableshost.active)
        self.assertEqual(variableshost.data, [])

    def test_append(self):
        """Testing function append."""
        # Initialize DataVariablesHost
        device = 'teddy_bear'
        variableshost = DataVariablesHost(device)
        self.assertEqual(variableshost.device, device)
        self.assertFalse(variableshost.active)
        self.assertEqual(variableshost.data, [])

        # Setup DataVariable
        value = 457
        data_label = 'gummy_bear'
        data_index = 999
        data_type = DATA_INT
        variable = DataVariable(
            value=value, data_label=data_label, data_index=data_index,
            data_type=data_type)

        # Test append
        variableshost.append(None)
        self.assertEqual(variableshost.data, [])

        variableshost.append(variable)
        self.assertTrue(bool(variableshost.data))
        self.assertTrue(isinstance(variableshost.data, list))
        self.assertEqual(len(variableshost.data), 1)

        # Test the values in the variable
        _variable = variableshost.data[0]
        self.assertEqual(_variable.data_type, data_type)
        self.assertEqual(_variable.value, value)
        self.assertEqual(_variable.data_label, data_label)
        self.assertEqual(_variable.data_index, data_index)

    def test_extend(self):
        """Testing function extend."""
        # Initialize DataVariablesHost
        device = 'teddy_bear'
        variableshost = DataVariablesHost(device)
        self.assertEqual(variableshost.device, device)
        self.assertFalse(variableshost.active)
        self.assertEqual(variableshost.data, [])

        # Setup DataVariable
        value = 32138
        data_label = 'grizzly_bear'
        data_index = 'qwerty'
        data_type = DATA_STRING
        variable = DataVariable(
            value=value, data_label=data_label, data_index=data_index,
            data_type=data_type)

        # Test append
        variableshost.extend(None)
        self.assertEqual(variableshost.data, [])
        variableshost.extend(variable)
        self.assertEqual(variableshost.data, [])

        variableshost.extend([variable])
        self.assertTrue(bool(variableshost.data))
        self.assertTrue(isinstance(variableshost.data, list))
        self.assertEqual(len(variableshost.data), 1)

        # Test the values in the variable
        _variable = variableshost.data[0]
        self.assertEqual(_variable.data_type, data_type)
        self.assertEqual(_variable.value, value)
        self.assertEqual(_variable.data_label, data_label)
        self.assertEqual(_variable.data_index, data_index)


class TestAgentPolledData(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test___init__(self):
        """Testing function __init__."""
        # Setup AgentPolledData variable
        agent_id = 'polar_bear'
        agent_program = 'brown_bear'
        agent_hostname = 'localhost'
        timestamp = 68
        polling_interval = 30
        apd = AgentPolledData(
            agent_id, agent_program, agent_hostname,
            timestamp=timestamp, polling_interval=polling_interval)

        # Test
        self.assertEqual(apd.timestamp, 60)
        self.assertEqual(apd.polling_interval, 30)
        self.assertEqual(apd.agent_id, agent_id)
        self.assertEqual(apd.agent_program, agent_program)
        self.assertEqual(apd.agent_hostname, agent_hostname)
        self.assertFalse(apd.active)

    def test___repr__(self):
        """Testing function __repr__."""
        # Setup AgentPolledData
        agent_id = 'polar_bear'
        agent_program = 'brown_bear'
        agent_hostname = 'localhost'
        timestamp = 68
        polling_interval = 30
        apd = AgentPolledData(
            agent_id, agent_program, agent_hostname,
            timestamp=timestamp, polling_interval=polling_interval)

        # Test
        expected = ('''\
<AgentPolledData agent_id='polar_bear' agent_program='brown_bear', \
agent_hostname='localhost', timestamp=60 polling_interval=30, active=False>''')
        result = apd.__repr__()
        self.assertEqual(result, expected)

    def test_append(self):
        """Testing function append."""
        # Setup AgentPolledData
        agent_id = 'koala_bear'
        agent_program = 'panda_bear'
        agent_hostname = 'localhost'
        timestamp = 68
        polling_interval = 30
        apd = AgentPolledData(
            agent_id, agent_program, agent_hostname,
            timestamp=timestamp, polling_interval=polling_interval)

        # Initialize DataVariablesHost
        device = 'teddy_bear'
        variableshost = DataVariablesHost(device)
        self.assertEqual(variableshost.device, device)
        self.assertFalse(variableshost.active)
        self.assertEqual(variableshost.data, [])

        # Setup DataVariable
        value = 457
        data_label = 'gummy_bear'
        data_index = 999
        data_type = DATA_INT
        variable = DataVariable(
            value=value, data_label=data_label, data_index=data_index,
            data_type=data_type)

        # Add data to DataVariablesHost
        self.assertFalse(variableshost.active)
        variableshost.append(variable)
        self.assertTrue(variableshost.active)

        # Test append
        self.assertFalse(apd.active)
        apd.append(None)
        self.assertFalse(apd.active)
        apd.append(variable)
        self.assertFalse(apd.active)
        apd.append(variableshost)
        self.assertTrue(apd.active)

        # Test contents
        data = apd.data
        self.assertTrue(isinstance(data, list))
        self.assertEqual(len(data), 1)

        dvh = data[0]
        self.assertTrue(isinstance(dvh, DataVariablesHost))
        self.assertEqual(dvh.device, device)
        self.assertTrue(dvh.active)
        self.assertTrue(isinstance(dvh.data, list))
        self.assertTrue(len(dvh.data), 1)

        _variable = dvh.data[0]
        self.assertEqual(_variable.data_type, data_type)
        self.assertEqual(_variable.value, value)
        self.assertEqual(_variable.data_label, data_label)
        self.assertEqual(_variable.data_index, data_index)

    def test_extend(self):
        """Testing function extend."""
        # Setup AgentPolledData
        agent_id = 'koala_bear'
        agent_program = 'panda_bear'
        agent_hostname = 'localhost'
        timestamp = 68
        polling_interval = 30
        apd = AgentPolledData(
            agent_id, agent_program, agent_hostname,
            timestamp=timestamp, polling_interval=polling_interval)

        # Initialize DataVariablesHost
        device = 'teddy_bear'
        variableshost = DataVariablesHost(device)
        self.assertEqual(variableshost.device, device)
        self.assertFalse(variableshost.active)
        self.assertEqual(variableshost.data, [])

        # Setup DataVariable
        value = 457
        data_label = 'gummy_bear'
        data_index = 999
        data_type = DATA_INT
        variable = DataVariable(
            value=value, data_label=data_label, data_index=data_index,
            data_type=data_type)

        # Add data to DataVariablesHost
        self.assertFalse(variableshost.active)
        variableshost.append(variable)
        self.assertTrue(variableshost.active)

        # Test append
        self.assertFalse(apd.active)
        apd.extend(None)
        self.assertFalse(apd.active)
        apd.extend(variable)
        self.assertFalse(apd.active)
        apd.extend(variableshost)
        self.assertFalse(apd.active)
        apd.extend([variableshost])
        self.assertTrue(apd.active)

        # Test contents
        data = apd.data
        self.assertTrue(isinstance(data, list))
        self.assertEqual(len(data), 1)

        dvh = data[0]
        self.assertTrue(isinstance(dvh, DataVariablesHost))
        self.assertEqual(dvh.device, device)
        self.assertTrue(dvh.active)
        self.assertTrue(isinstance(dvh.data, list))
        self.assertTrue(len(dvh.data), 1)

        _variable = dvh.data[0]
        self.assertEqual(_variable.data_type, data_type)
        self.assertEqual(_variable.value, value)
        self.assertEqual(_variable.data_label, data_label)
        self.assertEqual(_variable.data_index, data_index)


class TestAgentAPIVariable(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test___init__(self):
        """Testing function __init__."""
        # Setup AgentAPIVariable
        ip_bind_port = 1234
        listen_address = '1.2.3.4'

        # Test defaults
        aav = AgentAPIVariable()
        self.assertEqual(aav.ip_bind_port, 6000)
        self.assertEqual(aav.listen_address, '0.0.0.0')

        # Test non-defaults
        aav = AgentAPIVariable(
            ip_bind_port=ip_bind_port, listen_address=listen_address)
        self.assertEqual(aav.ip_bind_port, ip_bind_port)
        self.assertEqual(aav.listen_address, listen_address)

    def test___repr__(self):
        """Testing function __repr__."""
        # Test defaults
        aav = AgentAPIVariable()
        expected = ('''\
<AgentAPIVariable ip_bind_port=6000, listen_address='0.0.0.0'>''')
        result = aav.__repr__()
        self.assertEqual(expected, result)


class TestBasicFunctions(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test__strip_non_printable(self):
        """Testing function _strip_non_printable."""
        pass


if __name__ == '__main__':
    # Make sure the environment is OK to run unittests
    UnittestConfig().create()

    # Do the unit test
    unittest.main()
