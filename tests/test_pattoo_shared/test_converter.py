#!/usr/bin/env python3
"""Test the converter module."""

# Standard imports
import unittest
import os
import sys
from copy import deepcopy

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
from pattoo_shared import converter
from pattoo_shared.variables import (
    DataVariable, DeviceDataVariables, DeviceGateway, AgentPolledData)
from pattoo_shared.configuration import Config
from pattoo_shared.constants import (
    DATA_FLOAT, DATA_INT, DATA_COUNT64, DATA_COUNT, DATA_STRING, DATA_NONE)
from tests.libraries.configuration import UnittestConfig


# Known working data
APD = {
    'agent_hostname': 'palisadoes',
    'agent_id': '9088a13f',
    'agent_program': 'pattoo-agent-snmpd',
    'gateways': {
        'gw01': {
            'devices': {
                'device_1': {
                    '.1.3.6.1.2.1.2.2.1.10': {
                        'data': [['1', 1999], ['100', 2999]],
                        'data_type': 32},
                    '.1.3.6.1.2.1.2.2.1.16': {
                        'data': [['1', 3999], ['100', 4999]],
                        'data_type': 32}
                },
                'device_2': {
                    '.1.3.6.1.2.1.2.2.1.10': {
                        'data': [['1', 1888], ['100', 2888]],
                        'data_type': 32},
                    '.1.3.6.1.2.1.2.2.1.16': {
                        'data': [['2', 3888], ['102', 4888]],
                        'data_type': 32}
                },
            },
        },
    },
    'polling_interval': 10,
    'timestamp': 1571951520}


