"""Functions for installing external packages."""
# Standard imports
import os
import getpass
import json
import urllib.request

# Import pattoo related libraries
from pattoo_shared.installation import shared
from pattoo_shared import log


def get_installed_packages():
    """Retrieve installed pip packages.

    Args:
        None

    Returns:
        package_dict:A dictionary containing the installed packages

    """
    packages = shared.run_script('python3 -m pip freeze')[1]
    # Retrieve package names
    keys = [package.decode().split('==')[0] for package in packages.split()]

    # Retrieve package versions
    values = [package.decode().split('==')[1] for package in packages.split()]

    # Create dictionary with package versions
    package_dict = dict(zip(keys, values)) 

    return package_dict


def version_check(package_name, package_dict):
    """Check if package installed is updated to its latest version.

    Args:
        package_dict: A dictionary containing the packages
        package_name: The package being checked

    Returns:
        True: If the package is updated
        False: If the package is not updated/installed

    """
    package_url = 'https://pypi.org/pypi/{}/json'.format(package_name)
    # Retrieve information on latest package version
    package_data = urllib.request.urlopen(package_url).read()
    data = json.loads(package_data)
    latest_version = data['info']['version']

    # Get version name from dictionary
    if package_dict.get(package_name) == latest_version:
        return True
    else:
        return False


def install_missing_pip3(package, verbose=False):
    """Automatically Install missing pip3 packages.

    Args:
        package: The pip3 package to be installed

    Returns:
        None

    """
    # Validate pip directory
    shared.run_script('''\
python3 -m pip install {0} -U --force-reinstall'''.format(package), verbose=verbose)


def install(requirements_dir, installation_directory, verbose=False):
    """Ensure PIP3 packages are installed correctly.

    Args:
        requirements_dir: The directory with the pip_requirements file.
        installation_directory: Directory where packages must be installed.
        verbose: Print status messages if True

    Returns:
        True if pip3 packages are installed successfully

    """
    # Initialize key variables
    lines = []

    # Read pip_requirements file
    filepath = '{}{}pip_requirements.txt'.format(requirements_dir, os.sep)

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

    # Process each line of the file
    for line in lines:
        # Determine the package
        package = line.split('=', 1)[0]
        package = package.split('>', 1)[0]

        # If verbose is true, the package being checked is shown
        if verbose:
            print('Installing package {}'.format(package))
        command = 'python3 -m pip show {}'.format(package)
        (returncode, _, _) = shared.run_script(
            command, verbose=verbose, die=False)

        # Install any missing pip3 package
        if bool(returncode) is True:
            install_missing_pip3(package, verbose=verbose)

    # Check for outdated packages
    if verbose:
        print('Checking for outdated packages')
    installed_packages = get_installed_packages()
    for key in installed_packages:
        if version_check(key, installed_packages) is False:
            # Reinstall updated version of package
            install_missing_pip3(key, verbose=verbose)

    # Set ownership of any newly installed python packages to pattoo user
    if getpass.getuser() == 'root':
        if os.path.isdir(installation_directory) is True:
            shared.run_script('chown -R pattoo:pattoo {}'.format(
                installation_directory), verbose=verbose)

    print('pip3 packages successfully installed')
