#!/usr/bin/env python3
"""Test pattoo shared packages script."""
import os
import unittest
from random import random
import sys
import tempfile
import json
import urllib

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
from pattoo_shared.installation import shared, environment
from pattoo_shared.installation.packages import install, install_missing_pip3
from pattoo_shared.installation.packages import get_package_version, check_outdated_packages


class TestPackages(unittest.TestCase):
    """Checks all functions for the Pattoo packages script."""

    @classmethod
    def setUpClass(cls):
        """Declare class attributes for Unittesting."""
        cls.venv_dir = tempfile.mkdtemp()
        environment.environment_setup(cls.venv_dir)

    def test_install_missing_pip3(self):
        """Unittest to test the install_missing_pip3 function.""" 
        # Test with expected behaviour
        with self.subTest(): 
            # Attempt to install a test package
            install_missing_pip3('tweepy', verbose=False)

            # Try except to determine if package was installed
            try:
                import tweepy
                result = True
            except ModuleNotFoundError:
                result = False
            self.assertTrue(result)

        # Test case that would cause the install_missing_pip3
        # function to fail
        with self.subTest():
            with self.assertRaises(SystemExit) as cm_:
                install_missing_pip3('This does not exist', False)
            self.assertEqual(cm_.exception.code, 2)

        # Test with outdated package version
        with self.subTest():
            install_missing_pip3('matplotlib==3.3.0', False)
            expected = '3.3.0'
            result = get_package_version('matplotlib')
            self.assertEqual(result, expected)

        # Test with non-existent package version
        with self.subTest():
            with self.assertRaises(SystemExit) as cm_:
                install_missing_pip3('pandas==100000')
            self.assertEqual(cm_.exception.code, 2)

        # Test package reinstall to more updated version
        with self.subTest():
            install_missing_pip3('matplotlib==3.3.1')
            expected = '3.3.1'
            result = get_package_version('matplotlib')
            self.assertEqual(result, expected)

    def test_install(self):
        """Unittest to test the install function."""
        # Test with undefined requirements directory
        with self.subTest():
            with self.assertRaises(SystemExit) as cm_:
                requirements_dir = data.hashstring(str(random()))
                install(requirements_dir, self.venv_dir)
            self.assertEqual(cm_.exception.code, 3)

        # Test with default expected behaviour
        with self.subTest():
            # At least one expected package
            expected_package = 'Flask'
            expected = True

            # Create temporary directory
            result = install(ROOT_DIR, self.venv_dir)

            # Get raw packages in requirements format
            packages = shared.run_script('python3 -m pip freeze')[1]

            # Get packages with versions removed
            installed_packages = [
                package.decode().split('==')[0] for package in packages.split()
                ]
            result = expected_package in installed_packages
            self.assertEqual(result, expected)

    def test_get_package_version(self):
        """Unittest to test the get_package_version function."""
        package = 'PattooShared'
        shared.run_script('python3 -m pip install {}==0.0.90'.format(package))
        result = get_package_version(package)
        expected = '0.0.90'
        self.assertEqual(result, expected)

    def test_check_outdated_packages(self):
        """Unittest to test the check_outdated_packages function."""
        # Initialize key variables
        package_dict = {
            'Flask': '1.1.0',
            'pandas': '1.0.5',
            'PyNaCl': '1.4.0',
            'distro': '1.5.0'
        }

        packages = [
            'Flask<=1.1.0', 'pandas==1.0.5', 'PyNaCl>=1.3', 'distro<1.5.0']

        # Install the packages
        for package in package_dict:
            shared.run_script('pip3 install {}'.format(package))

        # Check if they're outdated based on the packages list
        check_outdated_packages(packages, verbose=True)

        # Iterate over package dict and perform unittests
        for package in package_dict:
            with self.subTest():
                result = get_package_version(package)
                expected = package_dict.get(package)
                self.assertEqual(result, expected)


if __name__ == '__main__':
    # Make sure the environment is OK to run unittests
    UnittestConfig().create()

    # Do the unit test
    unittest.main()
