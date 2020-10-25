#!/usr/bin/env/python3
"""Test pattoo configuration script."""

import os
import getpass
import grp
import unittest
import unittest.mock
import sys
import tempfile
import io
from copy import deepcopy

import yaml

# Try to create a working PYTHONPATH
EXEC_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(
    os.path.abspath(os.path.join(
        os.path.abspath(os.path.join(
            EXEC_DIR, os.pardir)), os.pardir)), os.pardir))
_EXPECTED = '''\
{0}pattoo-shared{0}tests{0}pattoo_shared_{0}installation'''.format(os.sep)
if EXEC_DIR.endswith(_EXPECTED) is True:
    # We need to prepend the path in case PattooShared has been installed
    # elsewhere on the system using PIP. This could corrupt expected results
    sys.path.insert(0, ROOT_DIR)
else:
    print('''This script is not installed in the "{0}" directory. Please fix.\
'''.format(_EXPECTED))
    sys.exit(2)

# Pattoo imports
from tests.libraries.configuration import UnittestConfig
from pattoo_shared.installation import configure
from pattoo_shared import files


class TestConfigure(unittest.TestCase):
    """Checks all functions for the Pattoo config script."""

    @classmethod
    def setUpClass(cls):
        """Declare class attributes for Unittesting."""
        # Initialize key variables
        cls._log_directory = tempfile.mkdtemp()
        cls._cache_directory = tempfile.mkdtemp()
        cls._daemon_directory = tempfile.mkdtemp()
        cls._system_daemon_directory = tempfile.mkdtemp()
        cls.default_config = {
            'pattoo': {
                'language': 'en',
                'log_directory': cls._log_directory,
                'log_level': 'debug',
                'cache_directory': cls._cache_directory,
                'daemon_directory': cls._daemon_directory,
                'system_daemon_directory': cls._system_daemon_directory
            },
            'pattoo_agent_api': {
                'ip_address': '127.0.0.1',
                'ip_bind_port': 20201
            },
            'pattoo_web_api': {
                'ip_address': '127.0.0.1',
                'ip_bind_port': 20202,
            }
        }

        cls.updated_config = deepcopy(cls.default_config)
        cls.updated_config['encryption'] = {
            'api_email': 'api_email@example.org'}

        cls.default_server_config = {
            'pattoo_db': {
                'db_pool_size': 10,
                'db_max_overflow': 20,
                'db_hostname': 'localhost',
                'db_username': 'pattoo',
                'db_password': 'password',
                'db_name': 'pattoo'
            },
            'pattoo_api_agentd': {
                'ip_listen_address': '0.0.0.0',
                'ip_bind_port': 20201,
            },
            'pattoo_apid': {
                'ip_listen_address': '0.0.0.0',
                'ip_bind_port': 20202,
            },
            'pattoo_ingesterd': {
                'ingester_interval': 3600,
                'batch_size': 500,
                'graceful_timeout': 10
            }
        }

    def test_group_exists(self):
        """Unittest to test the group exists function."""
        # Test case for when the group does not exist
        with self.subTest():
            expected = False

            # Generating random string
            result = configure.group_exists(str(os.urandom(5)))
            self.assertEqual(result, expected)

        # Test case for when the group exists
        with self.subTest():
            expected = True

            # Creating grp.struct object
            grp_struct = grp.getgrgid(os.getgid())
            result = configure.group_exists(grp_struct.gr_name)
            self.assertEqual(result, expected)

    def test_user_exists(self):
        """Unittest to test the user_exists function."""
        # Test case for when the user does not exist
        with self.subTest():
            expected = False

            # Generating random string
            result = configure.user_exists(str(os.urandom(5)))
            self.assertEqual(result, expected)

        # Test case for when the user does exist
        with self.subTest():
            expected = True
            result = configure.user_exists(getpass.getuser())
            self.assertEqual(result, expected)

    def test_read_config(self):
        """Unittest to test the read_server_config function."""
        # Initialize key variables
        expected = self.default_config

        # Create temporary directory using the temp file package
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, 'pattoo_temp_config.yaml')

            # Delete file if already exists
            if os.path.exists(file_path) is True:
                os.remove(file_path)
            self.assertFalse(os.path.isfile(file_path))

            # Dumps default configuration to file in temp directory
            with open(file_path, 'w+') as temp_config:
                yaml.dump(expected, temp_config, default_flow_style=False)
            result = configure.read_config(file_path, expected)
            self.assertEqual(result, expected)

            # Test updating the configuration
            with self.subTest():
                expected = self.updated_config
                result = configure.read_config(file_path, expected)
                for key, value in result.items():
                    self.assertEqual(expected[key], value)

    def test_pattoo_config_server(self):
        """Test the pattoo_config function for the pattoo server."""
        # Initialize key variables
        expected = '''\
pattoo_api_agentd:
  ip_bind_port: 20201
  ip_listen_address: 0.0.0.0
pattoo_apid:
  ip_bind_port: 20202
  ip_listen_address: 0.0.0.0
pattoo_db:
  db_hostname: localhost
  db_max_overflow: 20
  db_name: pattoo
  db_password: password
  db_pool_size: 10
  db_username: pattoo
pattoo_ingesterd:
  batch_size: 500
  graceful_timeout: 10
  ingester_interval: 3600'''

        # Initialize temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, 'pattoo_server.yaml')

            # Create config file
            configure.pattoo_config(
                'pattoo_server', temp_dir, self.default_server_config)

            with open(file_path, 'r') as temp_config:

                # Remove all whitespace
                result = temp_config.read().strip()
            self.assertEqual(result, expected)

    def test_pattoo_config_default(self):
        """Unittest to test the pattoo_config function with default values."""
        # Initialize key variables
        expected = '''\
pattoo:
  cache_directory: {}
  daemon_directory: {}
  language: en
  log_directory: {}
  log_level: debug
  system_daemon_directory: {}
pattoo_agent_api:
  ip_address: 127.0.0.1
  ip_bind_port: 20201
pattoo_web_api:
  ip_address: 127.0.0.1
  ip_bind_port: 20202
'''.format(
    self._cache_directory, self._daemon_directory,
    self._log_directory, self._system_daemon_directory)

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, 'pattoo.yaml')

            # Create config file
            configure.pattoo_config('pattoo', temp_dir, self.default_config)

            # Open config file for reading
            with open(file_path, 'r') as temp_config:

                # Remove all whitespace
                result = temp_config.read()
            self.assertEqual(result, expected)

    def test_pattoo_config_custom_dict(self):
        """Test the pattoo_config function with custom dictionary."""
        # Initialize key variables
        prefix = 'pattoo'
        default_expected = self.updated_config

        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = os.path.join(temp_dir, 'pattoo/log')
            cache_dir = os.path.join(temp_dir, 'pattoo/cache')
            daemon_dir = os.path.join(temp_dir, 'pattoo/daemon')
            original = {
                'pattoo': {
                    'log_directory': log_dir,
                    'log_level': 'debug',
                    'language': 'xyz',
                    'cache_directory': cache_dir,
                    'daemon_directory': daemon_dir,
                    'system_daemon_directory': self._system_daemon_directory,
                },
                'pattoo_agent_api': {
                    'ip_address': '127.0.0.6',
                    'ip_bind_port': 50505,
                },
                'dummy_0': {
                    'dummy_1': 'dummy_2',
                    'dummy_3': 'dummy_4',
                }
            }

            expected = {
                'dummy_0': {'dummy_1': 'dummy_2', 'dummy_3': 'dummy_4'},
                'encryption': {'api_email': 'api_email@example.org'},
                'pattoo': {
                    'cache_directory': cache_dir,
                    'daemon_directory': daemon_dir,
                    'language': 'xyz',
                    'log_directory': log_dir,
                    'log_level': 'debug',
                    'system_daemon_directory': self._system_daemon_directory},
                'pattoo_agent_api': {
                    'ip_address': '127.0.0.6', 'ip_bind_port': 50505},
                'pattoo_web_api': {
                    'ip_address': '127.0.0.1', 'ip_bind_port': 20202}
            }

            file_path = os.path.join(temp_dir, '{}.yaml'.format(prefix))

            # Create config file
            configure.pattoo_config(prefix, temp_dir, original)

            # Test for directories
            result = os.path.isdir(cache_dir)
            with self.subTest():
                self.assertTrue(result)

            result = os.path.isdir(log_dir)
            with self.subTest():
                self.assertTrue(result)

            result = os.path.isdir(daemon_dir)
            with self.subTest():
                self.assertTrue(result)

            # Retrieve config dict from yaml file
            result = configure.read_config(file_path, original)
            with self.subTest():
                self.assertEqual(result, original)

            ########################
            # Test overwriting file
            ########################

            # Delete old version of file
            os.remove(file_path)

            # Create new version of config file
            configure.pattoo_config('pattoo', temp_dir, original)

            # Apply updated configuration to that read from the
            # new configuration file
            result = configure.read_config(file_path, default_expected)
            with self.subTest():
                self.assertEqual(sorted(result), sorted(expected))

    # Using mock patch to capture output
    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_check_config(self, mock_stdout):
        # Initialize key variables
        """Unittest to test the check_config function."""
        config = {
            'pattoo': {
                'log_directory': self._log_directory,
                'log_level': 'debug',
                'language': 'xyz',
                'cache_directory': self._cache_directory,
                'daemon_directory': self._daemon_directory,
                'system_daemon_directory': self._system_daemon_directory,
            },
            'pattoo_agent_api': {
                'ip_address': '127.0.0.6',
                'ip_bind_port': 50505,
            },
            'pattoo_web_api': {
                'ip_address': '127.0.0.3',
                'ip_bind_port': 30303,
            }
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, 'pattoo.yaml')

            # Initializing expected output from stdout
            expected = '''\

Configuring {} file.

??: Checking configuration parameters.
OK: Configuration parameter check passed.
'''.format(config_file)

            # Create config file
            configure.pattoo_config('pattoo', temp_dir, config)

            # Run configuration
            configure.check_config(config_file, config)
            self.assertEqual(mock_stdout.getvalue(), expected)

    def test_configure_component(self):
        """Unittest to test the configure_component function."""
        # Initialize key variables
        test_name = str(os.urandom(5))
        expected = {
            'polling_interval': 300,
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, '{}.yaml'.format(test_name))

            # Create config file
            configure.configure_component(test_name, temp_dir, expected)

            # Retrieve config dict from yaml file
            result = configure.read_config(file_path, expected)
            self.assertEqual(result, expected)


if __name__ == '__main__':
    # Make sure the environment is OK to run unittests
    UnittestConfig().create()

    # Do the unit test
    unittest.main()
