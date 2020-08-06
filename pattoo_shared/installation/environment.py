"""Functions for setting up a virtual environment for the installation."""
import os
import getpass
from pattoo_shared.installation import shared


def make_venv(file_path):
    """Create virtual environment for pattoo installation.

    Args:
        file_path: The path to the virtual environment

    Returns:
        activation_path: The path to the activate_this.py file

    """
    # Say what we're doing
    print('??: Create virtual environment')
    command = 'python3 -m virtualenv {}'.format(file_path)
    shared.run_script(command)
    print('OK: Virtual environment created')
    # Ensure venv is owned by pattoo
    if getpass.getuser() == 'root':
        shared.run_script('chown -R pattoo:pattoo {}'.format(file_path))


def add_shebang(file_path, shebang):
    """Add shebang to the top of the file.

    This shebang should point to the interpreter for the virtual environment

    Args:
        file_path: The path to the file the shebang is being added to
        shebang: The shebang being inserted in the file

    Returns:
        None

    """
    # Open script for reading
    with open(file_path, 'r+') as f:
        content = f.readlines()

        # Check if shebang already exists
        if content[0].startswith('#!'):
            content[0] = shebang + '\n'
        else:
            content.insert(0, shebang + '\n')
        # Set pointer to beginning of file
        f.seek(0, 0)

        # Rewrite file contents
        f.write(''.join(content))


def activate_venv(activation_path):
    """Activate the virtual environment in the current interpreter.

    Args:
        activation_path: The path to the activate_this.py file

    Returns:
        None

    """
    # Open activte_this.py for reading
    with open(activation_path) as f:
        code = compile(f.read(), activation_path, 'exec')
        exec(code, dict(__file__=activation_path))


def environment_setup(file_path):
    """Create and activate virtual environment.

    Args:
        file_path: The path to the virtual environment

    Returns:
        None

    """
    # Initialize key variables
    activtion_path = os.path.join(file_path, 'bin/activate_this.py')

    make_venv(file_path)

    activate_venv(activtion_path)
