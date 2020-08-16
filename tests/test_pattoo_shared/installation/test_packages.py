#!/usr/bin/env python3
"""Test pattoo shared packages script."""
import os
import unittest
from random import random
import sys
import tempfile

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
from pattoo_shared.installation.packages import get_installed_packages
from pattoo_shared.installation.packages import version_check

class TestPackages(unittest.TestCase):
    """Checks all functions for the Pattoo packages script."""

    @classmethod
    def setUpClass(cls):
        """Declare class attributes for Unittesting."""
        cls.venv_dir = tempfile.mkdtemp()
        environment.environment_setup(cls.venv_dir)

    def test_install_missing_pip3(self):
        """Unittest to test the install_missing_pip3 function."""           
        # Attempt to install a test package
        install_missing_pip3('tweepy', verbose=False)

        # Try except to determine if package was installed
        try:
            import tweepy
            result = True
        except ModuleNotFoundError:
            result = False
        self.assertTrue(result)

        # Test case that would cause the install_missing_pip3 function to fail
        with self.assertRaises(SystemExit) as cm_:
            install_missing_pip3('This does not exist', False)
        self.assertEqual(cm_.exception.code, 2)

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
            installed_packages = [package.decode().split('==')[
                    0] for package in packages.split()]
            result = expected_package in installed_packages
            self.assertEqual(result, expected)

    def test_get_installed_packages(self):
        """Unittest to test the get_installed packages function."""
        packages = shared.run_script('python3 -m pip freeze')[1]

        # Get packages with versions removed
        pkg_names = [
            package.decode().split('==')[0] for package in packages.split()
            ]
        pkg_versions = [
            package.decode().split('==')[0] for package in packages.split()
            ]
        expected = dict(zip(pkg_names, pkg_versions))
        result = get_installed_packages()
        self.assertEqual(result, expected)

    def test_version_check(self):
        """Unittest to test the version_check function."""
        # Test with outdated pattoo_shared version
        with self.subTest():
            shared.run_script('pip3 install PattooShared==0.0.89')
            packages = get_installed_packages()
            self.assertFalse(version_check('PattooShared', packages))

        # Test by updating pattoo shared
        with self.subTest():
            shared.run_script('pip3 install PattooShared -U')
            packages = get_installed_packages()
            self.assertTrue(version_check('PattooShared', packages))


if __name__ == '__main__':
    # Make sure the environment is OK to run unittests
    UnittestConfig().create()

    # Do the unit test
    unittest.main()
