#!/usr/bin/env python3
"""Test the converter module."""

# Standard imports
import unittest
import os
import sys
from time import sleep

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
from pattoo_shared import converter
from pattoo_shared.configuration import Config
from pattoo_shared.variables import (
    DataPointMetadata, DataPoint, TargetDataPoints, AgentPolledData)
from pattoo_shared.constants import (
    DATA_FLOAT, DATA_INT, DATA_COUNT64, DATA_COUNT, DATA_STRING, DATA_NONE,
    DATAPOINT_KEYS, PattooDBrecord)
from tests.libraries.configuration import UnittestConfig


class TestBasicFunctions(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    config = Config()

    def test_cache_to_keypairs(self):
        """Testing method or function named cache_to_keypairs."""
        cache = {
            'pattoo_agent_id': '123bb3a17c6cc915a98a859226d282b394ee0964956b7'
                               'd23c145fe9d94567241',
            'pattoo_agent_polling_interval': 10000,
            'pattoo_agent_timestamp': 1575789070210,
            'pattoo_datapoints': {
                'datapoint_pairs': [
                    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                    [11, 1, 2, 3, 4, 5, 6, 7, 12, 13, 14]],
                'key_value_pairs': {
                    '0': ['agent_snmpd_oid', '.1.3.6.1.2.1.2.2.1.10.1'],
                    '1': ['pattoo_agent_hostname', 'swim'],
                    '2': ['pattoo_agent_id',
                          '123bb3a17c6cc915a98a859226d282b'
                          '394ee0964956b7d23c145fe9d94567241'],
                    '3': ['pattoo_agent_polled_target', 'localhost'],
                    '4': ['pattoo_agent_polling_interval', '10000'],
                    '5': ['pattoo_agent_program', 'pattoo_agent_snmpd'],
                    '6': ['pattoo_key', 'agent_snmpd_.1.3.6.1.2.1.2.2.1.10'],
                    '7': ['pattoo_data_type', 32],
                    '8': ['pattoo_value', 4057039287.0],
                    '9': ['pattoo_timestamp', 1575789070107],
                    '10': ['pattoo_checksum',
                           'f6ac40a45ec4fa7d19823d8c318bb0c6d0a19f79ad4b04ab5'
                           '290d65f42250296'],
                    '11': ['agent_snmpd_oid', '.1.3.6.1.2.1.2.2.1.10.2'],
                    '12': ['pattoo_value', 0.0],
                    '13': ['pattoo_timestamp', 1575789070108],
                    '14': ['pattoo_checksum',
                           '2849bef00a05419c4614610814a1a8088a89a81a8192dbfa2'
                           '77598e1ff3389da']
                }
            }
        }

        # Test
        pattoo_db_records = converter.cache_to_keypairs(cache)

        # pattoo_db_records[0]
        # should have the values in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        result = pattoo_db_records[0]
        expected = PattooDBrecord(
            pattoo_checksum='5306d34dac4c0c90b5cdc09c37a62c0d3056c6f58044b7a9'
                            'e2c93c65d0de9d88e4173b5972e73b59cecdad4a80e28fc7'
                            'a0edd32db653156b05cf80efb818f5c8',
            pattoo_metadata=[
                ('agent_snmpd_oid', '.1.3.6.1.2.1.2.2.1.10.1')],
            pattoo_data_type=32,
            pattoo_key='agent_snmpd_.1.3.6.1.2.1.2.2.1.10',
            pattoo_value=4057039287.0,
            pattoo_timestamp=1575789070107,
            pattoo_agent_polled_target='localhost',
            pattoo_agent_program='pattoo_agent_snmpd',
            pattoo_agent_hostname='swim',
            pattoo_agent_id='123bb3a17c6cc915a98a859226d282b394ee0964956b7d2'
                            '3c145fe9d94567241',
            pattoo_agent_polling_interval='10000')
        self.assertEqual(result, expected)

        # pattoo_db_records[1]
        # should have the values in [11, 1, 2, 3, 4, 5, 6, 7, 12, 13, 14]
        result = pattoo_db_records[1]
        expected = PattooDBrecord(
            pattoo_checksum='5decef67c60b4528f142373f2d796b28241c9af51d78abe5'
                            '29c92830e7491134de1dd600fb9c517f72a57a0f68640684'
                            '4a3ca1138c69a494cbedcb36e5e866b9',
            pattoo_metadata=[
                ('agent_snmpd_oid', '.1.3.6.1.2.1.2.2.1.10.2')],
            pattoo_data_type=32,
            pattoo_key='agent_snmpd_.1.3.6.1.2.1.2.2.1.10',
            pattoo_value=0.0,
            pattoo_timestamp=1575789070108,
            pattoo_agent_polled_target='localhost',
            pattoo_agent_program='pattoo_agent_snmpd',
            pattoo_agent_hostname='swim',
            pattoo_agent_id='123bb3a17c6cc915a98a859226d282b394ee0964956b7d23'
                            'c145fe9d94567241',
            pattoo_agent_polling_interval='10000')
        self.assertEqual(result, expected)

    def test__make_pattoo_db_record(self):
        """Testing method or function named _make_pattoo_db_record."""
        pass

    def test_agentdata_to_datapoints(self):
        """Testing method or function named agentdata_to_datapoints."""
        # Setup AgentPolledData
        agent_program = 'panda_bear'
        polling_interval = 20
        apd = AgentPolledData(agent_program, polling_interval)

        # Initialize TargetDataPoints
        target = 'teddy_bear'
        ddv = TargetDataPoints(target)

        # Setup DataPoint
        value = 457
        key = 'gummy_bear'
        data_type = DATA_INT
        variable = DataPoint(key, value, data_type=data_type)

        # Add data to TargetDataPoints
        ddv.add(variable)

        # Test TargetGateway to AgentPolledData
        apd.add(ddv)

        # Test contents
        expected_metadata = {
            'pattoo_agent_id': apd.agent_id,
            'pattoo_agent_program': agent_program,
            'pattoo_agent_hostname': apd.agent_hostname,
            'pattoo_agent_polled_target': target,
            'pattoo_agent_polling_interval': apd.agent_polling_interval
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
        """Testing method or function named datapoints_to_dicts."""
        # Initialize key variables
        datapoints = []

        # Create DataPoints
        for value in range(0, 2):
            # Sleep to force a change in the timestamp
            sleep(0.1)

            metadata = []
            for meta in range(0, 2):
                metadata.append(DataPointMetadata(int(meta), str(meta * 2)))

            # Create the datapoint
            datapoint = DataPoint(
                'label_{}'.format(value), value, data_type=DATA_INT
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
        expected = {
            'key_value_pairs': {
                0: ('0', '0'),
                1: ('1', '2'),
                2: ('pattoo_key', 'label_0'),
                3: ('pattoo_data_type', 99),
                4: ('pattoo_value', 0),
                5: ('pattoo_timestamp', 1575794447250),
                6: ('pattoo_checksum',
                    '284d21bff49bbde9eb7fc3ad98a88e5cbf72830f69743b47bd2c349'
                    '407807f68'),
                7: ('pattoo_key', 'label_1'),
                8: ('pattoo_value', 1),
                9: ('pattoo_timestamp', 1575915772433),
                10: ('pattoo_checksum',
                     'a5919eb5fc5bac62e7c80bc04155931f75e22166ed84b1d07f704f4'
                     '0b083d098')},
            'datapoint_pairs': [[0, 1, 2, 3, 4, 5, 6], [0, 1, 7, 3, 8, 9, 10]]}

        self.assertEqual(
            result['datapoint_pairs'], expected['datapoint_pairs'])
        for key, value in result['key_value_pairs'].items():
            if key not in [5, 9]:
                self.assertEqual(expected['key_value_pairs'][key], value)

    def test_agentdata_to_post(self):
        """Testing method or function named agentdata_to_post."""
        # Setup AgentPolledData
        agent_program = 'panda_bear'
        polling_interval = 20
        apd = AgentPolledData(agent_program, polling_interval)

        # Initialize TargetDataPoints
        target = 'teddy_bear'
        ddv = TargetDataPoints(target)

        # Setup DataPoint
        value = 457
        key = 'gummy_bear'
        data_type = DATA_INT
        variable = DataPoint(key, value, data_type=data_type)

        # Add data to TargetDataPoints
        ddv.add(variable)

        # Test TargetGateway to AgentPolledData
        apd.add(ddv)
        result = converter.agentdata_to_post(apd)
        self.assertEqual(result.pattoo_agent_id, apd.agent_id)
        self.assertEqual(
            result.pattoo_agent_polling_interval, polling_interval * 1000)
        self.assertTrue(isinstance(result.pattoo_datapoints, dict))

        # Test the key value pairs
        item = result.pattoo_datapoints['key_value_pairs']
        self.assertTrue('datapoint_pairs' in result.pattoo_datapoints)
        self.assertTrue('key_value_pairs' in result.pattoo_datapoints)
        self.assertTrue(isinstance(item, dict))

        # Convert item to a list of tuples for ease of testing
        tester = [(k, v) for k, v in sorted(item.items())]
        self.assertEqual(
            tester[0],
            (0, ('pattoo_agent_polling_interval', '20000')))

        self.assertEqual(
            tester[3:8],
            [
                (3, ('pattoo_agent_polled_target', 'teddy_bear')),
                (4, ('pattoo_agent_program', 'panda_bear')),
                (5, ('pattoo_key', 'gummy_bear')),
                (6, ('pattoo_data_type', 99)),
                (7, ('pattoo_value', 457))]
        )

        # Test the pointers to the key value pairs
        item = result.pattoo_datapoints['datapoint_pairs']
        self.assertTrue(isinstance(item, list))
        self.assertEqual(len(item), 1)
        self.assertEqual(len(item[0]), 10)

    def test_datapoints_to_post(self):
        """Testing method or function named datapoints_to_post."""
        # Initialize key variables
        key = '_key'
        value = '_value'
        datapoints = [DataPoint(key, value)]
        source = '1234'
        polling_interval = 20
        result = converter.datapoints_to_post(
            source, polling_interval, datapoints)

        # Test
        self.assertEqual(
            result.pattoo_agent_polling_interval, polling_interval)
        self.assertEqual(result.pattoo_agent_id, source)
        self.assertEqual(result.pattoo_datapoints, datapoints)
        self.assertEqual(result.pattoo_datapoints[0].key, key)
        self.assertEqual(result.pattoo_datapoints[0].value, value)

    def test_posting_data_points(self):
        """Testing method or function named posting_data_points."""
        # Initialize key variables
        key = '_key'
        value = '_value'
        datapoints = [DataPoint(key, value)]
        source = '1234'
        polling_interval = 20
        pdp = converter.datapoints_to_post(
            source, polling_interval, datapoints)
        result = converter.posting_data_points(pdp)

        # Test
        self.assertEqual(
            result['pattoo_agent_polling_interval'], polling_interval)
        self.assertEqual(result['pattoo_agent_id'], source)
        self.assertEqual(result['pattoo_datapoints'], datapoints)
        self.assertEqual(result['pattoo_datapoints'][0].key, key)
        self.assertEqual(result['pattoo_datapoints'][0].value, value)

    def test__keypairs(self):
        """Testing method or function named _keypairs."""
        # Test
        data = {'test this out': 7}
        result = converter._keypairs(data)
        expected = []
        self.assertEqual(result, expected)

        data = {'test this out': '7'}
        result = converter._keypairs(data)
        expected = [('test_this_out', '7')]
        self.assertEqual(result, expected)

    def test__checksum(self):
        """Testing method or function named _checksum."""
        # Test
        result = converter._checksum(1, 2, 3)
        expected = ('''\
3c9909afec25354d551dae21590bb26e38d53f2173b8d3dc3eee4c047e7ab1c1eb8b85103e3be7\
ba613b31bb5c9c36214dc9f14a42fd7a2fdb84856bca5c44c2''')
        self.assertEqual(result, expected)


if __name__ == '__main__':
    # Make sure the environment is OK to run unittests
    UnittestConfig().create()

    # Do the unit test
    unittest.main()
