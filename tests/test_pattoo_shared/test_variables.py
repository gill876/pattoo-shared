#!/usr/bin/env python3
"""Test the files module."""

# Standard imports
import unittest
import os
import sys
import socket
import time

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
from pattoo_shared import variables
from pattoo_shared import files
from pattoo_shared.configuration import Config
from pattoo_shared.constants import (
    DATA_INT, DATA_STRING, DATA_FLOAT, DATAPOINT_KEYS, AGENT_METADATA_KEYS)
from pattoo_shared.variables import (
    DataPoint, DataPointMetadata, ConverterMetadata, PostingDataPoints,
    TargetDataPoints, TargetPollingPoints,
    PollingPoint, IPTargetPollingPoints, AgentPolledData, AgentAPIVariable)
from tests.libraries.configuration import UnittestConfig


class TestPostingDataPoints(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test___init__(self):
        """Testing function __init__."""
        # Setup PostingDataPoints - Valid
        agent_id = '1234'
        polling_interval = 10
        _datapoints = {
            'datapoint_pairs': [[0], [1]],
            'key_value_pairs': {
                '0': ['key_01', 'value_01'],
                '1': ['key_02', 'value_02']}
            }
        result = PostingDataPoints(agent_id, polling_interval, _datapoints)
        self.assertEqual(result.pattoo_agent_id, agent_id)
        self.assertEqual(result.pattoo_datapoints, _datapoints)
        self.assertEqual(
            result.pattoo_agent_polling_interval, polling_interval)
        self.assertTrue(result.valid)

        # Setup PostingDataPoints - Invalid
        for agent_id in [1, True, None, False, {1: 2}, [1, 2]]:
            polling_interval = 10
            result = PostingDataPoints(agent_id, polling_interval, _datapoints)
            self.assertEqual(result.pattoo_agent_id, agent_id)
            self.assertEqual(result.pattoo_datapoints, _datapoints)
            self.assertEqual(
                result.pattoo_agent_polling_interval, polling_interval)
            self.assertFalse(result.valid)

        for polling_interval in ['1', True, None, False, {1: 2}, [1, 2]]:
            agent_id = '1234'
            result = PostingDataPoints(agent_id, polling_interval, _datapoints)
            self.assertEqual(result.pattoo_agent_id, agent_id)
            self.assertEqual(result.pattoo_datapoints, _datapoints)
            self.assertEqual(
                result.pattoo_agent_polling_interval, polling_interval)
            self.assertFalse(result.valid)

        for datapoints in [1, True, None, False, {1: 2}, [1, 2]]:
            agent_id = '1234'
            polling_interval = 10
            result = PostingDataPoints(agent_id, polling_interval, datapoints)
            self.assertEqual(result.pattoo_agent_id, agent_id)
            self.assertEqual(result.pattoo_datapoints, datapoints)
            self.assertEqual(
                result.pattoo_agent_polling_interval, polling_interval)
            self.assertFalse(result.valid)


class TestDataPointMetadata(unittest.TestCase):
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
            result = DataPointMetadata(key, value)
            self.assertEqual(result.key, str(key))
            self.assertEqual(result.value, str(value))
            self.assertTrue(result.valid)

        # Setup DataPoint - Invalid
        for key, value in [
                ('pattoo', 1), ('123pattoo123', 1),
                (None, 2), ('1', None), (True, '2'), ('1', True),
                ({}, 2.1), ('1.1', {2: 1}), (False, '2.1'), ('1.1', False)]:
            result = DataPointMetadata(key, value)
            self.assertFalse(result.valid)

    def test___repr__(self):
        """Testing function __repr__."""
        # Setup DataPointMetadata
        variable = DataPointMetadata(5, 6)

        # Test
        expected = ('''<DataPointMetadata key='5', value='6'>''')
        result = variable.__repr__()
        self.assertEqual(result, expected)


class TestConverterMetadata(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test___init__(self):
        """Testing function __init__."""
        # Setup DataPoint - Valid
        value = 1
        for key in AGENT_METADATA_KEYS:
            result = ConverterMetadata(key, value)
            self.assertEqual(result.key, str(key))
            self.assertEqual(result.value, str(value))
            self.assertTrue(result.valid)

        # Setup DataPoint - Invalid
        for key, value in [
                ('pattoo', 1), ('123pattoo123', 1),
                (None, 2), ('1', None), (True, '2'), ('1', True),
                ({}, 2.1), ('1.1', {2: 1}), (False, '2.1'), ('1.1', False)]:
            result = ConverterMetadata(key, value)
            self.assertFalse(result.valid)

    def test___repr__(self):
        """Testing function __repr__."""
        # Setup ConverterMetadata
        key = AGENT_METADATA_KEYS[0]
        variable = ConverterMetadata(key, 6)

        # Test
        expected = ('''<ConverterMetadata key='{}', value='6'>'''.format(key))
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
        _key_ = 'testing'
        _metakey = '_{}'.format(_key_)
        timestamp = int(time.time() * 1000)
        data_type = DATA_INT
        variable = DataPoint(_key_, value, data_type=data_type)
        variable.add(DataPointMetadata(_metakey, _metakey))

        # Test each variable
        self.assertEqual(variable.data_type, data_type)
        self.assertEqual(variable.value, value)
        self.assertEqual(variable.key, _key_)
        self.assertTrue(variable.timestamp >= timestamp)
        self.assertEqual(len(variable.checksum), 64)
        self.assertEqual(variable.checksum, '''\
306353a04200e3b889b18c6f78dd8e56a63a287218ec8424e22d31b4b961a905''')
        self.assertEqual(variable.valid, True)

        # Setup DataPoint - Valid
        value = 1093454
        timestamp = 7
        _key_ = 'testing'
        _metakey = '_{}'.format(_key_)
        data_type = DATA_INT
        variable = DataPoint(
            _key_, value, data_type=data_type, timestamp=timestamp)
        variable.add(DataPointMetadata(_metakey, _metakey))

        # Test each variable
        self.assertEqual(variable.data_type, data_type)
        self.assertEqual(variable.value, value)
        self.assertEqual(variable.key, _key_)
        self.assertEqual(variable.timestamp, timestamp)
        self.assertEqual(len(variable.checksum), 64)
        self.assertEqual(variable.checksum, '''\
306353a04200e3b889b18c6f78dd8e56a63a287218ec8424e22d31b4b961a905''')
        self.assertEqual(variable.valid, True)

        # Add metadata that should be ignored.
        for key in DATAPOINT_KEYS:
            variable.add(DataPointMetadata(key, '_{}_'.format(key)))
        variable.add(DataPointMetadata(_metakey, _metakey))

        # Test each variable (unchanged)
        self.assertEqual(variable.data_type, data_type)
        self.assertEqual(variable.value, value)
        self.assertEqual(variable.key, _key_)
        self.assertEqual(len(variable.checksum), 64)
        self.assertEqual(variable.checksum, '''\
306353a04200e3b889b18c6f78dd8e56a63a287218ec8424e22d31b4b961a905''')
        self.assertEqual(variable.valid, True)

        # Setup DataPoint - invalid data_type
        value = 1093454
        _key_ = 'testing'
        data_type = 123
        variable = DataPoint(_key_, value, data_type=data_type)

        # Test each variable
        self.assertEqual(variable.data_type, data_type)
        self.assertEqual(variable.value, value)
        self.assertEqual(variable.key, _key_)
        self.assertEqual(variable.valid, False)

        # Setup DataPoint - invalid value for numeric data_type
        value = '_123'
        _key_ = 'testing'
        data_type = DATA_INT
        variable = DataPoint(_key_, value, data_type=data_type)

        # Test each variable
        self.assertEqual(variable.data_type, data_type)
        self.assertEqual(variable.value, value)
        self.assertEqual(variable.key, _key_)
        self.assertEqual(variable.valid, False)

        # Setup DataPoint - valid value for integer data_type but
        # string for value
        value = '1093454'
        _key_ = 'testing'
        data_type = DATA_INT
        variable = DataPoint(_key_, value, data_type=data_type)

        # Test each variable
        self.assertEqual(variable.data_type, data_type)
        self.assertEqual(variable.value, int(value))
        self.assertEqual(variable.key, _key_)
        self.assertEqual(len(variable.checksum), 64)
        self.assertEqual(variable.checksum, '''\
7f99301d9be275b14af5626ffabe22a154415ed2ef7dad37f1707bd25b6afdc6''')
        self.assertEqual(variable.valid, True)

        # Setup DataPoint - valid value for int data_type but
        # string for value
        value = '1093454.3'
        _key_ = 'testing'
        data_type = DATA_INT
        variable = DataPoint(_key_, value, data_type=data_type)

        # Test each variable
        self.assertEqual(variable.data_type, data_type)
        self.assertEqual(variable.value, int(float(value)))
        self.assertEqual(variable.key, _key_)
        self.assertEqual(len(variable.checksum), 64)
        self.assertEqual(variable.checksum, '''\
7f99301d9be275b14af5626ffabe22a154415ed2ef7dad37f1707bd25b6afdc6''')
        self.assertEqual(variable.valid, True)

        # Setup DataPoint - valid value for int data_type but
        # string for value
        value = '1093454.3'
        _key_ = 'testing'
        data_type = DATA_FLOAT
        variable = DataPoint(_key_, value, data_type=data_type)

        # Test each variable
        self.assertEqual(variable.data_type, data_type)
        self.assertEqual(variable.value, float(value))
        self.assertEqual(variable.key, _key_)
        self.assertEqual(len(variable.checksum), 64)
        self.assertEqual(variable.checksum, '''\
ab48bdc902e2ea5476a54680a7ace0971ab90edb3f6ffe00a89b2d1e17b1548d''')
        self.assertEqual(variable.valid, True)

        # Setup DataPoint - valid value for str data_type
        for value in [0, 1, '1093454.3']:
            _key_ = 'testing'
            data_type = DATA_STRING
            variable = DataPoint(_key_, value, data_type=data_type)

            # Test each variable
            self.assertEqual(variable.data_type, data_type)
            self.assertEqual(variable.value, str(value))
            self.assertEqual(variable.key, _key_)
            self.assertEqual(len(variable.checksum), 64)
            self.assertEqual(variable.checksum, '''\
431111472993bf4d9b8b347476b79321fea8a337f3c1cb2fedaa185b54185540''')
            self.assertEqual(variable.valid, True)

        # Setup DataPoint - invalid value for str data_type
        for value in [True, False, None]:
            _key_ = 'testing'
            data_type = DATA_STRING
            variable = DataPoint(_key_, value, data_type=data_type)

            # Test each variable
            self.assertEqual(variable.data_type, data_type)
            self.assertEqual(variable.valid, False)
            self.assertEqual(variable.value, str(value))
            self.assertIsNone(variable.key)
            self.assertEqual(len(variable.checksum), 64)
            self.assertEqual(variable.checksum, '''\
a783370f88d8c54b5f5e6641af69d86dae5d4d62621d55cf7e63f6c66644c214''')

    def test___repr__(self):
        """Testing function __repr__."""
        # Need to see all the string output
        self.maxDiff = None

        # Setup DataPoint
        value = 10
        _key_ = 'testing'
        data_type = DATA_INT
        variable = DataPoint(_key_, value, data_type=data_type)

        # Test
        expected = ('''\
<DataPoint key='testing', value=10, data_type=99, \
timestamp={}, valid=True>'''.format(variable.timestamp))
        result = variable.__repr__()
        self.assertEqual(result, expected)

    def test_add(self):
        """Testing function add."""
        # Setup DataPoint - Valid
        value = 1093454
        _key_ = 'testing'
        data_type = DATA_INT
        variable = DataPoint(_key_, value, data_type=data_type)

        # Test adding
        for key, value in [(1, 2), (3, 4), (5, 6)]:
            metadata = DataPointMetadata(key, value)
            variable.add(metadata)
            self.assertEqual(variable.metadata[str(key)], str(value))

        self.assertEqual(len(variable.metadata), 3)
        self.assertEqual(len(variable.checksum), 64)
        self.assertEqual(variable.checksum, '''\
73ce7225ca1ea55f53c96991c9922a185cf695224b94f2051b8a853049ba1935''')

        # Test adding duplicates (no change)
        for key, value in [(1, 2), (3, 4), (5, 6)]:
            metadata = DataPointMetadata(key, value)
            variable.add(metadata)
            self.assertEqual(variable.metadata[str(key)], str(value))

        self.assertEqual(len(variable.metadata), 3)
        self.assertEqual(len(variable.checksum), 64)
        self.assertEqual(variable.checksum, '''\
73ce7225ca1ea55f53c96991c9922a185cf695224b94f2051b8a853049ba1935''')

        # Test adding with now update_checksum set to False. No change
        for key, value in [(10, 20), (30, 40), (50, 60)]:
            metadata = DataPointMetadata(key, value, update_checksum=False)
            variable.add(metadata)
            self.assertEqual(variable.metadata[str(key)], str(value))

        self.assertEqual(len(variable.metadata), 6)
        self.assertEqual(len(variable.checksum), 64)
        self.assertEqual(variable.checksum, '''\
73ce7225ca1ea55f53c96991c9922a185cf695224b94f2051b8a853049ba1935''')

        # Test adding with now update_checksum set to True. No change,
        # as they have been added already.
        for key, value in [(10, 20), (30, 40), (50, 60)]:
            metadata = DataPointMetadata(key, value, update_checksum=True)
            variable.add(metadata)
            self.assertEqual(variable.metadata[str(key)], str(value))

        self.assertEqual(len(variable.metadata), 6)
        self.assertEqual(len(variable.checksum), 64)
        self.assertEqual(variable.checksum, '''\
73ce7225ca1ea55f53c96991c9922a185cf695224b94f2051b8a853049ba1935''')

        # Test adding with now update_checksum set to True
        for key, value in [(11, 21), (31, 41), (51, 61)]:
            metadata = DataPointMetadata(key, value, update_checksum=True)
            variable.add(metadata)
            self.assertEqual(variable.metadata[str(key)], str(value))

        self.assertEqual(len(variable.metadata), 9)
        self.assertEqual(len(variable.checksum), 64)
        self.assertEqual(variable.checksum, '''\
2518ce8c9dc0683ef87a6a438c8c79c2ae3fd8ffd38032b6c1d253057d04c8f7''')


class TestTargetDataPoints(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test___init__(self):
        """Testing function __init__."""
        # Setup TargetDataPoints
        target = 'localhost'
        ddv = TargetDataPoints(target)

        # Test initial vlues
        self.assertEqual(ddv.target, target)
        self.assertFalse(ddv.valid)
        self.assertEqual(ddv.data, [])

    def test___repr__(self):
        """Testing function __repr__."""
        # Setup TargetDataPoints
        target = 'localhost'
        ddv = TargetDataPoints(target)

        # Test
        expected = ('''\
<TargetDataPoints target='localhost', valid=False, data=[]''')
        result = ddv.__repr__()
        self.assertEqual(result, expected)

    def test_add(self):
        """Testing function append."""
        # Initialize TargetDataPoints
        target = 'teddy_bear'
        ddv = TargetDataPoints(target)
        self.assertEqual(ddv.target, target)
        self.assertFalse(ddv.valid)
        self.assertEqual(ddv.data, [])

        # Setup DataPoint
        value = 457
        _key_ = 'gummy_bear'
        data_type = DATA_INT
        variable = DataPoint(_key_, value, data_type=data_type)

        # Test adding invalid value
        ddv.add(None)
        self.assertEqual(ddv.data, [])

        # Test adding variable
        ddv.add(variable)
        self.assertTrue(bool(ddv.data))
        self.assertTrue(isinstance(ddv.data, list))
        self.assertEqual(len(ddv.data), 1)
        checksum = ddv.data[0].checksum

        # Test adding duplicate variable (There should be no changes)
        ddv.add(variable)
        self.assertTrue(bool(ddv.data))
        self.assertTrue(isinstance(ddv.data, list))
        self.assertEqual(len(ddv.data), 1)
        self.assertEqual(checksum, ddv.data[0].checksum)

        # Test the values in the variable
        _variable = ddv.data[0]
        self.assertEqual(_variable.data_type, data_type)
        self.assertEqual(_variable.value, value)
        self.assertEqual(_variable.key, _key_)


class TestAgentPolledData(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    config = Config()

    def test___init__(self):
        """Testing function __init__."""
        # Setup AgentPolledData variable
        agent_program = 'brown_bear'
        agent_hostname = socket.getfqdn()
        polling_interval = 20
        apd = AgentPolledData(agent_program, polling_interval)
        agent_id = files.get_agent_id(agent_program, self.config)

        # Test
        self.assertTrue(bool(apd.agent_timestamp))
        self.assertEqual(
            apd.agent_polling_interval, polling_interval * 1000)
        self.assertEqual(apd.agent_id, agent_id)
        self.assertEqual(apd.agent_program, agent_program)
        self.assertEqual(apd.agent_hostname, agent_hostname)
        self.assertFalse(apd.valid)

    def test___repr__(self):
        """Testing function __repr__."""
        # Setup AgentPolledData
        agent_program = 'brown_bear'
        polling_interval = 20
        apd = AgentPolledData(agent_program, polling_interval)

        # Test
        expected = ('''\
<AgentPolledData agent_id='{}' agent_program='brown_bear', \
agent_hostname='{}', timestamp={} polling_interval={}, valid=False>\
'''.format(apd.agent_id, apd.agent_hostname, apd.agent_timestamp,
           polling_interval * 1000))
        result = apd.__repr__()
        self.assertEqual(result, expected)

    def test_add(self):
        """Testing function append."""
        # Setup AgentPolledData
        agent_program = 'panda_bear'
        polling_interval = 20
        apd = AgentPolledData(agent_program, polling_interval)

        # Initialize TargetDataPoints
        target = 'teddy_bear'
        ddv = TargetDataPoints(target)
        self.assertEqual(ddv.target, target)
        self.assertFalse(ddv.valid)
        self.assertEqual(ddv.data, [])

        # Setup DataPoint
        value = 457
        _key_ = 'gummy_bear'
        data_type = DATA_INT
        variable = DataPoint(_key_, value, data_type=data_type)

        # Add data to TargetDataPoints
        self.assertFalse(ddv.valid)
        ddv.add(variable)
        self.assertTrue(ddv.valid)

        # Test add
        self.assertFalse(apd.valid)
        apd.add(None)
        self.assertFalse(apd.valid)
        apd.add(variable)
        self.assertFalse(apd.valid)
        apd.add(ddv)
        self.assertTrue(apd.valid)

        # Test contents
        data = apd.data
        self.assertTrue(isinstance(data, list))
        self.assertEqual(len(data), 1)

        _ddv = data[0]
        self.assertTrue(isinstance(_ddv, TargetDataPoints))
        self.assertEqual(_ddv.target, target)
        self.assertTrue(_ddv.valid)
        self.assertTrue(isinstance(_ddv.data, list))
        self.assertTrue(len(_ddv.data), 1)

        data = _ddv.data
        _variable = _ddv.data[0]
        self.assertEqual(_variable.data_type, data_type)
        self.assertEqual(_variable.value, value)
        self.assertEqual(_variable.key, _key_)


class TestAgentAPIVariable(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test___init__(self):
        """Testing function __init__."""
        # Setup AgentAPIVariable
        ip_bind_port = 1234
        ip_listen_address = '1.2.3.4'

        # Test defaults
        aav = AgentAPIVariable()
        self.assertEqual(aav.ip_bind_port, 20201)
        self.assertEqual(aav.ip_listen_address, '0.0.0.0')

        # Test non-defaults
        aav = AgentAPIVariable(
            ip_bind_port=ip_bind_port, ip_listen_address=ip_listen_address)
        self.assertEqual(aav.ip_bind_port, ip_bind_port)
        self.assertEqual(aav.ip_listen_address, ip_listen_address)

    def test___repr__(self):
        """Testing function __repr__."""
        # Test defaults
        aav = AgentAPIVariable()
        expected = ('''\
<AgentAPIVariable ip_bind_port=20201, ip_listen_address='0.0.0.0'>''')
        result = aav.__repr__()
        self.assertEqual(expected, result)


class TestPollingPoint(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test___init__(self):
        """Testing function __init__."""
        # Setup PollingPoint
        address = 20
        multiplier = 6
        result = PollingPoint(address=address, multiplier=multiplier)
        self.assertEqual(result.address, address)
        self.assertEqual(result.multiplier, multiplier)

        # Test with bad multiplier
        address = 25
        multipliers = [None, False, True, 'foo']
        for multiplier in multipliers:
            result = PollingPoint(address=address, multiplier=multiplier)
            self.assertEqual(result.address, address)
            self.assertEqual(result.multiplier, 1)

    def test___repr__(self):
        """Testing function __repr__."""
        # Setup variable
        address = 20
        multiplier = 6
        item = PollingPoint(address=address, multiplier=multiplier)

        # Test
        expected = ('''\
<PollingPoint address={}, multiplier={}>'''.format(address, multiplier))
        result = item.__repr__()
        self.assertEqual(result, expected)


class TestIPTargetPollingPoints(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test___init__(self):
        """Testing function __init__."""
        # Test
        for address in [123, 'koala_bear', '1.2.3', None, True, False, {}, []]:
            result = IPTargetPollingPoints(address)
            self.assertFalse(result.valid)

        for address in ['127.0.0.1', '::1', 'localhost', 'www.google.com']:
            result = IPTargetPollingPoints(address)
            result.add(PollingPoint(1, 2))
            self.assertTrue(result.valid)


class TestTargetPollingPoints(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test___init__(self):
        """Testing function __init__."""
        # Setup TargetPollingPoints
        target = 'localhost'
        dpt = TargetPollingPoints(target)
        self.assertEqual(dpt.target, target)
        self.assertFalse(dpt.valid)

    def test___repr__(self):
        """Testing function __repr__."""
        # Setup variable
        target = 'localhost'
        item = TargetPollingPoints(target)
        result = item.__repr__()

        # Test
        expected = ('''\
<TargetPollingPoints target='localhost', valid=False, data=[]>''')
        result = item.__repr__()
        self.assertEqual(result, expected)

    def test_add(self):
        """Testing function append."""
        # Initialize TargetPollingPoints
        target = 'localhost'
        dpt = TargetPollingPoints(target)
        self.assertEqual(dpt.target, target)
        self.assertFalse(dpt.valid)

        # Add bad values
        values = [True, False, None, 'foo']
        for value in values:
            dpt.add(value)
            self.assertFalse(dpt.valid)

        # Add good values
        address = 20
        multiplier = 6
        value = PollingPoint(address=address, multiplier=multiplier)
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

    def test__key_value_valid(self):
        """Testing function _key_value_valid."""
        # Test with valid values
        for _key, _value in [
                (1, 2), (0, 4), (5, 0), ('1', 2), (3, '4'), (0, 0), ('0', 1),
                (1, '0'), ('0', '0')]:
            (key, value, valid) = variables._key_value_valid(_key, _value)
            self.assertEqual(key, str(_key))
            self.assertEqual(value, _value)
            self.assertTrue(valid)

        # Test with invalid values
        for _key, _value in [
                (None, 2), (False, 4), ({5: 1}, 6),
                ('test', True), ('test', False), ('test', None),
                (True, 'test'), (False, 'test'), (None, 'test'),
                ('1', True), ('1', False), ('1', None),
                (True, '1'), (False, '1'), (None, '1'),
                (1, True), (1, False), (1, None),
                (True, 1), (False, 1), (None, 1)]:
            (key, value, valid) = variables._key_value_valid(_key, _value)
            self.assertIsNone(key)
            self.assertIsNone(value)
            self.assertFalse(valid)

        # Test with valid values
        for _key, _value in [
                (1, 2), (0, 4), (5, 0), ('1', 2), (3, '4'), (0, 0), ('0', 1),
                (1, '0'), ('0', '0')]:
            (key, value, valid) = variables._key_value_valid(
                _key, _value, metadata=True)
            self.assertEqual(key, str(_key))
            self.assertEqual(value, str(_value))
            self.assertTrue(valid)

        # Test with invalid values
        for _key, _value in [
                (None, 2), (False, 4), ({5: 1}, 6),
                ('test', True), ('test', False), ('test', None),
                (True, 'test'), (False, 'test'), (None, 'test'),
                ('1', True), ('1', False), ('1', None),
                (True, '1'), (False, '1'), (None, '1'),
                (1, True), (1, False), (1, None),
                (True, 1), (False, 1), (None, 1)]:
            (key, value, valid) = variables._key_value_valid(
                _key, _value, metadata=True)
            self.assertIsNone(key)
            self.assertIsNone(value)
            self.assertFalse(valid)


if __name__ == '__main__':
    # Make sure the environment is OK to run unittests
    UnittestConfig().create()

    # Do the unit test
    unittest.main()
