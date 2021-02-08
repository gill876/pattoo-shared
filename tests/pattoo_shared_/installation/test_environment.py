"""Test pattoo shared environment."""
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
{0}pattoo-shared{0}tests{0}pattoo_shared_{0}installation'''.format(os.sep)
if EXEC_DIR.endswith(_EXPECTED) is True:
    # We need to prepend the path in case PattooShared has been installed
    # elsewhere on the system using PIP. This could corrupt expected results
    sys.path.insert(0, ROOT_DIR)
else:
    print('''This script is not installed in the "{0}" directory. Please fix.\
'''.format(_EXPECTED))
    sys.exit(2)

from tests.libraries.configuration import UnittestConfig
from pattoo_shared.installation import environment, packages, shared


def pip_helper(package):
    """Retrieve pip package without version.

    Args:
        package: The pip package parsed from the pip requirements file

    Returns:
        The package with its version removed

    """
    return package.decode().split('==')[0]


class TestEnvironment(unittest.TestCase):
    """Checks all functions for the Pattoo environment script."""

    @classmethod
    def setUpClass(cls):
        """Declare class attributes for Unittesting."""
        cls.venv_dir = tempfile.mkdtemp()

    # test_environment_setup tests both make_venv and activate_venv
    # by creating and activating the venv
    def test_make_venv(self):
        """Unittest to test the make_venv function."""
        pass

    def test_activate_venv(self):
        """Unittest to test the activate_venv function."""
        pass

    def test_environment_setup(self):
        """Unittest to test the environment_setup function."""
        # Set up venv
        environment.environment_setup(self.venv_dir)

        # Ensure that there are no packages
        with self.subTest():
            pip_packages = shared.run_script('python3 -m pip freeze')[1]

            # Retrieve packages without version
            installed_packages = [
                pip_helper(package) for package in pip_packages.split()]
            result = installed_packages == []
            self.assertTrue(result)

        # Test with installing a package to the venv
        with self.subTest():
            packages.install_missing_pip3('matplotlib', verbose=False)
            pip_packages = shared.run_script('python3 -m pip freeze')[1]

            # Retrieve packages without version
            installed_packages = [
                pip_helper(package) for package in pip_packages.split()]
            result = 'matplotlib' in installed_packages
            self.assertTrue(result)


if __name__ == '__main__':
    # Make sure the environment is OK to run unittests
    UnittestConfig().create()

    # Do the unit test
    unittest.main()
