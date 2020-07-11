# Main python libraries
import sys
import os
import getpass

# Pattoo libraries

import shared
sys.path.append(os.pardir)
from pattoo_shared import configuration
from pattoo_shared import log


def install_missing(package, pip_dir, verbose):
    """Automatically Install missing pip3 packages.

    Args:
        package: The pip3 package to be installed
        pip_dir: The directory the packages should be installed to

    Returns:
        True: if the package could be successfully installed

    """
    # Installs to the directory specified as pip_dir if the user is not travis
    if getpass.getuser() != 'travis':
        shared.run_script(
            'python3 -m pip install {0} -t {1}'.format(package, pip_dir),
            verbose)
    else:
        shared.run_script(
            'python3 -m pip install {0}'.format(package), verbose)
    return True


def check_pip3(verbose, pip3_dir, requirements_file):
    """Ensure PIP3 packages are installed correctly.

    Args:
        prompt_value: A boolean value to toggle the script's verbose mode and
                      enable the pip3 directory to be manually set.
        requirements_file: The filepath to the pip_requirements file.

    Returns:
        True if pip3 packages are installed successfully.

    """
    # Initialize key variables
    lines = []
    config_obj = configuration.Config()

    # Appends pip3 dir to python path
    sys.path.append(pip3_dir)

    # Read pip_requirements file
    print('??: Checking pip3 packages')
    if os.path.isfile(requirements_file) is False:
        log.log2die_safe(51011, 'Cannot find PIP3 requirements file {}'.format(
                                                        requirements_file))

    # Opens pip_requirements file for reading
    with open(requirements_file, 'r') as _fp:
        line = _fp.readline()
        while line:
            # Strip line
            _line = line.strip()
            # Read line
            if True in [_line.startswith('#'), bool(_line) is False]:
                pass
            else:
                lines.append(_line)
            line = _fp.readline()
    for line in lines:

        # Determine the package
        package = line.split('=', 1)[0]
        package = package.split('>', 1)[0]

        # If verbose is true, the package being checked is shown
        if verbose:
            print('??: Checking package {}'.format(package))
        command = 'python3 -m pip show {}'.format(package)
        (returncode, _, _) = shared.run_script(command, verbose, die=False)
        if bool(returncode) is True:

            # Installs missing pip3 package
            install_missing(package, pip3_dir, verbose)

        # If the verbose is True, the package will be shown
        if verbose:
            print('OK: package {}'.format(line))

    # Set ownership of python packages to pattoo user
    if getpass.getuser() != 'travis' and getpass.getuser() == 'root':
        config_obj.initialize_ownership('pattoo', 'pattoo', pip3_dir)
    print('OK: pip3 packages successfully installed')
    return True
