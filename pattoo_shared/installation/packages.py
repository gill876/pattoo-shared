"""Functions for installing external packages."""
# Standard imports
import os
import getpass
import re
from collections import namedtuple

# Import pattoo related libraries
from pattoo_shared.installation import shared
from pattoo_shared.installation import environment
from pattoo_shared import log


def installed_version(package):
    """Retrieve installed pip package version.

    Args:
        package: The name of the package

    Returns:
        version: The version of the package if the package is installed.
        None: If the package is not installed

    """
    # Initialize key variable
    version = None
    output = ''

    # Get desired package name and version
    details = package_details(package)

    # Get version from OS
    try:
        (_, output, __) = shared.run_script(
            'python3 -m pip show {}'.format(details.name),
            verbose=False)
    except:
        return version

    # Process data
    lines = output.decode().strip().split('\n')
    if bool(lines):
        version = lines[1].split(':')[1].strip()
    return version


def install_package(package, verbose=False):
    """Automatically Install missing pip3 packages.

    Args:
        package: The pip3 package to be installed

    Returns:
        None

    """
    # Initialize key variables
    command = (
        'python3 -m pip install --force-reinstall {0}'.format(package))

    # Get desired package name and version
    details = package_details(package)

    # Return if there is no package
    if bool(details.name) is False:
        return

    # Get installed version
    current_version = installed_version(package)

    # Update if there is a '<' or '>' in the desired package.
    if bool(current_version) is True and bool(details.inequality) is False:
        # Do nothing if installed and proposed versions match,
        # or no desired version specified
        if (current_version == details.version) or (details.version is None):
            return

    # Install
    try:
        shared.run_script(command, verbose=verbose)
    except SystemExit:
        message = 'Invalid pip package/package version "{}"'.format(package)
        log.log2die_safe(1088, message)


def install(requirements_dir, install_dir, verbose=False):
    """Ensure PIP3 packages are installed correctly.

    Args:
        requirements_dir: The directory with the pip_requirements file.
        install_dir: Directory where packages must be installed.
        verbose: Print status messages if True

    Returns:
        True if pip3 packages are installed successfully

    """
    # Initialize key variables
    lines = []
    filepath = '{}{}pip_requirements.txt'.format(requirements_dir, os.sep)
    path = environment.PIPpath('{}/bin'.format(install_dir))

    # Say what we are doing
    print('Checking pip3 packages')
    if os.path.isfile(filepath) is False:
        shared.log('Cannot find PIP3 requirements file {}'.format(filepath))

    # Opens pip_requirements file for reading
    try:
        _fp = open(filepath, 'r')
    except PermissionError:
        log.log2die_safe(1079, '''\
Insufficient permissions for reading the file: {}. \
Ensure the file has read-write permissions and try again'''.format(filepath))
    else:
        with _fp:
            lines = _fp.readlines()

    # Strip unprintable characters from ends
    lines = [_.strip() for _ in lines]

    # Remove comments and blank lines
    packages = [
        _ for _ in lines if (_.startswith('#') is False) and (bool(_) is True)]

    # Process each line of the file
    for package in packages:
        # We need to pre-pend the install_dir to the OS path for venv version
        # of Python3 pip to correctly identify packages installed in the
        # venv environment
        path.set()
        install_package(package, verbose=verbose)
        path.reset()

    # Set ownership of any newly installed python packages to pattoo user
    if getpass.getuser() == 'root':
        if os.path.isdir(install_dir) is True:
            shared.run_script('chown -R pattoo:pattoo {}'.format(
                install_dir), verbose=verbose)

    print('pip3 packages successfully installed')


def package_details(package):
    """Get package details.

    Args:
        package: The pip3 package to be installed

    Returns:
        result: Named tuple of package name and version

    """
    # Initialize key variables
    Package = namedtuple('Package', 'name version inequality')

    # Get desired package name and version
    nodes = re.split('=|<|>|~', package)
    _ = nodes.append(None) if len(nodes) == 1 else nodes
    (name, version) = nodes[0: 2]

    # Determine whether there is an inequality in the string
    inequality = '<' in package or '>' in package

    # Return
    result = Package(name=name, version=version, inequality=inequality)
    return result
