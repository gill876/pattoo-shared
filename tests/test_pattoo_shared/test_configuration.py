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
from pattoo_shared import configuration
from pattoo_shared import log
from pattoo_shared.variables import PollingPoint
from tests.libraries.configuration import UnittestConfig


class TestConfig(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    config = configuration.Config()

    def test___init__(self):
        """Testing function __init__."""
        pass

    def test_language(self):
        """Testing function language."""
        # Initialize key values
        expected = 'xyz'

        # Test
        result = self.config.language()
        self.assertEqual(result, expected)

    def test_agent_api_ip_address(self):
        """Testing function agent_api_ip_address."""
        # Initialize key values
        expected = '127.0.0.6'

        # Test
        result = self.config.agent_api_ip_address()
        self.assertEqual(result, expected)

    def test_agent_api_ip_bind_port(self):
        """Testing function agent_api_ip_bind_port."""
        # Initialize key values
        expected = 50505

        # Test
        result = self.config.agent_api_ip_bind_port()
        self.assertEqual(result, expected)

    def test_agent_api_uri(self):
        """Testing function api_uri."""
        # Initialize key values
        expected = '/pattoo/api/v1/agent/receive'

        # Test
        result = self.config.agent_api_uri()
        self.assertEqual(result, expected)

    def test_agent_api_key(self):
        """Test for key exchange."""
        # Test
        expected = '/pattoo/api/v1/agent/key'
        result = self.config.agent_api_key()

        self.assertEqual(result, expected)

    def test_agent_api_validation(self):
        """Test for key validation."""
        # Test
        expected = '/pattoo/api/v1/agent/validation'
        result = self.config.agent_api_validation()

        self.assertEqual(result, expected)

    def test_agent_api_encrypted(self):
        """Test for encrypted post route."""
        # Test
        expected = '/pattoo/api/v1/agent/encrypted'
        result = self.config.agent_api_encrypted()

        self.assertEqual(result, expected)

    def test_agent_api_server_url(self):
        """Testing function agent_api_server_url."""
        # Initialize key values
        expected = 'http://127.0.0.6:50505/pattoo/api/v1/agent/receive/123'
        agent_id = 123

        # Test
        result = self.config.agent_api_server_url(agent_id)
        self.assertEqual(result, expected)

    def test_agent_api_key_url(self):
        """Test key exchange URL."""
        # Test

        expected = 'http://127.0.0.6:50505/pattoo/api/v1/agent/key'
        result = self.config.agent_api_key_url()

        self.assertEqual(result, expected)

    def test_agent_api_validation_url(self):
        """Test validation URL"""
        # Test

        expected = 'http://127.0.0.6:50505/pattoo/api/v1/agent/validation'
        result = self.config.agent_api_validation_url()

        self.assertEqual(result, expected)

    def test_agent_api_encrypted_url(self):
        """Test for encrypted post URL"""
        # Test

        expected = 'http://127.0.0.6:50505/pattoo/api/v1/agent/encrypted'
        result = self.config.agent_api_encrypted_url()

        self.assertEqual(result, expected)

    def test_api_email_address(self):
        """Test api email address retrieval"""
        # Test from yaml file
        result = self.config.api_email_address()
        expected = 'test_api@example.org'

        self.assertEqual(result, expected)

    def test_agent_email_address(self):
        """Test agent email address retrieval"""
        # Test from yaml file
        result = self.config.agent_email_address()
        expected = 'test_agent@example.org'

        self.assertEqual(result, expected)

    def test_daemon_directory(self):
        """Testing function daemon_directory."""
        # Nothing should happen. Directory exists in testing.
        _ = self.config.daemon_directory()

    def test_system_daemon_directory(self):
        """Testing function system_daemon_directory."""
        # Nothing should happen. Directory exists in testing.
        _ = self.config.system_daemon_directory()

    def test_log_directory(self):
        """Testing function log_directory."""
        # Nothing should happen. Directory exists in testing.
        _ = self.config.log_directory()

    def test_log_file(self):
        """Testing function log_file."""
        # Initialize key values
        expected = '{1}{0}pattoo.log'.format(
            os.sep, self.config.log_directory())

        # Test
        result = self.config.log_file()
        self.assertEqual(result, expected)

    def test_log_file_api(self):
        """Testing function log_file_api."""
        # Initialize key values
        expected = '{1}{0}pattoo-api.log'.format(
            os.sep, self.config.log_directory())

        # Test
        result = self.config.log_file_api()
        self.assertEqual(result, expected)

    def test_log_level(self):
        """Testing function log_level."""
        # Initialize key values
        expected = 'debug'

        # Test
        result = self.config.log_level()
        self.assertEqual(result, expected)

    def test_log_file_daemon(self):
        """Testing function log_file_daemon."""
        # Initialize key values
        expected = '{1}{0}pattoo-daemon.log'.format(
            os.sep, self.config.log_directory())

        # Test
        result = self.config.log_file_daemon()
        self.assertEqual(result, expected)

    def test_cache_directory(self):
        """Testing function cache_directory."""
        # Nothing should happen. Directory exists in testing.
        _ = self.config.cache_directory()

    def test_agent_cache_directory(self):
        """Testing function agent_cache_directory."""
        # Initialize key values
        agent_id = 123
        expected = '{1}{0}{2}'.format(
            os.sep, self.config.cache_directory(), agent_id)

        # Test
        result = self.config.agent_cache_directory(agent_id)
        self.assertEqual(result, expected)


class TestBasicFunctions(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test_agent_config_filename(self):
        """Testing method or function named agent_config_filename."""
        # Test
        agent_program = 'koala_bear'
        _config_directory = log.check_environment()
        config_directory = os.path.expanduser(_config_directory)
        expected = (
            '{}{}{}.yaml'.format(config_directory, os.sep, agent_program))
        result = configuration.agent_config_filename(agent_program)
        self.assertEqual(result, expected)

    def test_get_polling_points(self):
        """Testing function _polling_points."""
        # Initialize key values
        oids = ['.1.3.6.1.2.1.2.2.1.10', '.1.3.6.1.2.1.2.2.1.16']
        data = [
            {'address': '.1.3.6.1.2.1.2.2.1.10',
             'multiplier': 8},
            {'address': '.1.3.6.1.2.1.2.2.1.16',
             'multiplier': 8}]

        # Test with good data
        result = configuration.get_polling_points(data)
        self.assertTrue(isinstance(result, list))
        self.assertTrue(bool(result))
        for index, value in enumerate(result):
            self.assertTrue(isinstance(value, PollingPoint))
            self.assertEqual(value.address, oids[index])
            self.assertEqual(value.multiplier, 8)

    def test_search(self):
        """Testing function search."""
        # Initialize key variables
        data = {
            1: {
                11: '11',
                12: '12'
            },
            2: {
                21: '21',
                22: '22'
            },
            3: {
                31: '31',
                32: '32'
            },
            4: {
                41: '41',
                42: '42'
            }
        }

        # Test OK value
        expected = '11'
        result = configuration.search(1, 11, data)
        self.assertEqual(result, expected)

        # Test all values
        for key, key_dict in data.items():
            for sub_key, expected in key_dict.items():
                result = configuration.search(key, sub_key, data)
                self.assertEqual(result, expected)

        # Test bad values
        with self.assertRaises(SystemExit):
            _ = configuration.search('1111111', 11, data)

        # Test bad values
        _ = configuration.search('1111111', 11, data, die=False)


if __name__ == '__main__':
    # Make sure the environment is OK to run unittests
    UnittestConfig().create()

    # Do the unit test
    unittest.main()
