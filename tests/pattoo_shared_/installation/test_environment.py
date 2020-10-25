"""Test pattoo shared environment."""
import os
import unittest
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


class TestVenv(unittest.TestCase):
    """Checks all functions for the Pattoo environment script."""

    def test___init__(self):
        """Testing function __init__."""
        pass

    def test_create(self):
        """Testing function create."""
        pass

    def test_activate(self):
        """Testing function activate."""
        pass

    def test_deactivate(self):
        """Testing function deactivate."""
        pass


class TestFunctions(unittest.TestCase):
    """Checks all functions for the Pattoo environment script."""

    def setUp(self):
        """Prepare each test for testing."""
        self.venv_dir = tempfile.mkdtemp()
        self.venv = environment.environment_setup(self.venv_dir)

    def tearDown(self):
        """Cleanup each test after testing."""
        self.venv.deactivate()

    def test_environment_setup(self):
        """Unittest to test the environment_setup function."""

        # Ensure that there are no packages
        pip_packages = shared.run_script('python3 -m pip freeze')[1]

        # Retrieve packages without version
        installed_packages = [
            pip_helper(package) for package in pip_packages.split()]
        result = installed_packages == []
        self.assertTrue(result)

        # Test with installing a package to the venv
        packages.install_package('matplotlib', verbose=False)
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
