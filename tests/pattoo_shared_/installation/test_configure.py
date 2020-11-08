#!/usr/bin/env/python3
"""Test pattoo configuration script."""

import os
import getpass
import grp
import unittest
import unittest.mock
import sys
import tempfile
from collections import defaultdict
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
from tests.libraries import general
from pattoo_shared.installation import configure


class Test_Config(unittest.TestCase):
    """Checks all functions for the Pattoo config script."""

    def setUp(self):
        """Declare class attributes for Unittesting."""
        # Initialize key variables
        self.modifications = {
            'pattoo_api_agentd': {
                'ip_bind_port': 60601,
                'ip_listen_address': '::1'},
            'pattoo_apid': {
                'ip_bind_port': 60602,
                'ip_listen_address': '::3'},
            'pattoo_db': {
                'db_hostname': 'localhost',
                'db_max_overflow': 100,
                'db_name': 'pattoo',
                'db_password': 'n5PaNcV85vR6jmW3',
                'db_username': 'pattoo'},
            'pattoo_ingesterd': {
                'ingester_interval': 3600,
                'multiprocessing': True}
        }

        self.default = {
            'pattoo_api_agentd': {
                'api_encryption_email': 'test_api@example.org',
                'ip_bind_port': 20201,
                'ip_listen_address': '0.0.0.0'},
            'pattoo_apid': {
                'access_token_exp': '15_m',
                'ip_bind_port': 20202,
                'ip_listen_address': '0.0.0.0',
                'jwt_secret_key': '9uBqwWTc-02c2aaK99ULdQ',
                'refresh_token_exp': '1_D'},
            'pattoo_db': {
                'db_hostname': 'localhost',
                'db_max_overflow': 20,
                'db_name': 'pattoo',
                'db_password': 'password',
                'db_pool_size': 10,
                'db_username': 'pattoo'},
            'pattoo_ingesterd': {
                'batch_size': 500,
                'graceful_timeout': 10,
                'ingester_interval': 3600},
            'boo': 'boo'
        }

        self.existing = {
            'pattoo_api_agentd': {
                'api_encryption_email': 'test_api@example.org',
                'ip_bind_port': 60601,
                'ip_listen_address': '::1'},
            'pattoo_apid': {
                'access_token_exp': '15_m',
                'ip_bind_port': 60602,
                'ip_listen_address': '::3',
                'refresh_token_exp': '1_D'},
            'pattoo_db': {
                'db_hostname': 'localhost',
                'db_max_overflow': 100,
                'db_name': 'pattoo',
                'db_password': 'n5PaNcV85vR6jmW3',
                'db_pool_size': 10,
                'db_username': 'pattoo'},
            'pattoo_ingesterd': {
                'multiprocessing': True},
            }

        self.expected = {
            'pattoo_api_agentd': {
                'api_encryption_email': 'test_api@example.org',
                'ip_bind_port': 60601,
                'ip_listen_address': '::1'},
            'pattoo_apid': {
                'access_token_exp': '15_m',
                'ip_bind_port': 60602,
                'ip_listen_address': '::3',
                'jwt_secret_key': '9uBqwWTc-02c2aaK99ULdQ',
                'refresh_token_exp': '1_D'},
            'pattoo_db': {
                'db_hostname': 'localhost',
                'db_max_overflow': 100,
                'db_name': 'pattoo',
                'db_password': 'n5PaNcV85vR6jmW3',
                'db_pool_size': 10,
                'db_username': 'pattoo'},
            'pattoo_ingesterd': {
                'batch_size': 500,
                'graceful_timeout': 10,
                'ingester_interval': 3600,
                'multiprocessing': True},
            'boo': 'boo'
            }

    def test__merge_config(self):
        """Unittest to test the _merge_config function."""
        # Initialize key variables
        default = deepcopy(self.default)
        modifications = deepcopy(self.modifications)
        expected = deepcopy(self.expected)
        new_expected = deepcopy(expected)

        # Test
        result = configure._merge_config(default, modifications)
        self.assertTrue(isinstance(result, dict))
        self.assertFalse(isinstance(result, defaultdict))
        self.assertEqual(sorted(result), sorted(expected))

        # Make sure there are no defaultdict objects in the result.
        # yaml.safe_dump doesn't work correctly if defaultdicts are present.
        for _, value in result.items():
            self.assertFalse(isinstance(value, defaultdict))

        # Test with key not found in default
        modifications['test'] = 'test'
        new_expected['test'] = 'test'
        result = configure._merge_config(default, modifications)
        self.assertTrue(isinstance(result, dict))
        self.assertFalse(isinstance(result, defaultdict))
        self.assertEqual(sorted(result), sorted(new_expected))

        # Make sure there are no defaultdict objects in the result.
        # yaml.safe_dump doesn't work correctly if defaultdicts are present.
        for _, value in result.items():
            self.assertFalse(isinstance(value, defaultdict))

    def test_read(self):
        """Unittest to test the read method."""
        # Initialize key variables
        default = deepcopy(self.default)
        expected = deepcopy(self.expected)
        existing = deepcopy(self.existing)

        # Create temporary directory using the temp file package
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, 'pattoo_temp_config.yaml')

            # Delete file if already exists
            if os.path.exists(file_path) is True:
                os.remove(file_path)
            self.assertFalse(os.path.isfile(file_path))

            # Create configuration file
            with open(file_path, 'w') as fh_:
                yaml.safe_dump(existing, stream=fh_, default_flow_style=False)
            config = configure._Config(file_path, existing)
            result = config.read()
            self.assertEqual(result, existing)

            # Test updating the configuration
            config = configure._Config(file_path, default)
            result = config.read()
            for key, value in result.items():
                self.assertEqual(expected[key], value)
            self.assertEqual(sorted(result), sorted(expected))

    def test_update(self):
        """Test the update method."""
        # Initialize key variables
        default = deepcopy(self.default)
        expected = deepcopy(self.expected)
        existing = deepcopy(self.existing)
        filename = 'pattoo_temp_config'
        key = 'pattoo_apid'

        # Test with no existing configuration
        with tempfile.TemporaryDirectory() as temp_dir:
            # Configuration file should not exist
            file_path = os.path.join(temp_dir, '{}.yaml'.format(filename))
            self.assertFalse(os.path.isfile(file_path))

            # Test
            config = configure._Config(file_path, default)
            config.update()
            self.assertTrue(os.path.isfile(file_path))

            # Test to make sure the configuration was created
            result = config.read()
            self.assertEqual(result, default)

        # Test with existing configuration
        with tempfile.TemporaryDirectory() as temp_dir:
            # Configuration file should not exist
            file_path = os.path.join(temp_dir, '{}.yaml'.format(filename))
            self.assertFalse(os.path.isfile(file_path))

            # Create configuration file
            with open(file_path, 'w') as fh_:
                yaml.safe_dump(
                    existing, stream=fh_, default_flow_style=False)

            # Configuration file should exist
            self.assertTrue(os.path.isfile(file_path))

            # Test
            config = configure._Config(file_path, default)
            config.update()
            with open(file_path, 'r') as fh_:
                result = yaml.safe_load(fh_.read())

            # self.assertEqual(result, existing)
            self.assertEqual(result, expected)

        # Test with existing configuration with directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Configuration file should not exist
            file_path = os.path.join(temp_dir, '{}.yaml'.format(filename))
            self.assertFalse(os.path.isfile(file_path))

            # Create and delete a temporary directory
            new_dir = tempfile.mkdtemp()
            os.rmdir(new_dir)
            self.assertFalse(os.path.isdir(new_dir))

            # Update the configuration
            new_default = deepcopy(default)
            new_expected = deepcopy(expected)
            new_default[key]['dummy_directory'] = new_dir
            new_expected[key]['dummy_directory'] = new_dir

            # Create configuration file
            with open(file_path, 'w') as fh_:
                yaml.safe_dump(
                    existing, stream=fh_, default_flow_style=False)

            # Configuration file should exist
            self.assertTrue(os.path.isfile(file_path))

            # Test
            config = configure._Config(file_path, new_default)
            config.update()
            with open(file_path, 'r') as fh_:
                result = yaml.safe_load(fh_.read())
            self.assertEqual(result, new_expected)

            # Verify the creation of the new directory
            self.assertTrue(os.path.isdir(new_dir))
            os.rmdir(new_dir)
            self.assertFalse(os.path.isdir(new_dir))

    def test_validate(self):
        """Test the update method."""
        # Initialize key variables
        key = 'pattoo_apid'
        default = deepcopy(self.default)
        existing = deepcopy(self.existing)
        existing.pop(key)

        # Create temporary directory using the temp file package
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, 'pattoo_temp_config.yaml')

            # Delete file if already exists
            if os.path.exists(file_path) is True:
                os.remove(file_path)
            self.assertFalse(os.path.isfile(file_path))

            # Create configuration file
            with open(file_path, 'w') as fh_:
                yaml.safe_dump(existing, stream=fh_, default_flow_style=False)

            # Test, nothing should happen
            config = configure._Config(file_path, default)
            config.validate()

    def test__create_directories(self):
        """Unittest to test the _create_directories function."""
        # Initialize key variables
        key = 'pattoo_apid'
        default = deepcopy(self.default)
        directory = tempfile.mkdtemp()
        os.rmdir(directory)
        default[key]['test_directory'] = directory

        # Test
        self.assertFalse(os.path.isdir(directory))
        configure._create_directories(default)
        self.assertTrue(os.path.isdir(directory))
        os.rmdir(directory)
        self.assertFalse(os.path.isdir(directory))

    def test_configure_component(self):
        """Unittest to test the configure_component function."""
        # Initialize key variables
        test_name = general.random_string()
        expected = {
            'polling_interval': 300,
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, '{}.yaml'.format(test_name))

            # Create config file
            configure.configure_component(test_name, temp_dir, expected)

            # Retrieve config dict from yaml file
            config = configure._Config(file_path, expected)
            result = config.read()
            self.assertEqual(result, expected)


class TestUserFunctions(unittest.TestCase):
    """Checks all functions for the Pattoo config script."""

    def test_create_user(self):
        """Unittest to test the create_user function."""
        pass

    def test_group_exists(self):
        """Unittest to test the group_exists function."""
        # Test case for when the group does not exist
        with self.subTest():
            expected = False

            # Generating random string
            result = configure.group_exists(general.random_string())
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
            result = configure.user_exists(general.random_string())
            self.assertEqual(result, expected)

        # Test case for when the user does exist
        with self.subTest():
            expected = True
            result = configure.user_exists(getpass.getuser())
            self.assertEqual(result, expected)


if __name__ == '__main__':
    # Make sure the environment is OK to run unittests
    UnittestConfig().create()

    # Do the unit test
    unittest.main()
