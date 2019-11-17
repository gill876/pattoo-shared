#!/usr/bin/env python3
"""Test the converter module."""

# Standard imports
import unittest
import os
import sys
import time

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
from pattoo_shared import data as lib_data
from pattoo_shared.variables import (
    DataPointMeta, DataPoint, DeviceDataPoints, DeviceGateway, AgentPolledData)
from pattoo_shared.configuration import Config
from pattoo_shared.constants import (
    DATA_FLOAT, DATA_INT, DATA_COUNT64, DATA_COUNT, DATA_STRING, DATA_NONE,
    PattooDBrecord)
from tests.libraries.configuration import UnittestConfig


class TestBasicFunctions(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test_cache_to_keypairs(self):
        """Testing method / function cache_to_keypairs."""
        cache = [
            "1234",
            [{"metadata": [
                {"agent_hostname": "palisadoes"},
                {"agent_id": "1234"},
                {"agent_program": "program_1"},
                {"device": "device_1"},
                {"gateway": "palisadoes"},
                {"polling_interval": "10"}],
              "data_label": 30386,
              "data_type": 99,
              "data_index": "index_1",
              "data_value": 523.0,
              "data_timestamp": 1574011824387,
              "checksum": '''\
b6c093d976251b97d00324bb65b6f3319c4df1f1c90c94c564014165bf6672b4'''},
             {"metadata": [
                 {"agent_hostname": "palisadoes"},
                 {"agent_id": "1234"},
                 {"agent_program": "program_1"},
                 {"device": "device_1"},
                 {"gateway": "palisadoes"},
                 {"polling_interval": "10"}],
              "data_label": 30386 * 2,
              "data_type": 99,
              "data_index": "index_1",
              "data_value": 523.0 * 2,
              "data_timestamp": 1574011824390,
              "checksum": '''\
7ed9053508b247fe1f1749594fda40cf8e2292c786e438b935ff11193ae07640'''}]]

        # Test
        results = converter.cache_to_keypairs(cache[0], cache[1])
        self.assertTrue(isinstance(results, list))
        for index, result in enumerate(results):
            pass

    def test_agentdata_to_datapoints(self):
        """Testing method / function agentdata_to_datapoints."""
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

        # Initialize DeviceDataPoints
        device = 'teddy_bear'
        ddv = DeviceDataPoints(device)

        # Setup DataPoint
        value = 457
        data_label = 'gummy_bear'
        data_index = 999
        data_type = DATA_INT
        variable = DataPoint(
            value, data_label=data_label, data_index=data_index,
            data_type=data_type)

        # Add data to DeviceDataPoints
        ddv.add(variable)

        # Add data to DeviceGateway
        dgw.add(ddv)

        # Test DeviceGateway to AgentPolledData
        apd.add(dgw)

        # Test contents
        expected_metadata = {
            'agent_id': agent_id,
            'agent_program': agent_program,
            'agent_hostname': agent_hostname,
            'polling_interval': polling_interval,
            'gateway': gateway,
            'device': device
        }
        result = converter.agentdata_to_datapoints(apd)

        self.assertEqual(len(result), 1)
        item = result[0]
        self.assertTrue(isinstance(item, DataPoint))
        self.assertEqual(item.data_value, value)
        self.assertEqual(item.data_type, DATA_INT)
        self.assertEqual(item.data_index, data_index)
        self.assertEqual(item.data_label, data_label)
        self.assertEqual(
            item.checksum,
            '''\
adaa977bbc2f3b0cae66f4c3021963a34ef16077e3ad54d2ae3736b3842c85b0''')
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
                metadata.append(DataPointMeta(int(meta), str(meta * 2)))
            datapoint = DataPoint(
                value,
                data_index=(value * 10),
                data_type=('type_{}'.format(value)),
                data_label=('label_{}'.format(value)),
            )
            for meta in metadata:
                datapoint.add(meta)
            datapoints.append(datapoint)

        # Start testing
        result = converter.datapoints_to_dicts(datapoints)
        self.assertTrue(isinstance(result, list))
        for value, item in enumerate(result):
            self.assertEqual(item['data_index'], value * 10)
            self.assertEqual(item['data_type'], 'type_{}'.format(value))
            self.assertEqual(item['data_label'], 'label_{}'.format(value))
            self.assertTrue(item['data_timestamp'] >= now)
            self.assertTrue(item['data_timestamp'] <= now + 1000)
            self.assertTrue(isinstance(item['checksum'], str))
            self.assertTrue(isinstance(item['metadata'], list))
            self.assertTrue(len(item['metadata'], 4))
            for meta, metadata in enumerate(item['metadata']):
                self.assertTrue(metadata, dict)
                for m_key, m_value in metadata.items():
                    self.assertEqual(2 * int(m_key), int(m_value))
                    self.assertEqual(int(m_key) % 7, 0)


if __name__ == '__main__':
    # Make sure the environment is OK to run unittests
    UnittestConfig().create()

    # Do the unit test
    unittest.main()
