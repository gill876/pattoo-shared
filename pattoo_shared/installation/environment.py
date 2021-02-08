"""Functions for setting up a virtual environment for the installation."""
import os
import getpass
from pattoo_shared.installation import shared, configure
from pattoo_shared import log


class Venv():
    """Virtual Environment class."""

    def __init__(self, directory):
        """Initialize the class.

        Args:
            directory: Activation directory

        Returns:
            None

        """
        # Initialize key variables
        self._directory = directory
        self._path = os.environ.get('PATH')

    def create(self):
        """Create virtual environment for pattoo installation.

        Args:
            None

        Returns:
            None

        """
        # Say what we're doing
        print('??: Create virtual environment')
        command = 'python3 -m virtualenv {}'.format(self._directory)
        shared.run_script(command)
        print('OK: Virtual environment created')
        # Ensure venv is owned by pattoo if the pattoo user exists
        if configure.user_exists(
                'pattoo') and configure.group_exists('pattoo'):
            if getpass.getuser() == 'root':
                shared.run_script(
                    'chown -R pattoo:pattoo {}'.format(self._directory))

    def activate(self):
        """Activate the virtual environment in the current interpreter.

        Args:
            None

        Returns:
            None

        """
        # Initialize key variables
        filepath = os.path.join(self._directory, 'bin/activate_this.py')

        # Open activte_this.py for reading
        try:
            f_handle = open(filepath)
        except PermissionError:
            log.log2die_safe(1061, '''\
Insufficient permissions on file: {}. Ensure the directory has the necessary \
read-write permissions'''.format(filepath))
        except FileNotFoundError:
            log.log2die_safe(1074, '''\
activate_this.py for the venv has not been created at {} with virtualenv. \
Ensure that its created using the module "virtualenv"
'''.format(filepath))
        else:
            with f_handle:
                code = compile(f_handle.read(), filepath, 'exec')
                exec(code, dict(__file__=filepath))

    def deactivate(self):
        """Deactivate the virtual environment in the current interpreter.

        Args:
            None

        Returns:
            None

        """
        # Reset the 'PATH' variable
        os.environ['PATH'] = self._path

        # Delete the 'VIRTUAL_ENV' reference
        venv = os.environ.get('VIRTUAL_ENV')
        if bool(venv) is True:
            del os.environ['VIRTUAL_ENV']


class PIPpath():
    """Set PIP paths for installations."""

    def __init__(self, directory):
        """Initialize the class.

        Args:
            directory: Virtual Environment directory

        Returns:
            None

        """
        # Initialize key variables
        self._directory = directory
        self._path = os.environ.get('PATH')

    def set(self):
        """Set path to view PIP packages installed in venv.

        Args:
            None

        Returns:
            None

        """
        # Set the 'PATH' variable
        os.environ['PATH'] = '{}:{}'.format(self._directory, self._path)

    def reset(self):
        """Set path to view PIP packages installed in venv.

        Args:
            None

        Returns:
            None

        """
        # Reset the 'PATH' variable
        os.environ['PATH'] = self._path


def environment_setup(directory):
    """Create and activate virtual environment.

    Args:
        directory: The path to the virtual environment

    Returns:
        venv: Venv instance

    """
    # Setup the environment
    venv = Venv(directory)
    venv.create()
    venv.activate()
    return venv
