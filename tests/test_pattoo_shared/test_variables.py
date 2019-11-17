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
    DataPoint, DataPointMeta, DeviceDataPoints, DeviceGateway,
    PollingTarget, DevicePollingTargets,
    AgentPolledData, AgentAPIVariable)
from tests.libraries.configuration import UnittestConfig


class TestDataPointMeta(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test___init__(self):
        """Testing function __init__."""
        # Setup DataPoint - Valid
        for key, value in [
                (1, 2), ('1', 2), (1, '2'), ('1', '2'),
                (1.1, 2.1), ('1.1', 2.1), (1.1, '2.1'), ('1.1', '2.1')]:
            result = DataPointMeta(key, value)
            self.assertEqual(result.key, str(key))
            self.assertEqual(result.value, str(value))
            self.assertTrue(result.valid)

        # Setup DataPoint - Valid
        for key, value in [
                (None, 2), ('1', None), (True, '2'), ('1', True),
                ({}, 2.1), ('1.1', {2: 1}), (False, '2.1'), ('1.1', False)]:
            result = DataPointMeta(key, value)
            self.assertFalse(result.valid)

    def test___repr__(self):
        """Testing function __repr__."""
        # Setup DataPointMeta
        variable = DataPointMeta(5, 6)

        # Test
        expected = ('''<DataPointMeta key='5', value='6'>''')
        result = variable.__repr__()
        self.assertEqual(result, expected)


class TestDataPoint(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test___init__(self):
        """Testing function __init__."""
        # Setup DataPoint - Valid
        value = 1093454
        data_label = 'testing'
        data_index = 98766
        data_type = DATA_INT
        variable = DataPoint(
            value, data_label=data_label, data_index=data_index,
            data_type=data_type)

        # Test each variable
        self.assertEqual(variable.data_type, data_type)
        self.assertEqual(variable.data_value, value)
        self.assertEqual(variable.data_label, data_label)
        self.assertEqual(variable.data_index, data_index)
        self.assertEqual(len(variable.checksum), 64)
        self.assertEqual(variable.checksum, '''\
8a33d392cd65e5a24606ee5fd46abe8840196e0702354e8ad2033ba8259a44f4''')
        self.assertEqual(variable.valid, True)

        # Setup DataPoint - invalid data_type
        value = 1093454
        data_label = 'testing'
        data_index = 98766
        data_type = 123
        variable = DataPoint(
            value, data_label=data_label, data_index=data_index,
            data_type=data_type)

        # Test each variable
        self.assertEqual(variable.data_type, data_type)
        self.assertEqual(variable.data_value, value)
        self.assertEqual(variable.data_label, data_label)
        self.assertEqual(variable.data_index, data_index)
        self.assertEqual(variable.valid, False)

        # Setup DataPoint - invalid value for numeric data_type
        value = '_123'
        data_label = 'testing'
        data_index = 98766
        data_type = DATA_INT
        variable = DataPoint(
            value, data_label=data_label, data_index=data_index,
            data_type=data_type)

        # Test each variable
        self.assertEqual(variable.data_type, data_type)
        self.assertEqual(variable.data_value, value)
        self.assertEqual(variable.data_label, data_label)
        self.assertEqual(variable.data_index, data_index)
        self.assertEqual(variable.valid, False)

        # Setup DataPoint - valid value for integer data_type but
        # string for value
        value = '1093454'
        data_label = 'testing'
        data_index = 98766
        data_type = DATA_INT
        variable = DataPoint(
            value, data_label=data_label, data_index=data_index,
            data_type=data_type)

        # Test each variable
        self.assertEqual(variable.data_type, data_type)
        self.assertEqual(variable.data_value, int(value))
        self.assertEqual(variable.data_label, data_label)
        self.assertEqual(variable.data_index, data_index)
        self.assertEqual(len(variable.checksum), 64)
        self.assertEqual(variable.checksum, '''\
8a33d392cd65e5a24606ee5fd46abe8840196e0702354e8ad2033ba8259a44f4''')
        self.assertEqual(variable.valid, True)

        # Setup DataPoint - valid value for int data_type but
        # string for value
        value = '1093454.3'
        data_label = 'testing'
        data_index = 98766
        data_type = DATA_INT
        variable = DataPoint(
            value, data_label=data_label, data_index=data_index,
            data_type=data_type)

        # Test each variable
        self.assertEqual(variable.data_type, data_type)
        self.assertEqual(variable.data_value, int(float(value)))
        self.assertEqual(variable.data_label, data_label)
        self.assertEqual(variable.data_index, data_index)
        self.assertEqual(len(variable.checksum), 64)
        self.assertEqual(variable.checksum, '''\
8a33d392cd65e5a24606ee5fd46abe8840196e0702354e8ad2033ba8259a44f4''')
        self.assertEqual(variable.valid, True)

        # Setup DataPoint - valid value for int data_type but
        # string for value
        value = '1093454.3'
        data_label = 'testing'
        data_index = 98766
        data_type = DATA_FLOAT
        variable = DataPoint(
            value, data_label=data_label, data_index=data_index,
            data_type=data_type)

        # Test each variable
        self.assertEqual(variable.data_type, data_type)
        self.assertEqual(variable.data_value, float(value))
        self.assertEqual(variable.data_label, data_label)
        self.assertEqual(variable.data_index, data_index)
        self.assertEqual(len(variable.checksum), 64)
        self.assertEqual(variable.checksum, '''\
b555c7d50d836597959e58369357a20c8e89b6b14a4a147618afc9aad2a8dc82''')
        self.assertEqual(variable.valid, True)

        # Setup DataPoint - valid value for str data_type
        for value in [True, False, None, 0, 1, '1093454.3']:
            data_label = 'testing'
            data_index = 98766
            data_type = DATA_STRING
            variable = DataPoint(
                value, data_label=data_label, data_index=data_index,
                data_type=data_type)

            # Test each variable
            self.assertEqual(variable.data_type, data_type)
            self.assertEqual(variable.data_value, str(value))
            self.assertEqual(variable.data_label, data_label)
            self.assertEqual(variable.data_index, data_index)
            self.assertEqual(len(variable.checksum), 64)
            self.assertEqual(variable.checksum, '''\
7dbd9767177b3c07aab11a299a3619a7f0427adc64e779a15968b7818a618a14''')
            self.assertEqual(variable.valid, True)

    def test___repr__(self):
        """Testing function __repr__."""
        # Setup DataPoint
        value = 10
        data_label = 'testing'
        data_index = 10
        data_type = DATA_INT
        variable = DataPoint(
            value, data_label=data_label, data_index=data_index,
            data_type=data_type)

        # Test
        expected = ('''\
<DataPoint data_value=10, data_label='testing', data_index=10, data_type=99, \
data_timestamp={}, valid=True>'''.format(variable.data_timestamp))
        result = variable.__repr__()
        self.assertEqual(result, expected)

    def test_add(self):
        """Testing function add."""
        # Setup DataPoint - Valid
        value = 1093454
        data_label = 'testing'
        data_index = 98766
        data_type = DATA_INT
        variable = DataPoint(
            value, data_label=data_label, data_index=data_index,
            data_type=data_type)

        for key, value in [(1, 2), (3, 4), (5, 6)]:
            metadata = DataPointMeta(key, value)
            variable.add(metadata)
            self.assertEqual(variable.metadata[str(key)], str(value))

        self.assertEqual(len(variable.checksum), 64)
        self.assertEqual(variable.checksum, '''\
8a33d392cd65e5a24606ee5fd46abe8840196e0702354e8ad2033ba8259a44f4''')


class TestDeviceDataPoints(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test___init__(self):
        """Testing function __init__."""
        # Setup DeviceDataPoints
        device = 'localhost'
        ddv = DeviceDataPoints(device)

        # Test initial vlues
        self.assertEqual(ddv.device, device)
        self.assertFalse(ddv.valid)
        self.assertEqual(ddv.data, [])

    def test___repr__(self):
        """Testing function __repr__."""
        # Setup DeviceDataPoints
        device = 'localhost'
        ddv = DeviceDataPoints(device, device_type=456)

        # Test
        expected = ('''\
<DeviceDataPoints device='localhost', device_type=456, valid=False, \
data=[]''')
        result = ddv.__repr__()
        self.assertEqual(result, expected)

    def test_add(self):
        """Testing function append."""
        # Initialize DeviceDataPoints
        device = 'teddy_bear'
        ddv = DeviceDataPoints(device)
        self.assertEqual(ddv.device, device)
        self.assertFalse(ddv.valid)
        self.assertEqual(ddv.data, [])

        # Setup DataPoint
        value = 457
        data_label = 'gummy_bear'
        data_index = 999
        data_type = DATA_INT
        variable = DataPoint(
            value, data_label=data_label, data_index=data_index,
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
        self.assertEqual(_variable.data_value, value)
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
        polling_interval = 30
        apd = AgentPolledData(
            agent_id, agent_program, agent_hostname, polling_interval)

        # Test
        self.assertTrue(bool(apd.agent_timestamp))
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
        polling_interval = 30
        apd = AgentPolledData(
            agent_id, agent_program, agent_hostname, polling_interval)

        # Test
        expected = ('''\
<AgentPolledData agent_id='polar_bear' agent_program='brown_bear', \
agent_hostname='localhost', timestamp={} polling_interval=30, valid=False>\
'''.format(apd.agent_timestamp, 3))
        result = apd.__repr__()
        self.assertEqual(result, expected)

    def test_add(self):
        """Testing function append."""
        # Setup AgentPolledData
        agent_id = 'koala_bear'
        agent_program = 'panda_bear'
        agent_hostname = 'localhost'
        polling_interval = 30
        apd = AgentPolledData(
            agent_id, agent_program, agent_hostname, polling_interval)

        # Initialize DeviceGateway
        gateway = 'grizzly_bear'
        dgw = DeviceGateway(gateway)
        self.assertEqual(dgw.device, gateway)
        self.assertFalse(dgw.valid)
        self.assertEqual(dgw.data, [])

        # Initialize DeviceDataPoints
        device = 'teddy_bear'
        ddv = DeviceDataPoints(device)
        self.assertEqual(ddv.device, device)
        self.assertFalse(ddv.valid)
        self.assertEqual(ddv.data, [])

        # Setup DataPoint
        value = 457
        data_label = 'gummy_bear'
        data_index = 999
        data_type = DATA_INT
        variable = DataPoint(
            value, data_label=data_label, data_index=data_index,
            data_type=data_type)

        # Add data to DeviceDataPoints
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
        self.assertTrue(isinstance(_ddv, DeviceDataPoints))
        self.assertEqual(_ddv.device, device)
        self.assertTrue(_ddv.valid)
        self.assertTrue(isinstance(_ddv.data, list))
        self.assertTrue(len(_ddv.data), 1)

        data = _ddv.data
        _variable = _ddv.data[0]
        self.assertEqual(_variable.data_type, data_type)
        self.assertEqual(_variable.data_value, value)
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

        # Initialize DeviceDataPoints
        device = 'teddy_bear'
        ddv = DeviceDataPoints(device)
        self.assertEqual(ddv.device, device)
        self.assertFalse(ddv.valid)
        self.assertEqual(ddv.data, [])

        # Setup DataPoint
        value = 457
        data_label = 'gummy_bear'
        data_index = 999
        data_type = DATA_INT
        variable = DataPoint(
            value, data_label=data_label, data_index=data_index,
            data_type=data_type)

        # Add data to DeviceDataPoints
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
        self.assertTrue(isinstance(_ddv, DeviceDataPoints))
        self.assertEqual(_ddv.device, device)
        self.assertTrue(_ddv.valid)
        self.assertTrue(isinstance(_ddv.data, list))
        self.assertTrue(len(_ddv.data), 1)

        data = _ddv.data
        _variable = _ddv.data[0]
        self.assertEqual(_variable.data_type, data_type)
        self.assertEqual(_variable.data_value, value)
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

    def test___repr__(self):
        """Testing function __repr__."""
        # Setup variable
        device = 'localhost'
        item = DevicePollingTargets(device, device_type=678)
        result = item.__repr__()

        # Test
        expected = ('''\
<DevicePollingTargets device='localhost', device_type=678, valid=False, \
data=[]>''')
        result = item.__repr__()
        self.assertEqual(result, expected)

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
