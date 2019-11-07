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
from pattoo_shared.constants import DATA_INT, DATA_STRING, DATA_FLOAT
from pattoo_shared.variables import (
    DataVariable, DeviceDataVariables, DeviceGateway,
    PollingTarget, DevicePollingTargets,
    AgentPolledData, AgentAPIVariable)
from tests.libraries.configuration import UnittestConfig


class TestDataVariable(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test___init__(self):
        """Testing function __init__."""
        # Setup DataVariable - Valid
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
        self.assertEqual(variable.valid, True)

        # Setup DataVariable - invalid data_type
        value = 1093454
        data_label = 'testing'
        data_index = 98766
        data_type = 123
        variable = DataVariable(
            value=value, data_label=data_label, data_index=data_index,
            data_type=data_type)

        # Test each variable
        self.assertEqual(variable.data_type, data_type)
        self.assertEqual(variable.value, value)
        self.assertEqual(variable.data_label, data_label)
        self.assertEqual(variable.data_index, data_index)
        self.assertEqual(variable.valid, False)

        # Setup DataVariable - invalid value for numeric data_type
        value = '_123'
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
        self.assertEqual(variable.valid, False)

        # Setup DataVariable - valid value for integer data_type but
        # string for value
        value = '1093454'
        data_label = 'testing'
        data_index = 98766
        data_type = DATA_INT
        variable = DataVariable(
            value=value, data_label=data_label, data_index=data_index,
            data_type=data_type)

        # Test each variable
        self.assertEqual(variable.data_type, data_type)
        self.assertEqual(variable.value, int(value))
        self.assertEqual(variable.data_label, data_label)
        self.assertEqual(variable.data_index, data_index)
        self.assertEqual(variable.valid, True)

        # Setup DataVariable - valid value for int data_type but
        # string for value
        value = '1093454.3'
        data_label = 'testing'
        data_index = 98766
        data_type = DATA_INT
        variable = DataVariable(
            value=value, data_label=data_label, data_index=data_index,
            data_type=data_type)

        # Test each variable
        self.assertEqual(variable.data_type, data_type)
        self.assertEqual(variable.value, int(float(value)))
        self.assertEqual(variable.data_label, data_label)
        self.assertEqual(variable.data_index, data_index)
        self.assertEqual(variable.valid, True)

        # Setup DataVariable - valid value for int data_type but
        # string for value
        value = '1093454.3'
        data_label = 'testing'
        data_index = 98766
        data_type = DATA_FLOAT
        variable = DataVariable(
            value=value, data_label=data_label, data_index=data_index,
            data_type=data_type)

        # Test each variable
        self.assertEqual(variable.data_type, data_type)
        self.assertEqual(variable.value, float(value))
        self.assertEqual(variable.data_label, data_label)
        self.assertEqual(variable.data_index, data_index)
        self.assertEqual(variable.valid, True)

        # Setup DataVariable - valid value for str data_type
        for value in [True, False, None, 0, 1, '1093454.3']:
            data_label = 'testing'
            data_index = 98766
            data_type = DATA_STRING
            variable = DataVariable(
                value=value, data_label=data_label, data_index=data_index,
                data_type=data_type)

            # Test each variable
            self.assertEqual(variable.data_type, data_type)
            self.assertEqual(variable.value, str(value))
            self.assertEqual(variable.data_label, data_label)
            self.assertEqual(variable.data_index, data_index)
            self.assertEqual(variable.valid, True)

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
<DataVariable value=10, data_label='testing', data_index=10, data_type=0, \
valid=True>''')
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
        self.assertFalse(ddv.valid)
        self.assertEqual(ddv.data, [])

    def test_add(self):
        """Testing function append."""
        # Initialize DeviceDataVariables
        device = 'teddy_bear'
        ddv = DeviceDataVariables(device)
        self.assertEqual(ddv.device, device)
        self.assertFalse(ddv.valid)
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

        # Test addding variable
        ddv.add(variable)
        self.assertTrue(bool(ddv.data))
        self.assertTrue(isinstance(ddv.data, list))
        self.assertEqual(len(ddv.data), 1)
        checksum = ddv.data[0].checksum

        # Test addding duplicate variable
        ddv.add(variable)
        self.assertTrue(bool(ddv.data))
        self.assertTrue(isinstance(ddv.data, list))
        self.assertEqual(len(ddv.data), 1)
        self.assertEqual(checksum, ddv.data[0].checksum)

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
            agent_id, agent_program, agent_hostname, polling_interval,
            timestamp=timestamp)

        # Test
        self.assertEqual(apd.timestamp, 60)
        self.assertEqual(apd.polling_interval, 30)
        self.assertEqual(apd.agent_id, agent_id)
        self.assertEqual(apd.agent_program, agent_program)
        self.assertEqual(apd.agent_hostname, agent_hostname)
        self.assertFalse(apd.valid)

    def test___repr__(self):
        """Testing function __repr__."""
        # Setup AgentPolledData
        agent_id = 'polar_bear'
        agent_program = 'brown_bear'
        agent_hostname = 'localhost'
        timestamp = 68
        polling_interval = 30
        apd = AgentPolledData(
            agent_id, agent_program, agent_hostname, polling_interval,
            timestamp=timestamp)

        # Test
        expected = ('''\
<AgentPolledData agent_id='polar_bear' agent_program='brown_bear', \
agent_hostname='localhost', timestamp=60 polling_interval=30, valid=False>''')
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
            agent_id, agent_program, agent_hostname, polling_interval,
            timestamp=timestamp)

        # Initialize DeviceGateway
        gateway = 'grizzly_bear'
        dgw = DeviceGateway(gateway)
        self.assertEqual(dgw.device, gateway)
        self.assertFalse(dgw.valid)
        self.assertEqual(dgw.data, [])

        # Initialize DeviceDataVariables
        device = 'teddy_bear'
        ddv = DeviceDataVariables(device)
        self.assertEqual(ddv.device, device)
        self.assertFalse(ddv.valid)
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
        self.assertFalse(ddv.valid)
        ddv.add(variable)
        self.assertTrue(ddv.valid)

        # Add data to DeviceGateway
        self.assertFalse(dgw.valid)
        dgw.add(ddv)
        self.assertTrue(dgw.valid)

        # Test add
        self.assertFalse(apd.valid)
        apd.add(None)
        self.assertFalse(apd.valid)
        apd.add(variable)
        self.assertFalse(apd.valid)
        apd.add(dgw)
        self.assertTrue(apd.valid)

        # Test contents
        data = apd.data
        self.assertTrue(isinstance(data, list))
        self.assertEqual(len(data), 1)

        _dgw = data[0]
        self.assertTrue(isinstance(_dgw, DeviceGateway))
        self.assertEqual(_dgw.device, gateway)
        self.assertTrue(_dgw.valid)
        self.assertTrue(isinstance(_dgw.data, list))
        self.assertTrue(len(_dgw.data), 1)

        data = _dgw.data
        _ddv = data[0]
        self.assertTrue(isinstance(_ddv, DeviceDataVariables))
        self.assertEqual(_ddv.device, device)
        self.assertTrue(_ddv.valid)
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
        self.assertFalse(dgw.valid)
        self.assertEqual(dgw.data, [])

    def test___repr__(self):
        """Testing function __repr__."""
        # Setup DeviceGateway variable
        gateway = 'polar_bear'
        dgw = DeviceGateway(gateway)

        # Test
        expected = ('''\
<DeviceGateway device='polar_bear', valid=False, data=[]>''')
        result = dgw.__repr__()
        self.assertEqual(result, expected)

    def test_add(self):
        """Testing function append."""
        # Initialize DeviceGateway
        gateway = 'grizzly_bear'
        dgw = DeviceGateway(gateway)
        self.assertEqual(dgw.device, gateway)
        self.assertFalse(dgw.valid)
        self.assertEqual(dgw.data, [])

        # Initialize DeviceDataVariables
        device = 'teddy_bear'
        ddv = DeviceDataVariables(device)
        self.assertEqual(ddv.device, device)
        self.assertFalse(ddv.valid)
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
        self.assertFalse(ddv.valid)
        ddv.add(variable)
        self.assertTrue(ddv.valid)

        # Test add
        self.assertFalse(dgw.valid)
        dgw.add(None)
        self.assertFalse(dgw.valid)
        dgw.add(variable)
        self.assertFalse(dgw.valid)
        dgw.add(ddv)
        self.assertTrue(dgw.valid)

        # Test contents
        data = dgw.data
        _ddv = data[0]
        self.assertTrue(isinstance(_ddv, DeviceDataVariables))
        self.assertEqual(_ddv.device, device)
        self.assertTrue(_ddv.valid)
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


class TestPollingTarget(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test___init__(self):
        """Testing function __init__."""
        # Setup PollingTarget
        address = 20
        multiplier = 6
        result = PollingTarget(address=address, multiplier=multiplier)
        self.assertEqual(result.address, address)
        self.assertEqual(result.multiplier, multiplier)

        # Test with bad multiplier
        address = 25
        multipliers = [None, False, True, 'foo']
        for multiplier in multipliers:
            result = PollingTarget(address=address, multiplier=multiplier)
            self.assertEqual(result.address, address)
            self.assertEqual(result.multiplier, 1)

    def test___repr__(self):
        """Testing function __repr__."""
        # Setup variable
        address = 20
        multiplier = 6
        item = PollingTarget(address=address, multiplier=multiplier)

        # Test
        expected = ('''\
<PollingTarget address={}, multiplier={}>'''.format(address, multiplier))
        result = item.__repr__()
        self.assertEqual(result, expected)


class TestDevicePollingTargets(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test___init__(self):
        """Testing function __init__."""
        # Setup DevicePollingTargets
        device = 'localhost'
        dpt = DevicePollingTargets(device)
        self.assertEqual(dpt.device, device)
        self.assertFalse(dpt.valid)

    def test_add(self):
        """Testing function append."""
        # Initialize DevicePollingTargets
        device = 'localhost'
        dpt = DevicePollingTargets(device)
        self.assertEqual(dpt.device, device)
        self.assertFalse(dpt.valid)

        # Add bad values
        values = [True, False, None, 'foo']
        for value in values:
            dpt.add(value)
            self.assertFalse(dpt.valid)

        # Add good values
        address = 20
        multiplier = 6
        value = PollingTarget(address=address, multiplier=multiplier)
        dpt.add(value)
        self.assertTrue(dpt.valid)
        self.assertEqual(len(dpt.data), 1)
        for item in dpt.data:
            self.assertEqual(item.address, address)
            self.assertEqual(item.multiplier, multiplier)

        # Try adding bad values and the results must be the same
        values = [True, False, None, 'foo']
        for value in values:
            dpt.add(value)
            self.assertTrue(dpt.valid)
            self.assertEqual(len(dpt.data), 1)
            item = dpt.data[0]
            self.assertEqual(item.address, address)
            self.assertEqual(item.multiplier, multiplier)


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
