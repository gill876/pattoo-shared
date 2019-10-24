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
    DataVariable, DataVariablesHost, AgentPolledData)
from pattoo_shared.configuration import Config
from tests.libraries.configuration import UnittestConfig


class TestConvertAgentPolledData(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test___init__(self):
        """Testing method / function __init__."""
        pass

    def test__process(self):
        """Testing method / function _process."""
        pass

    def test_data(self):
        """Testing method / function data."""
        pass


class TestBasicFunctions(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    apd = {
        'agent_hostname': 'palisadoes',
        'agent_id': '9088a13f',
        'agent_program': 'pattoo-agent-snmpd',
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
        'polling_interval': 10,
        'timestamp': 1571951520}

    def test_convert(self):
        """Testing method / function convert."""
        # Test expected OK
        data = deepcopy(self.apd)
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
        data = deepcopy(self.apd)
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
        self.assertTrue('device_1' in polled_data)
        self.assertTrue('device_2' in polled_data)

        # No agent_id
        data = deepcopy(self.apd)
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
        self.assertTrue('device_1' in polled_data)
        self.assertTrue('device_2' in polled_data)

        # No agent_program
        data = deepcopy(self.apd)
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
        self.assertTrue('device_1' in polled_data)
        self.assertTrue('device_2' in polled_data)

        # No agent_hostname
        data = deepcopy(self.apd)
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
        self.assertTrue('device_1' in polled_data)
        self.assertTrue('device_2' in polled_data)

        # No timestamp
        data = deepcopy(self.apd)
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
        self.assertTrue('device_1' in polled_data)
        self.assertTrue('device_2' in polled_data)

        # No polling_interval
        data = deepcopy(self.apd)
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
        self.assertTrue('device_1' in polled_data)
        self.assertTrue('device_2' in polled_data)

        # No devices
        data = deepcopy(self.apd)
        del data['devices']
        (agent_id, agent_program, agent_hostname, timestamp, polling_interval,
         polled_data, agent_valid) = converter._valid_agent(data)
        self.assertFalse(agent_valid)
        self.assertEqual(agent_id, data['agent_id'])
        self.assertEqual(agent_program, data['agent_program'])
        self.assertEqual(timestamp, data['timestamp'])
        self.assertEqual(polling_interval, data['polling_interval'])
        self.assertEqual(agent_hostname, data['agent_hostname'])
        self.assertIsNone(polled_data)

    def test__datavariableshost(self):
        """Testing method / function _datavariableshost."""
        # Initialize key variables
        device = 'device_1'

        # Test expected OK
        data = deepcopy(self.apd)['devices']
        dv_host = converter._datavariableshost(device, data[device])
        self.assertTrue(isinstance(dv_host, DataVariablesHost))
        self.assertEqual(dv_host.device, device)
        self.assertTrue(dv_host.active)
        self.assertTrue(bool(dv_host.data))
        self.assertTrue(isinstance(dv_host.data, list))

        for _dv in dv_host.data:
            self.assertTrue(isinstance(_dv, DataVariable))

    def test__datavariables(self):
        """Testing method / function _datavariables."""
        pass


if __name__ == '__main__':
    # Make sure the environment is OK to run unittests
    UnittestConfig().create()

    # Do the unit test
    unittest.main()
