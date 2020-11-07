"""Functions for configuring pattoo components."""
# Standard imports
import os
import grp
import pwd
import getpass
from collections import defaultdict

# Import dependendices
import yaml

# Import pattoo related libraries
from pattoo_shared import files, log
from pattoo_shared.installation import shared


class _Config():
    """Installation configuration file manipulation class."""

    def __init__(self, filepath, default):
        """Initialize the class.

        Args:
            filepath: Configuration filename
            default: Default configuration

        Returns:
            None

        """
        # Read data
        self._filepath = filepath
        self._default = {} if isinstance(default, dict) is False else default

    def update(self):
        """Create configuration file.

        Args:
            None

        Returns:
            The path to the configuration file

        """
        # Get configuration
        config = self.read()
        filepath = self._filepath

        # Check validity of directories, if any
        if bool(config) is False:
            # Set default
            config = self._default

        # Create directories found in configuration
        _create_directories(config)

        # Update the configuration
        try:
            f_handle = open(filepath, 'w')
        except PermissionError:
            log.log2die(1076, '''\
Insufficient permissions for creating the file:{}'''.format(filepath))
        else:
            with f_handle:
                # Convert to dict, just in case as defaultdict
                # isn't supported by yaml.safe_dump
                yaml.safe_dump(
                    dict(config), stream=f_handle, default_flow_style=False)

    def read(self):
        """Read configuration file and replace default values.

        Args:
            None

        Returns:
            config: Dict of configuration

        """
        # Initialize key variables
        filepath = self._filepath
        default = self._default
        config = {}

        # Read config
        if os.path.isfile(filepath) is True:
            try:
                f_handle = open(filepath, 'r')
            except PermissionError:
                log.log2die_safe(1078, '''\
Insufficient permissions for reading the file:{}'''.format(filepath))
            else:
                with f_handle:
                    yaml_string = f_handle.read()
                    existing = yaml.safe_load(yaml_string)

            # Merge configurations
            config = _merge_config(default, existing)
        else:
            config = default
        return config

    def validate(self):
        """Do basic configuration validation.

        Args:
            None

        Returns:
            res

        """
        # Read configuration
        config = self.read()

        # Check main keys
        for primary in self._default.keys():
            if primary not in config:
                log_message = ('''\
Section "{}" not found in configuration file {}. Please fix.\
'''.format(primary, self._filepath))
                log.log2die_safe(1055, log_message)


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


def _create_directories(config):
    """Create directories found in configuration file.

    Args:
        None

    Returns:
        None

    """
    # Iterate over config dict
    for _, value in sorted(config.items()):
        if isinstance(value, dict) is True:
            for secondary_key in value.keys():
                # Directory parameter found
                if 'directory' in secondary_key:
                    if os.sep not in value.get(secondary_key):
                        log.log2die_safe(1006,
                                         'Invalid directory {}'.format(value))

                    # Attempt to create directory
                    full_directory = os.path.expanduser(
                        value.get(secondary_key))
                    if os.path.isdir(full_directory) is False:
                        files.mkdir(full_directory)

                    # Recursively set file ownership to pattoo user and group
                    if getpass.getuser() == 'root':
                        shared.chown(full_directory)


def _merge_config(default, updates):
    """Merge two lambda dicts together.

    Args:
        default: Default dict
        updates: Dict with updates for the default

    Returns:
        result: Merged dictionary

    """
    # All components of 'result' must be dicts.
    result = defaultdict(lambda: {})

    # Merge configurations
    for key, value in default.items():
        result[key] = value
        if key in updates:
            if isinstance(value, dict):
                for _key, _value in updates[key].items():
                    result[key][_key] = _value

    # Merge the other way around
    for key, value in updates.items():
        if key not in result:
            result[key] = value

    # Convert to dict to facilitate YAML file processing
    result = dict(result)
    return result


def configure_component(component_name, config_dir, default):
    """Configure individual pattoo related components and check configuration.

    Args:
        component_name: The file name for the component being configured
        config_dir: The directory with the configuration files
        default: A dictionary containing the default configuration values

    Returns:
        None

    """
    # Initialize key variables
    filepath = os.path.join(config_dir, '{}.yaml'.format(component_name))

    # Create configuration file
    config = _Config(filepath, default)
    config.update()
    config.validate()
