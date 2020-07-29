#!/usr/bin/env/python3
"""Test pattoo configuration script."""

import os
import unittest
import sys
import tempfile
import yaml
import distro
from random import random

# Try to create a working PYTHONPATH
EXEC_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(os.path.abspath(os.path.join(
    os.path.abspath(os.path.join(EXEC_DIR, os.pardir)), os.pardir)), os.pardir))
_EXPECTED = '''\
{0}pattoo-shared{0}tests{0}test_pattoo_shared{0}installation'''.format(os.sep)
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
from pattoo_shared import data
from pattoo_shared.installation.systemd import _filepaths, copy_service_files
from pattoo_shared.installation.systemd import _get_runtime_directory
from pattoo_shared.installation.systemd import update_environment_strings
from pattoo_shared.installation.systemd import symlink_dir, _check_symlinks


class Test_Systemd(unittest.TestCase):
    """Checks all functions and methods."""

    def test__filepaths(self):
        """Testing method or function named "_filepaths"."""
        # Initialize temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, 'test_file.txt')

            # Create file
            with open(file_path, 'w+') as test_file:
                test_file.write('this is a test')
            expected = [file_path]
            result = _filepaths(temp_dir)
            self.assertEqual(expected, result)

    def test_symlink_dir(self):
        """Testing method or function named "symlink_dir"."""
        # Initialise key variables
        linux_distro = distro.linux_distribution()[0].lower()
        etc_dir = '/etc/systemd/system/multi-user.target.wants'

        if linux_distro == 'ubuntu':
            expected = '/lib/systemd/system'
        else:
            # Expected directory for CentOS
            expected = '/usr/lib/systemd/system'

        # Test directory without symlinks
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(SystemExit) as cm_:
                symlink_dir(temp_dir)
            self.assertEqual(cm_.exception.code, 3)

        # Test directory with expected symlinks
        result = symlink_dir(etc_dir)
        self.assertEqual(result, expected)

    def test__get_runtime_directory_default(self):
        """Testing method or function named "_get_runtime_directory"."""
        # Initialize key variables
        default_config = {
            'pattoo': {
                'language': 'en',
                'log_directory': (
                    '/var/log/pattoo'),
                'log_level': 'debug',
                'cache_directory': (
                    '/opt/pattoo-cache'),
                'daemon_directory': (
                    '/opt/pattoo-daemon'),
                'system_daemon_directory': '/var/run/pattoo'
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

        expected = ('/var/run/pattoo', 'pattoo')

        # Retrieve runtime directory from temp directory
        with tempfile.TemporaryDirectory() as temp_dir:

            # Test with default system daemon directory
            with open(os.path.join(temp_dir, 'pattoo.yaml'), 'w+') as config:
                yaml.dump(default_config, config, default_flow_style=False)
                result = _get_runtime_directory(temp_dir)
            self.assertEqual(expected, result)

    def test__get_runtime_undefined_file(self):
        """Testing method or function named "_get_runtime_directory"."""
        with self.assertRaises(SystemExit) as cm_:
            # Generate random directory name
            _get_runtime_directory(data.hashstring(str(random())))
        self.assertEqual(cm_.exception.code, 3)

    def test__get_runtime_directory_no_systemd(self):
        """Testing method or function named "_get_runtime_directory"."""
        # Initialize key variables
        fake_config = {
            'pattoo': {
                    'language': 'en',
                    'log_directory': (
                        '/var/log/pattoo'),
                    'log_level': 'debug',
                    'cache_directory': (
                        '/opt/pattoo-cache'),
                    'daemon_directory': (
                        '/opt/pattoo-daemon')
                }
            }

        # Retrieve runtime directory from temp directory
        with tempfile.TemporaryDirectory() as temp_dir:
            with open(os.path.join(temp_dir, 'pattoo.yaml'), 'w+') as config:
                yaml.dump(fake_config, config, default_flow_style=False)

            # Test without system daemon directory
            with self.assertRaises(SystemExit) as cm_:
                _get_runtime_directory(temp_dir)
            self.assertEqual(cm_.exception.code, 3)

        def test___check_symlinks(self):
            """Testing method or function named "_get_runtime_directory"."""
            # Initialize key variables
            daemons = [
                'pattoo_apid',
                'pattoo_api_agentd',
                'pattoo_ingesterd'
                ]
            result = []

            with tempfile.TemporaryDirectory() as temp_dir:
                # Create target directory
                target_dir = os.path.join(temp_dir, 'test_symlink')
                os.mkdir(target_dir)

                # Check for symlinks and sudo access
                with self.assertRaises(SystemExit) as cm_:
                    _check_symlinks(temp_dir, daemons)
                self.assertEqual(cm_.exception.code, 3)

            self.assertTrue(all(result))


if __name__ == '__main__':
    # Make sure the environment is OK to run unittests
    UnittestConfig().create()

    # Do the unit test
    unittest.main()
