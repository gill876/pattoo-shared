"""Functions for configuring pattoo components"""
# Standard imports
import os
import grp
import pwd
import getpass

# Import dependendices
import yaml

# Import pattoo related libraries
from pattoo_shared import files, log
from pattoo_shared.installation import shared


def create_user(user_name, directory, shell, verbose):
    """Create user and their respective group.

    Args:
        user_name: The name and group of the user being created
        directory: The home directory of the user
        shell: The shell of the user
        verbose: A boolean value that a allows the script to run in verbose
        mode

    Returns:
        None
    """
    # Ensure user has sudo privileges
    if getpass.getuser() == 'root':

        # If the group specified does not exist, it gets created
        if not group_exists(user_name):
            shared.run_script('groupadd {0}'.format(user_name), verbose)

        # If the user specified does not exist, they get created
        if not user_exists(user_name):
            shared.run_script(
                'useradd -d {1} -s {2} -g {0} {0}'.format(
                    user_name, directory, shell), verbose)
    else:
        # Die if not root
        shared.log('You are currently not running the script as root')


def group_exists(group_name):
    """Check if the group already exists.

    Args:
        group_name: The name of the group

    Returns
        True if the group exists and False if it does not
    """
    try:
        # Gets group name
        grp.getgrnam(group_name)
        return True
    except KeyError:
        return False


def read_config(filepath, default_config):
    """Read configuration file and replace default values.

    Args:
        filepath: Name of configuration file
        default_config: Default configuration dict

    Returns:
        config: Dict of configuration

    """
    # Convert config to yaml
    default_config_string = yaml.dump(default_config)

    # Read config
    if os.path.isfile(filepath) is True:
        with open(filepath, 'r') as f_handle:
            yaml_string = (
                '{}\n{}'.format(default_config_string, f_handle.read()))
            config = yaml.safe_load(yaml_string)
    else:
        config = default_config

    return config


def secondary_key_check(config, primary, secondaries):
    """Check secondary keys.

    Args:
        config: Configuration dict
        primary: Primary key
        secondaries: List of secondary keys

    Returns:
        None

    """
    # Check keys
    for key in secondaries:
        if key not in config[primary]:
            log_message = ('''\
Configuration file's "{}" section does not have a "{}" sub-section. \
Please fix.'''.format(primary, key))
            log.log2die_safe(1062, log_message)


def check_config(config_file, config_dict):
    """Ensure agent configuration exists.

    Args:
        config: The name of the configuration file
        config_dict: A dictionary containing the primary configuration keys
        and a list of the secondary keys

    Returns:
        None

    """
    # Initialize key variables
    config_directory = os.environ['PATTOO_CONFIGDIR']

    # Print Status
    print('??: Checking configuration parameters.')

    # Retrieve config dict
    config = files.read_yaml_file(config_file)

    # Check main keys
    for primary in config_dict:
        if primary not in config:
            log_message = ('''\
Section "{}" not found in configuration file {} in directory {}. Please fix.\
    '''.format(primary, config_file, config_directory))
            log.log2die_safe(1055, log_message)

        # Retrieve and check secondary keys
        secondary_list = list(config_dict.get(primary).keys())

        # Run secondary key check
        secondary_key_check(config, primary, secondary_list)

    # Print Status
    print('OK: Configuration parameter check passed.')


def user_exists(user_name):
    """Check if the user already exists.

    Args:
        user_name: The name of the user

    Returns
        True if the user exists and False if it does not

    """
    try:
        # Gets user name
        pwd.getpwnam(user_name)
        return True
    except KeyError:
        return False


def pattoo_config(file_name, config_directory, config_dict):
    """Create configuration file.

    Args:
        file_name: Name of the configuration file without its file extension
        config_directory: Full path to the configuration directory
        config_dict: A dictionary containing the configuration values.

    Returns:
        The path to the configuration file

    """
    # Initialize key variables
    config_file = os.path.join(config_directory, '{}.yaml'.format(file_name))

    # Say what we are doing
    print('\nConfiguring {} file.\n'.format(config_file))

    # Get configuration
    config = read_config(config_file, config_dict)

    # Retrieve dictionary keys
    keys = config.keys()

    # Check validity of directories, if any
    for primary_key in keys:
        for key, value in sorted(config[primary_key].items()):
            if 'directory' in key:
                if os.sep not in value:
                    log.log2die_safe(
                        1019, '{} is an invalid directory'.format(value))

                # Attempt to create directory
                full_directory = os.path.expanduser(value)
                if os.path.isdir(full_directory) is False:
                    files.mkdir(full_directory)

                # Recursively set file ownership to pattoo user and group
                if getpass.getuser == 'root':
                    shared.chown(full_directory)

    # Write file
    with open(config_file, 'w') as f_handle:
        yaml.dump(config, f_handle, default_flow_style=False)

    return config_file
