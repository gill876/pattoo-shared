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
    DataVariable, DeviceDataVariables, DeviceGateway,
    AgentPolledData, AgentAPIVariable)
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


class TestDeviceDataVariables(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test___init__(self):
        """Testing function __init__."""
        # Setup DeviceDataVariables
        device = 'localhost'
        ddv = DeviceDataVariables(device)

        # Test initial vlues
        self.assertEqual(ddv.device, device)
        self.assertFalse(ddv.active)
        self.assertEqual(ddv.data, [])

    def test_add(self):
        """Testing function append."""
        # Initialize DeviceDataVariables
        device = 'teddy_bear'
        ddv = DeviceDataVariables(device)
        self.assertEqual(ddv.device, device)
        self.assertFalse(ddv.active)
        self.assertEqual(ddv.data, [])

        # Setup DataVariable
        value = 457
        data_label = 'gummy_bear'
        data_index = 999
        data_type = DATA_INT
        variable = DataVariable(
            value=value, data_label=data_label, data_index=data_index,
            data_type=data_type)

        # Test add
        ddv.add(None)
        self.assertEqual(ddv.data, [])

        ddv.add(variable)
        self.assertTrue(bool(ddv.data))
        self.assertTrue(isinstance(ddv.data, list))
        self.assertEqual(len(ddv.data), 1)

        # Test the values in the variable
        _variable = ddv.data[0]
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

    def test_add(self):
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

        # Initialize DeviceGateway
        gateway = 'grizzly_bear'
        dgw = DeviceGateway(gateway)
        self.assertEqual(dgw.device, gateway)
        self.assertFalse(dgw.active)
        self.assertEqual(dgw.data, [])

        # Initialize DeviceDataVariables
        device = 'teddy_bear'
        ddv = DeviceDataVariables(device)
        self.assertEqual(ddv.device, device)
        self.assertFalse(ddv.active)
        self.assertEqual(ddv.data, [])

        # Setup DataVariable
        value = 457
        data_label = 'gummy_bear'
        data_index = 999
        data_type = DATA_INT
        variable = DataVariable(
            value=value, data_label=data_label, data_index=data_index,
            data_type=data_type)

        # Add data to DeviceDataVariables
        self.assertFalse(ddv.active)
        ddv.add(variable)
        self.assertTrue(ddv.active)

        # Add data to DeviceGateway
        self.assertFalse(dgw.active)
        dgw.add(ddv)
        self.assertTrue(dgw.active)

        # Test add
        self.assertFalse(apd.active)
        apd.add(None)
        self.assertFalse(apd.active)
        apd.add(variable)
        self.assertFalse(apd.active)
        apd.add(dgw)
        self.assertTrue(apd.active)

        # Test contents
        data = apd.data
        self.assertTrue(isinstance(data, list))
        self.assertEqual(len(data), 1)

        _dgw = data[0]
        self.assertTrue(isinstance(_dgw, DeviceGateway))
        self.assertEqual(_dgw.device, gateway)
        self.assertTrue(_dgw.active)
        self.assertTrue(isinstance(_dgw.data, list))
        self.assertTrue(len(_dgw.data), 1)

        data = _dgw.data
        _ddv = data[0]
        self.assertTrue(isinstance(_ddv, DeviceDataVariables))
        self.assertEqual(_ddv.device, device)
        self.assertTrue(_ddv.active)
        self.assertTrue(isinstance(_ddv.data, list))
        self.assertTrue(len(_ddv.data), 1)

        data = _ddv.data
        _variable = _ddv.data[0]
        self.assertEqual(_variable.data_type, data_type)
        self.assertEqual(_variable.value, value)
        self.assertEqual(_variable.data_label, data_label)
        self.assertEqual(_variable.data_index, data_index)


class TestDeviceGateway(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test___init__(self):
        """Testing function __init__."""
        # Setup DeviceGateway variable
        gateway = 'polar_bear'
        dgw = DeviceGateway(gateway)

        # Test
        self.assertEqual(dgw.device, gateway)
        self.assertFalse(dgw.active)
        self.assertEqual(dgw.data, [])

    def test___repr__(self):
        """Testing function __repr__."""
        # Setup DeviceGateway variable
        gateway = 'polar_bear'
        dgw = DeviceGateway(gateway)

        # Test
        expected = ('''\
<DeviceGateway device='polar_bear' active=False, data=[]>''')
        result = dgw.__repr__()
        self.assertEqual(result, expected)

    def test_add(self):
        """Testing function append."""
        # Initialize DeviceGateway
        gateway = 'grizzly_bear'
        dgw = DeviceGateway(gateway)
        self.assertEqual(dgw.device, gateway)
        self.assertFalse(dgw.active)
        self.assertEqual(dgw.data, [])

        # Initialize DeviceDataVariables
        device = 'teddy_bear'
        ddv = DeviceDataVariables(device)
        self.assertEqual(ddv.device, device)
        self.assertFalse(ddv.active)
        self.assertEqual(ddv.data, [])

        # Setup DataVariable
        value = 457
        data_label = 'gummy_bear'
        data_index = 999
        data_type = DATA_INT
        variable = DataVariable(
            value=value, data_label=data_label, data_index=data_index,
            data_type=data_type)

        # Add data to DeviceDataVariables
        self.assertFalse(ddv.active)
        ddv.add(variable)
        self.assertTrue(ddv.active)

        # Test add
        self.assertFalse(dgw.active)
        dgw.add(None)
        self.assertFalse(dgw.active)
        dgw.add(variable)
        self.assertFalse(dgw.active)
        dgw.add(ddv)
        self.assertTrue(dgw.active)

        # Test contents
        data = dgw.data
        _ddv = data[0]
        self.assertTrue(isinstance(_ddv, DeviceDataVariables))
        self.assertEqual(_ddv.device, device)
        self.assertTrue(_ddv.active)
        self.assertTrue(isinstance(_ddv.data, list))
        self.assertTrue(len(_ddv.data), 1)

        data = _ddv.data
        _variable = _ddv.data[0]
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