class TestConvertAgentPolledData(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test___init__(self):
        """Testing method / function __init__."""
        # Test expected OK
        data = deepcopy(APD)
        agentdata = converter.convert(data)
        self.assertTrue(isinstance(agentdata, AgentPolledData))
        self.assertEqual(agentdata.active, True)
        self.assertEqual(agentdata.agent_program, data['agent_program'])
        self.assertEqual(agentdata.agent_hostname, data['agent_hostname'])
        self.assertEqual(agentdata.timestamp, data['timestamp'])
        self.assertEqual(agentdata.polling_interval, data['polling_interval'])
        self.assertEqual(agentdata.agent_id, data['agent_id'])
        self.assertTrue(bool(agentdata.data))
        self.assertTrue(isinstance(agentdata.data, list))
        for dgw in agentdata.data:
            self.assertTrue(isinstance(dgw, DeviceGateway))
            self.assertTrue(bool(dgw.data))
            self.assertTrue(isinstance(dgw.data, list))
            for dvh in dgw.data:
                self.assertTrue(isinstance(dvh, DeviceDataVariables))
                self.assertTrue(bool(dvh.data))
                for _dv in dvh.data:
                    self.assertTrue(isinstance(_dv.value, int))
                    self.assertTrue(isinstance(_dv.data_index, str))
                    self.assertTrue(isinstance(_dv.data_label, str))
                    self.assertEqual(_dv.data_type, 32)
                    self.assertTrue(_dv.data_label.startswith(
                        '.1.3.6.1.2.1.2.2.1.1'))

    def test__process(self):
        """Testing method / function _process."""
        # Tested by test___init__
        pass

    def test_data(self):
        """Testing method / function data."""
        # Tested by test___init__
        pass


class TestBasicFunctions(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    # Bad data for testing. Empty list, dict, None, fake dict
    bad_data = [
        'test_string',
        1,
        1.1,
        [],
        {},
        None,
        {
            'key1': 1,
            'key2': 2,
            'key3': 3,
            'key4': 4
        },
        {
            'data': [],
            'data_type': 26
        }
    ]

    # Bad data for DeviceDataVariables testing
    # - Data not a list of lists
    # - Data has bad data_type
    # - Data is None
    # - Data is dict
    # - No Data
    # - No data_type
    # - Data is empty list of lists
    # - Data is empty list
    # - Data is empty list of lists of lists
    bad_dvh_01 = {
        'bad_dev_01': {
            'bad_key_01': {
                'data': [{'1': 1999}, {'100': 2999}],
                'data_type': 32}
        },
        'bad_dev_02': {
            'bad_key_01': {
                'data': [['1', 1999], ['100', 2999]],
                'data_type': 23}
        },
        'bad_dev_03': {
            'bad_key_01': {
                'data': None,
                'data_type': 32}
        },
        'bad_dev_04': {
            'bad_key_01': {
                'data': {},
                'data_type': 32}
        },
        'bad_dev_05': {
            'bad_key_01': {
                'data_type': 32}
        },
        'bad_dev_06': {
            'bad_key_01': {
                'data': {},
            }
        },
        'bad_dev_07': {
            'bad_key_01': {
                'data': [[]],
                'data_type': 32}
        },
        'bad_dev_08': {
            'bad_key_01': {
                'data': [],
                'data_type': 32}
        },
        'bad_dev_09': {
            'bad_key_01': {
                'data': [[[]]],
                'data_type': 32}
        },
    }

    # Almost good data for DeviceDataVariables testing
    # - Data has None in list
    # - Data has list with 3 values
    bad_dvh_02 = {
        'bad_dev_01': {
            'bad_key_01': {
                'data': [['1', 1999], None],
                'data_type': 32}
        },
        'bad_dev_02': {
            'bad_key_01': {
                'data': [['1', 1999], [1, 2, 3]],
                'data_type': 32}
        },
    }

    def test_convert(self):
        """Testing method / function convert."""
        # Test expected OK
        data = deepcopy(APD)
        result = converter.convert(data)
        self.assertTrue(isinstance(result, AgentPolledData))
        self.assertEqual(result.active, True)
        self.assertEqual(result.agent_program, data['agent_program'])
        self.assertEqual(result.agent_hostname, data['agent_hostname'])
        self.assertEqual(result.timestamp, data['timestamp'])
        self.assertEqual(result.polling_interval, data['polling_interval'])
        self.assertEqual(result.agent_id, data['agent_id'])

    def test__valid_agent(self):
        """Testing method / function _valid_agent."""
        # Test expected OK
        data = deepcopy(APD)
        (agent_id, agent_program, agent_hostname, timestamp, polling_interval,
         polled_data, agent_valid) = converter._valid_agent(data)
        self.assertEqual(agent_valid, True)
        self.assertEqual(agent_program, data['agent_program'])
        self.assertEqual(agent_hostname, data['agent_hostname'])
        self.assertEqual(timestamp, data['timestamp'])
        self.assertEqual(polling_interval, data['polling_interval'])
        self.assertEqual(agent_id, data['agent_id'])
        self.assertTrue(bool(polled_data))
        self.assertTrue(isinstance(polled_data, dict))
        self.assertTrue('gw01' in polled_data)

        # No agent_id
        data = deepcopy(APD)
        del data['agent_id']
        (agent_id, agent_program, agent_hostname, timestamp, polling_interval,
         polled_data, agent_valid) = converter._valid_agent(data)
        self.assertFalse(agent_valid)
        self.assertEqual(agent_program, data['agent_program'])
        self.assertEqual(agent_hostname, data['agent_hostname'])
        self.assertEqual(timestamp, data['timestamp'])
        self.assertEqual(polling_interval, data['polling_interval'])
        self.assertTrue(bool(polled_data))
        self.assertTrue(isinstance(polled_data, dict))
        self.assertIsNone(agent_id)
        self.assertTrue('gw01' in polled_data)

        # No agent_program
        data = deepcopy(APD)
        del data['agent_program']
        (agent_id, agent_program, agent_hostname, timestamp, polling_interval,
         polled_data, agent_valid) = converter._valid_agent(data)
        self.assertFalse(agent_valid)
        self.assertEqual(agent_id, data['agent_id'])
        self.assertEqual(agent_hostname, data['agent_hostname'])
        self.assertEqual(timestamp, data['timestamp'])
        self.assertEqual(polling_interval, data['polling_interval'])
        self.assertTrue(bool(polled_data))
        self.assertTrue(isinstance(polled_data, dict))
        self.assertIsNone(agent_program)
        self.assertTrue('gw01' in polled_data)

        # No agent_hostname
        data = deepcopy(APD)
        del data['agent_hostname']
        (agent_id, agent_program, agent_hostname, timestamp, polling_interval,
         polled_data, agent_valid) = converter._valid_agent(data)
        self.assertFalse(agent_valid)
        self.assertEqual(agent_id, data['agent_id'])
        self.assertEqual(agent_program, data['agent_program'])
        self.assertEqual(timestamp, data['timestamp'])
        self.assertEqual(polling_interval, data['polling_interval'])
        self.assertTrue(bool(polled_data))
        self.assertTrue(isinstance(polled_data, dict))
        self.assertIsNone(agent_hostname)
        self.assertTrue('gw01' in polled_data)

        # No timestamp
        data = deepcopy(APD)
        del data['timestamp']
        (agent_id, agent_program, agent_hostname, timestamp, polling_interval,
         polled_data, agent_valid) = converter._valid_agent(data)
        self.assertFalse(agent_valid)
        self.assertEqual(agent_id, data['agent_id'])
        self.assertEqual(agent_hostname, data['agent_hostname'])
        self.assertEqual(polling_interval, data['polling_interval'])
        self.assertEqual(agent_program, data['agent_program'])
        self.assertTrue(bool(polled_data))
        self.assertTrue(isinstance(polled_data, dict))
        self.assertIsNone(timestamp)
        self.assertTrue('gw01' in polled_data)

        # No polling_interval
        data = deepcopy(APD)
        del data['polling_interval']
        (agent_id, agent_program, agent_hostname, timestamp, polling_interval,
         polled_data, agent_valid) = converter._valid_agent(data)
        self.assertFalse(agent_valid)
        self.assertEqual(agent_id, data['agent_id'])
        self.assertEqual(agent_program, data['agent_program'])
        self.assertEqual(timestamp, data['timestamp'])
        self.assertTrue(bool(polled_data))
        self.assertTrue(isinstance(polled_data, dict))
        self.assertEqual(agent_hostname, data['agent_hostname'])
        self.assertIsNone(polling_interval)
        self.assertTrue('gw01' in polled_data)

        # No gateways
        data = deepcopy(APD)
        del data['gateways']
        (agent_id, agent_program, agent_hostname, timestamp, polling_interval,
         polled_data, agent_valid) = converter._valid_agent(data)
        self.assertFalse(agent_valid)
        self.assertEqual(agent_id, data['agent_id'])
        self.assertEqual(agent_program, data['agent_program'])
        self.assertEqual(timestamp, data['timestamp'])
        self.assertEqual(polling_interval, data['polling_interval'])
        self.assertEqual(agent_hostname, data['agent_hostname'])
        self.assertIsNone(polled_data)

        # Test with bad data
        for data in self.bad_data:
            (agent_id, agent_program, agent_hostname, timestamp,
             polling_interval, polled_data, agent_valid
             ) = converter._valid_agent(data)
            self.assertFalse(agent_valid)
            self.assertIsNone(agent_id)
            self.assertIsNone(agent_program)
            self.assertIsNone(timestamp)
            self.assertIsNone(polling_interval)
            self.assertIsNone(agent_hostname)
            self.assertIsNone(polled_data)

    def test__create_ddv(self):
        """Testing method / function _create_ddv."""
        # Initialize key variables
        device = 'device_1'

        # Test expected OK
        data = deepcopy(APD)['gateways']['gw01']['devices']
        dv_host = converter._create_ddv(device, data[device])
        self.assertTrue(isinstance(dv_host, DeviceDataVariables))
        self.assertEqual(dv_host.device, device)
        self.assertTrue(dv_host.active)
        self.assertTrue(bool(dv_host.data))
        self.assertTrue(isinstance(dv_host.data, list))
        for _dv in dv_host.data:
            self.assertTrue(isinstance(_dv, DataVariable))

        # Test with bad data
        for data in self.bad_data:
            dv_host = converter._create_ddv(data, data)
            self.assertTrue(isinstance(dv_host, DeviceDataVariables))
            self.assertEqual(dv_host.device, data)
            self.assertFalse(dv_host.active)
            self.assertFalse(bool(dv_host.data))
            self.assertTrue(isinstance(dv_host.data, list))
            for _dv in dv_host.data:
                self.assertFalse(isinstance(_dv, DataVariable))

        # Test with bad data
        for device, data in sorted(self.bad_dvh_01.items()):
            dv_host = converter._create_ddv(device, data)
            self.assertTrue(isinstance(dv_host, DeviceDataVariables))
            self.assertTrue(dv_host.device, device)
            self.assertFalse(dv_host.active)
            self.assertFalse(bool(dv_host.data))
            self.assertTrue(isinstance(dv_host.data, list))
            for _dv in dv_host.data:
                self.assertFalse(isinstance(_dv, DataVariable))

        # Test with partially corrupted data
        for device, data in sorted(self.bad_dvh_02.items()):
            dv_host = converter._create_ddv(device, data)
            self.assertTrue(isinstance(dv_host, DeviceDataVariables))
            self.assertTrue(dv_host.device, device)
            self.assertTrue(dv_host.active)
            self.assertTrue(bool(dv_host.data))
            self.assertTrue(isinstance(dv_host.data, list))
            self.assertTrue(len(dv_host.data), 1)
            for _dv in dv_host.data:
                self.assertTrue(isinstance(_dv, DataVariable))
                self.assertEqual(_dv.value, 1999)
                self.assertEqual(_dv.data_index, '1')
                self.assertEqual(_dv.data_type, 32)
                self.assertEqual(_dv.data_label, 'bad_key_01')

    def test__create_datavariables(self):
        """Testing method / function _create_datavariables."""
        # Initialize key variables
        valid_types = [
            DATA_FLOAT, DATA_INT, DATA_COUNT64, DATA_COUNT,
            DATA_STRING, DATA_NONE]
        invalid_types = [True, False, '', 1.2]
        data_label = '.1.3.6.1.2.1.2.2.1.16'
        label_dict = {
            'data': [['2', 3888], ['102', 4888]],
            'data_type': 32}

        # Test valid types
        for next_type in valid_types:
            label_dict['data_type'] = next_type
            result = converter._create_datavariables(data_label, label_dict)
            self.assertTrue(isinstance(result, list))
            self.assertTrue(bool(result))
            for _dv in result:
                self.assertTrue(isinstance(_dv, DataVariable))
                self.assertEqual(_dv.data_type, next_type)

        # Test invalid types
        for next_type in invalid_types:
            label_dict['data_type'] = next_type
            result = converter._create_datavariables(data_label, label_dict)
            self.assertTrue(isinstance(result, list))
            self.assertFalse(bool(result))
            for _dv in result:
                self.assertTrue(isinstance(_dv, DataVariable))
                self.assertEqual(_dv.data_type, next_type)

    def test_extract(self):
        """Testing method / function _create_datavariables."""
        # Test expected OK
        data = deepcopy(APD)
        agentdata = converter.convert(data)
        result = converter.extract(agentdata)
        self.assertTrue(isinstance(result, list))
        for row in result:
            print(row)
            self.assertEqual(len(row), 11)
            self.assertEqual(row.agent_id, '9088a13f')
            self.assertEqual(row.agent_program, 'pattoo-agent-snmpd')
            self.assertEqual(row.agent_hostname, 'palisadoes')
            self.assertEqual(row.timestamp, 1571951520)
            self.assertEqual(row.polling_interval, 10)
            self.assertEqual(row.gateway, 'gw01')
            self.assertTrue(isinstance(row.value, int))
            self.assertTrue(isinstance(row.data_type, int))
            self.assertTrue(isinstance(row.data_index, str))


if __name__ == '__main__':
    # Make sure the environment is OK to run unittests
    UnittestConfig().create()

    # Do the unit test
    unittest.main()
