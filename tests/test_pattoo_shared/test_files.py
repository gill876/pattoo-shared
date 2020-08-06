#!/usr/bin/env python3
"""Test the files module."""

# Standard imports
import unittest
import os
import tempfile
import sys
import json
from math import pi
from random import randint
import shutil
from random import random

# PIP imports
import yaml

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
from pattoo_shared import files
from pattoo_shared.configuration import Config
from tests.libraries.configuration import UnittestConfig


class TestBasicFunctions(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    prefix = 'unittest'
    agent_hostname = 'pattoo_host'
    config = Config()

    def test_execute(self):
        """Testing method or function named execute."""
        # Test known bad command
        command = '{}'.format(random())
        with self.assertRaises(SystemExit):
            files.execute(command)

        # Test known bad command, but don't die
        command = '{}'.format(random())
        result = files.execute(command, die=False)
        self.assertTrue(bool(result))

        # Test known good command (Works in Windows and Linux)
        result = files.execute('date')
        self.assertFalse(bool(result))

    def test_read_yaml_files(self):
        """Testing method or function named read_yaml_files."""
        # Initializing key variables
        dict_1 = {
            'key1': 1,
            'key2': 2,
            'key3': 3,
            'key4': 4,
        }

        dict_2 = {
            'key6': 6,
            'key7': 7,
        }
        dict_3 = {}

        # Populate a third dictionary with contents of other dictionaries.
        for key, value in dict_1.items():
            dict_3[key] = value

        for key, value in dict_2.items():
            dict_3[key] = value

        # Create temp file with known data
        directory = tempfile.mkdtemp()
        filenames = {
            '{}{}file_1.yaml'.format(directory, os.sep): dict_1,
            '{}{}file_2.yaml'.format(directory, os.sep): dict_2
        }
        for filename, data_dict in filenames.items():
            with open(filename, 'w') as filehandle:
                yaml.dump(data_dict, filehandle, default_flow_style=False)

        # Get Results
        result = files.read_yaml_files(directory)

        # Clean up
        for key in result.keys():
            self.assertEqual(dict_3[key], result[key])
        filelist = [
            next_file for next_file in os.listdir(
                directory) if next_file.endswith('.yaml')]
        for delete_file in filelist:
            delete_path = '{}{}{}'.format(directory, os.sep, delete_file)
            os.remove(delete_path)
        os.removedirs(directory)

    def test_read_yaml_file(self):
        """Testing function read_yaml_file."""
        # Initializing key variables
        dict_1 = {
            'key1': 1,
            'key2': 2,
            'key3': 3,
            'key4': 4,
        }

        # Create a temporary file without a json extension and test
        tmp = tempfile.NamedTemporaryFile(delete=False)
        with self.assertRaises(SystemExit):
            _ = files.read_yaml_file(tmp.name)
        os.remove(tmp.name)

        # Create temp file with known data
        directory = tempfile.mkdtemp()
        file_data = [
            (('{}{}file_1.yaml').format(directory, os.sep), dict_1)
        ]
        for item in file_data:
            filename = item[0]
            data_dict = item[1]
            with open(filename, 'w') as filehandle:
                yaml.dump(data_dict, filehandle, default_flow_style=False)

            # Get Results
            result = files.read_yaml_file(filename)

            # Test equivalence
            for key in result.keys():
                self.assertEqual(data_dict[key], result[key])

        # Clean up
        filelist = [
            next_file for next_file in os.listdir(
                directory) if next_file.endswith('.yaml')]
        for delete_file in filelist:
            delete_path = ('{}{}{}').format(directory, os.sep, delete_file)
            os.remove(delete_path)
        os.removedirs(directory)

    def test_read_json_files(self):
        """Testing method or function named read_json_files."""
        # Initializing key variables
        dict_1 = {
            'key1': 1,
            'key2': 2,
            'key3': 3,
            'key4': 4,
        }

        dict_2 = {
            'key6': 6,
            'key7': 7,
        }

        # Create a temporary file without a json extension and test
        directory = tempfile.mkdtemp()
        with self.assertRaises(SystemExit):
            _ = files.read_json_files(directory)
        os.removedirs(directory)

        # Create a temporary file without a json extension and test
        directory = tempfile.mkdtemp()
        with self.assertRaises(SystemExit):
            _ = files.read_json_files(directory, die=True)
        os.removedirs(directory)

        # Test with die being False. Nothing should happen
        directory = tempfile.mkdtemp()
        _ = files.read_json_files(directory, die=False)
        os.removedirs(directory)

        # Create temp file with known data
        directory = tempfile.mkdtemp()
        filenames = {
            '{}{}file_1.json'.format(directory, os.sep): dict_1,
            '{}{}file_2.json'.format(directory, os.sep): dict_2
        }
        for filename, data_dict in filenames.items():
            with open(filename, 'w') as filehandle:
                json.dump(data_dict, filehandle)

        # Get Results
        result = files.read_json_files(directory)

        # First test, only 2 files
        self.assertEqual(len(result), 2)

        # Clean up
        for filepath, data in result:
            self.assertEqual(filepath in filenames, True)
            for key, value in sorted(data.items()):
                self.assertEqual(filenames[filepath][key], value)
            os.remove(filepath)
        os.removedirs(directory)

    def test_read_json_file(self):
        """Testing function read_json_file."""
        # Initialize key variables
        data = {
            'key1': 1,
            'key2': 2,
            'key3': 3,
            'key4': 4,
        }

        # Create a temporary file without a json extension and test
        tmp = tempfile.NamedTemporaryFile(delete=False)
        with self.assertRaises(SystemExit):
            _ = files.read_json_file(tmp.name)
        os.remove(tmp.name)

        # Create a temporary file without a json extension and test
        tmp = tempfile.NamedTemporaryFile(delete=False)
        with self.assertRaises(SystemExit):
            _ = files.read_json_file(tmp.name, die=True)
        os.remove(tmp.name)

        # Test with die being False. Nothing should happen
        tmp = tempfile.NamedTemporaryFile(delete=False)
        _ = files.read_json_file(tmp.name, die=False)
        os.remove(tmp.name)

        # Create json file and test
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        with open(tmp.name, 'w') as f_handle:
            json.dump(data, f_handle)
        result = files.read_json_file(tmp.name)
        self.assertEqual(len(result), 4)
        for key, value in sorted(result.items()):
            self.assertEqual(data[key], value)
        os.remove(tmp.name)

    def test_mkdir(self):
        """Testing function mkdir."""
        # Test with file, not directory
        tmpfile = tempfile.NamedTemporaryFile(delete=False).name
        open(tmpfile, 'a').close()
        with self.assertRaises(SystemExit):
            files.mkdir(tmpfile)
        os.remove(tmpfile)

        # Create a sub directory of a temp directory.
        directory = '{0}tmp{0}test_pattoo-unittest{0}{1}.fake'.format(
            os.sep, randint(1, 10000) * pi)
        files.mkdir(directory)
        self.assertTrue(os.path.isdir(directory))
        shutil.rmtree(directory)

    def test_pid_file(self):
        """Testing function pid_file."""
        # Test
        filename = files._File(self.config)
        expected = filename.pid(self.prefix)
        result = files.pid_file(self.prefix, self.config)
        self.assertEqual(result, expected)

    def test_lock_file(self):
        """Testing function lock_file."""
        # Test
        filename = files._File(self.config)
        expected = filename.lock(self.prefix)
        result = files.lock_file(self.prefix, self.config)
        self.assertEqual(result, expected)

    def test_agent_id_file(self):
        """Testing function agent_id_file."""
        # Test
        filename = files._File(self.config)
        expected = filename.agent_id(self.prefix)
        result = files.agent_id_file(self.prefix, self.config)
        self.assertEqual(result, expected)

    def test_get_agent_id(self):
        """Testing method or function named get_agent_id."""
        # Test. Agent_id shouldn't change
        agent_name = random()
        expected = files.get_agent_id(agent_name, self.config)
        result = files.get_agent_id(agent_name, self.config)
        self.assertEqual(result, expected)

        # Delete the file, make sure a new ID is generated
        filename = files.agent_id_file(agent_name, self.config)
        os.remove(filename)
        _expected = files.get_agent_id(agent_name, self.config)
        _result = files.get_agent_id(agent_name, self.config)
        self.assertEqual(_result, _expected)
        self.assertNotEqual(expected, _expected)

    def test__generate_agent_id(self):
        """Testing method or function named _generate_agent_id."""
        pass

    def test_get_session_cache_dir(self):
        """Test get_session_cache_dir function"""
        # Test

        dir_name = 'session_cache'
        expected = '{}/{}'.format(
            self.config.cache_directory(), dir_name)
        result = files.get_session_cache_dir(self.config)
        self.assertEqual(result, expected)


class Test_Directory(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    config = Config()

    def test___init__(self):
        """Testing function __init__."""
        # Test
        directory = files._Directory(self.config)
        expected = self.config.daemon_directory()
        result = directory._root
        self.assertEqual(result, expected)

    def test_pid(self):
        """Testing function pid."""
        # Test
        directory = files._Directory(self.config)
        expected = '{}{}pid'.format(self.config.system_daemon_directory(), os.sep)
        result = directory.pid()
        self.assertEqual(result, expected)

    def test_lock(self):
        """Testing function lock."""
        # Test
        directory = files._Directory(self.config)
        expected = '{}{}lock'.format(self.config.system_daemon_directory(), os.sep)
        result = directory.lock()
        self.assertEqual(result, expected)

    def test_agent_id(self):
        """Testing function agent_id."""
        # Test
        directory = files._Directory(self.config)
        expected = '{}{}agent_id'\
                   .format(self.config.daemon_directory(), os.sep)
        result = directory.agent_id()
        self.assertEqual(result, expected)

    def test_keyring(self):
        """Test function keyring."""
        # Test
        directory = files._Directory(self.config)
        expected = '{}{}keys{}{}'\
                   .format(
                       self.config.daemon_directory(),
                       os.sep, os.sep, '.gnupg'
                       )
        result = directory.keyring()
        self.assertEqual(result, expected)

    def test_session_cache_directory(self):
        """Test function session_cache_directory"""
        # Test
        directory = files._Directory(self.config)

        dir_name = 'session_cache'
        expected = '{}/{}'.format(
            self.config.cache_directory(), dir_name)
        result = directory.session_cache_directory()
        self.assertEqual(result, expected)


class Test_File(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    prefix = 'unittest'
    agent_hostname = 'pattoo_host'
    config = Config()

    def test___init__(self):
        """Testing function __init__."""
        pass

    def test_pid(self):
        """Testing function pid."""
        # Test
        filename = files._File(self.config)
        result = filename.pid(self.prefix)
        self.assertTrue(os.path.isdir(os.path.dirname(result)))

    def test_lock(self):
        """Testing function lock."""
        # Test
        filename = files._File(self.config)
        result = filename.lock(self.prefix)
        self.assertTrue(os.path.isdir(os.path.dirname(result)))

    def test_agent_id(self):
        """Testing function agent_id."""
        filename = files._File(self.config)
        result = filename.agent_id(self.prefix)
        self.assertTrue(os.path.isdir(os.path.dirname(result)))


class Test_GnuPG(unittest.TestCase):
    """Test Pgpier integration."""
    # Initialize config object
    config = Config()

    def test_set_gnupg(self):
        """Set Pgpier object test for agent."""

        # Agent details
        agent_name = 'test_agent1'
        agent_email = 'test_agent1@example.org'

        # Result
        result = files.set_gnupg(
                    agent_name, self.config, agent_email
                                )

        # If a Pgpier object was created, a key ID would
        # be set of type str
        self.assertIsNotNone(result.keyid)
        self.assertIsInstance(result.keyid, str)

    def test_get_gnupg(self):
        """Test retrieval of Pgpier object."""

        # Create Pgpier object
        # Agent details
        agent_name = 'test_agent2'
        agent_email = 'test_agent2@example.org'

        # Result
        files.set_gnupg(
                    agent_name, self.config, agent_email
                        )

        # Retrieve Pgpier object
        result = files.get_gnupg(agent_name, self.config)

        # Test if the Pgpier object was retrieved
        self.assertIsNotNone(result)


if __name__ == '__main__':
    # Make sure the environment is OK to run unittests
    UnittestConfig().create()

    # Do the unit test
    unittest.main()
