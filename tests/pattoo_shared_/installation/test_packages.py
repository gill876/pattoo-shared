#!/usr/bin/env python3
"""Test pattoo shared packages script."""
import os
import unittest
from random import random
import sys
import tempfile

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
from pattoo_shared import data
from pattoo_shared.installation import shared, environment
from pattoo_shared.installation.packages import install, install_package
from pattoo_shared.installation.packages import installed_version


class TestPackages(unittest.TestCase):
    """Checks all functions for the Pattoo packages script."""

    def setUp(self):
        """Prepare each test for testing."""
        self.venv_dir = tempfile.mkdtemp()
        self.venv = environment.environment_setup(self.venv_dir)

    def tearDown(self):
        """Cleanup each test after testing."""
        self.venv.deactivate()

    def test_install_package(self):
        """Unittest to test the install_package function."""
        # Test with expected behaviour
        with self.subTest():
            # Attempt to install a test package
            install_package('tweepy', verbose=False)

            # Try except to determine if package was installed
            try:
                import tweepy
                result = True
            except ModuleNotFoundError:
                result = False
            self.assertTrue(result)

        # Test case that would cause the install_package
        # function to fail
        with self.subTest():
            with self.assertRaises(SystemExit) as cm_:
                install_package('This does not exist', False)
            self.assertEqual(cm_.exception.code, 2)

        # Test with outdated package version
        with self.subTest():
            install_package('matplotlib==3.3.0', False)
            expected = '3.3.0'
            result = installed_version('matplotlib')
            self.assertEqual(result, expected)

        # Test with non-existent package version
        with self.subTest():
            with self.assertRaises(SystemExit) as cm_:
                install_package('pandas==100000')
            self.assertEqual(cm_.exception.code, 2)

        # Test package reinstall to more updated version
        with self.subTest():
            install_package('matplotlib==3.3.1')
            expected = '3.3.1'
            result = installed_version('matplotlib')
            self.assertEqual(result, expected)

        # Test reverting to outdated package version
        with self.subTest():
            install_package('matplotlib==3.3.0', False)
            expected = '3.3.0'
            result = installed_version('matplotlib')
            self.assertEqual(result, expected)

        # Test package reinstall to more updated version
        with self.subTest():
            install_package('matplotlib==3.3.1')
            expected = '3.3.1'
            result = installed_version('matplotlib')
            self.assertEqual(result, expected)

        # Test package reinstall to most recent version
        with self.subTest():
            install_package('matplotlib>=3.3.1')
            expected = '3.3.1'
            result = installed_version('matplotlib')
            self.assertGreater(result, expected)

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
            install(ROOT_DIR, self.venv_dir)

            # Get raw packages in requirements format
            packages = shared.run_script('python3 -m pip freeze')[1]

            # Get packages with versions removed
            installed_packages = [
                package.decode().split('==')[0] for package in packages.split()
                ]
            result = expected_package in installed_packages
            self.assertEqual(result, expected)

    def test_installed_version(self):
        """Unittest to test the installed_version function."""
        package = 'PattooShared'

        with self.subTest():
            # Uninstall package and verify
            shared.run_script(
                'python3 -m pip uninstall -y {}'.format(package))
            result = installed_version(package)
            expected = None
            self.assertEqual(result, expected)

        with self.subTest():
            # Test with installed version
            shared.run_script(
                'python3 -m pip install {}==0.0.90'.format(package))
            result = installed_version(package)
            expected = '0.0.90'
            self.assertEqual(result, expected)


if __name__ == '__main__':
    # Make sure the environment is OK to run unittests
    UnittestConfig().create()

    # Do the unit test
    unittest.main()
