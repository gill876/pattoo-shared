#!/usr/bin/env python3
"""Test the converter module."""

# Standard imports
import unittest
import os
import sys
import time
from pprint import pprint

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
from pattoo_shared.configuration import Config
from pattoo_shared.variables import (
    DataPointMetadata, DataPoint, DeviceDataPoints, AgentPolledData)
from pattoo_shared.constants import (
    DATA_FLOAT, DATA_INT, DATA_COUNT64, DATA_COUNT, DATA_STRING, DATA_NONE,
    DATAPOINT_KEYS)
from tests.libraries.configuration import UnittestConfig


class TestBasicFunctions(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    config = Config()

    def test_cache_to_keypairs(self):
        """Testing method / function cache_to_keypairs."""
        self.maxDiff = None

        cache = {
            'pattoo_source': '1234',
            'pattoo_polling_interval': 30,
            'pattoo_datapoints': [
                {'pattoo_metadata': [
                    {'pattoo_agent_hostname': 'palisadoes'},
                    {'pattoo_agent_id': '1234'},
                    {'pattoo_agent_program': 'program_1'},
                    {'pattoo_device': 'device_1'},
                    {'gateway': 'palisadoes'}],
                 'pattoo_key': 30386,
                 'pattoo_data_type': 99,
                 'pattoo_value': 523.0,
                 'pattoo_timestamp': 1574011824387,
                 'pattoo_checksum': '123'}
            ]
        }

        # Test
        # cache = json.loads(cache_data)
        results = converter.cache_to_keypairs(cache)
        self.assertTrue(isinstance(results, list))
        for _, result in enumerate(results):
            self.assertEqual(result.pattoo_checksum, '''\
5c531afb2e4106cc78f99ff895ef99d2fa587f7272a91f82244f06caddf89176c299afc0ef4a44\
7d6c5042dff4690e271a3d09aabf97465faba20591f818ab27''')
            self.assertEqual(result.pattoo_timestamp, 1574011824387)
            self.assertEqual(result.pattoo_value, 523.0)
            self.assertEqual(result.pattoo_polling_interval, 30000)
            self.assertEqual(result.pattoo_data_type, 99)
            self.assertEqual(result.pattoo_key, 30386)
            _metadata = cache['pattoo_datapoints'][0]['pattoo_metadata']
            self.assertEqual(
                result.pattoo_metadata,
                [(_k_, _v_) for _dict in _metadata for _k_, _v_ in sorted(
                    _dict.items())])

    def test_agentdata_to_datapoints(self):
        """Testing method / function agentdata_to_datapoints."""
        # Setup AgentPolledData
        agent_program = 'panda_bear'
        apd = AgentPolledData(agent_program, self.config)

        # Initialize DeviceDataPoints
        device = 'teddy_bear'
        ddv = DeviceDataPoints(device)

        # Setup DataPoint
        value = 457
        key = 'gummy_bear'
        data_type = DATA_INT
        variable = DataPoint(key, value, data_type=data_type)

        # Add data to DeviceDataPoints
        ddv.add(variable)

        # Test DeviceGateway to AgentPolledData
        apd.add(ddv)

        # Test contents
        expected_metadata = {
            'pattoo_agent_id': apd.agent_id,
            'pattoo_agent_program': agent_program,
            'pattoo_agent_hostname': apd.agent_hostname,
            'pattoo_agent_polled_device': device
        }
        result = converter.agentdata_to_datapoints(apd)

        self.assertEqual(len(result), 1)
        item = result[0]
        self.assertTrue(isinstance(item, DataPoint))
        self.assertEqual(item.value, value)
        self.assertEqual(item.data_type, DATA_INT)
        self.assertEqual(item.key, key)
        self.assertTrue(isinstance(item.metadata, dict))
        self.assertEqual(len(item.metadata), len(expected_metadata))
        for key, value in item.metadata.items():
            self.assertTrue(isinstance(value, str))
            self.assertTrue(isinstance(key, str))
            self.assertEqual(value, str(expected_metadata[key]))

    def test_datapoints_to_dicts(self):
        """Testing method / function datapoints_to_dicts."""
        # Initialize key variables
        datapoints = []
        now = time.time()

        # Create DataPoints
        for value in range(0, 5):
            metadata = []
            for meta in range(0, 22, 7):
                metadata.append(DataPointMetadata(int(meta), str(meta * 2)))

            # Create the datapoint
            datapoint = DataPoint(
                'label_{}'.format(value), value,
                data_type=('type_{}'.format(value))
            )
            # Add metadata
            for meta in metadata:
                datapoint.add(meta)

            # Add metadata that should be ignored.
            for key in DATAPOINT_KEYS:
                metadata.append(DataPointMetadata(key, '_{}_'.format(key)))

            # Add the datapoint to the list
            datapoints.append(datapoint)

        # Start testing
        result = converter.datapoints_to_dicts(datapoints)
        self.assertTrue(isinstance(result, list))
        for value, item in enumerate(result):
            self.assertEqual(item['pattoo_data_type'], 'type_{}'.format(value))
            self.assertEqual(item['pattoo_key'], 'label_{}'.format(value))
            self.assertTrue(item['pattoo_timestamp'] >= now)
            self.assertTrue(item['pattoo_timestamp'] <= now + 1000)
            self.assertTrue(isinstance(item['pattoo_checksum'], str))
            self.assertTrue(isinstance(item['pattoo_metadata'], list))
            self.assertTrue(len(item['pattoo_metadata'], 4))
            for meta, metadata in enumerate(item['pattoo_metadata']):
                self.assertTrue(metadata, dict)
                for m_key, m_value in metadata.items():
                    self.assertEqual(2 * int(m_key), int(m_value))
                    self.assertEqual(int(m_key) % 7, 0)

    def test_agentdata_to_post(self):
        """Testing method / function agentdata_to_post."""
        # Setup AgentPolledData
        agent_program = 'panda_bear'
        polling_interval = self.config.polling_interval()
        apd = AgentPolledData(agent_program, self.config)

        # Initialize DeviceDataPoints
        device = 'teddy_bear'
        ddv = DeviceDataPoints(device)

        # Setup DataPoint
        value = 457
        key = 'gummy_bear'
        data_type = DATA_INT
        variable = DataPoint(key, value, data_type=data_type)

        # Add data to DeviceDataPoints
        ddv.add(variable)

        # Test DeviceGateway to AgentPolledData
        apd.add(ddv)
        result = converter.agentdata_to_post(apd)
        self.assertEqual(result.pattoo_source, apd.agent_id)
        self.assertEqual(result.pattoo_polling_interval, polling_interval)
        self.assertTrue(isinstance(result.pattoo_datapoints, list))

        # We have a dict to evaluate
        datapoint = result.pattoo_datapoints[0]
        self.assertTrue(isinstance(datapoint, dict))
        self.assertTrue(
            datapoint['pattoo_checksum'],
            'a488c71cafa214ee81f670eb0f935dc809374daee0664fe815f28ea628c3c8b3')
        self.assertTrue(datapoint['pattoo_data_type'], DATA_INT)
        self.assertTrue(datapoint['pattoo_key'], key)
        self.assertTrue(datapoint['pattoo_value'], value)

        expected_metadata = {
            'pattoo_agent_id': apd.agent_id,
            'pattoo_agent_program': apd.agent_program,
            'pattoo_agent_hostname': apd.agent_hostname,
            'pattoo_agent_polled_device': device
        }
        for item in datapoint['pattoo_metadata']:
            for key, value in item.items():
                self.assertTrue(isinstance(value, str))
                self.assertTrue(isinstance(key, str))
                self.assertEqual(value, str(expected_metadata[key]))

    def test_datapoints_to_post(self):
        """Testing method / function datapoints_to_post."""
        # Initialize key variables
        key = '_key'
        value = '_value'
        datapoints = [DataPoint(key, value)]
        source = '1234'
        polling_interval = self.config.polling_interval()
        result = converter.datapoints_to_post(
            source, polling_interval, datapoints)

        # Test
        self.assertEqual(result.pattoo_polling_interval, polling_interval)
        self.assertEqual(result.pattoo_source, source)
        self.assertEqual(result.pattoo_datapoints, datapoints)
        self.assertEqual(result.pattoo_datapoints[0].key, key)
        self.assertEqual(result.pattoo_datapoints[0].value, value)

    def test_posting_data_points(self):
        """Testing method / function posting_data_points."""
        # Initialize key variables
        key = '_key'
        value = '_value'
        datapoints = [DataPoint(key, value)]
        source = '1234'
        polling_interval = self.config.polling_interval()
        pdp = converter.datapoints_to_post(
            source, polling_interval, datapoints)
        result = converter.posting_data_points(pdp)

        # Test
        self.assertEqual(result['pattoo_polling_interval'], polling_interval)
        self.assertEqual(result['pattoo_source'], source)
        self.assertEqual(result['pattoo_datapoints'], datapoints)
        self.assertEqual(result['pattoo_datapoints'][0].key, key)
        self.assertEqual(result['pattoo_datapoints'][0].value, value)


if __name__ == '__main__':
    # Make sure the environment is OK to run unittests
    UnittestConfig().create()

    # Do the unit test
    unittest.main()
