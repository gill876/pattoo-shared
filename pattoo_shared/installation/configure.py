"""Methods for configuring pattoo components"""
# Standard imports
import os
import grp
import pwd

# Dependendices
import yaml

# Import project libraries
from pattoo_shared import files, configuration, log
import shared


class Configure():
    """Class that configures pattoo components."""

    def __init__(self):
        """Initialize the class.

        Args:
            None

        Returns:
            None

        """
        self.default_config = {
            'pattoo': {
                'language': 'en',
                'log_directory': (
                    '/var/log/pattoo'),
                'log_level': 'debug',
                'cache_directory': (
                    '/opt/pattoo-cache'),
                'daemon_directory': (
                    '/opt/pattoo-daemon'),
                'system_daemon_directory': '/var/run/pattoo'
            },
            'pattoo_agent_api': {
                'ip_address': '127.0.0.1',
                'ip_bind_port': 20201
            },
            'pattoo_web_api': {
                'ip_address': '127.0.0.1',
                'ip_bind_port': 20202,
            }
        }

    def create_user(self, user_name, directory, shell, verbose):
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
        # If the group specified does not exist, it gets created
        if not self.group_exists(user_name):
            shared.run_script('groupadd {0}'.format(user_name), verbose)
        # If the user specified does not exist, they get created
        if not self.user_exists(user_name):
            shared.run_script(
                'useradd -d {1} -s {2} -g {0} {0}'.format(
                    user_name, directory, shell), verbose)

    def group_exists(self, group_name):
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

    def user_exists(self, user_name):
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

    def initialize_ownership(self, user, group,  dir_path, verbose):
        """Recursively change the ownership of the directory.

        Args:
            user: The name of the user
            group: The name of the group
            dir_name: The name of the directory
            verbose: A boolean value that a allows the script to run in verbose
            mode

        Returns:
            None
        """
        # Set ownership of file specified at dir_path
        shared.run_script(
            'chown -R {0}:{1} {2}'.format(user, group, dir_path), verbose)

    def pattoo_config(self, config_directory, config_dict=None):
        """Create pattoo.yaml file.

        Args:
            config_directory: Configuration directory
            config_dict: A dictionary containing the configuration values
            by default its value is set to None.

        Returns:
            None

        """
        # Initialize key variables
        filepath = '{}{}pattoo.yaml'.format(config_directory, os.sep)
        config_obj = configuration.Config()

        # Set config_dict if None has been passed in
        if config_dict is None:
            pattoo_config = self.default_config

        # Say what we are doing
        print('\nConfiguring {} file.\n'.format(filepath))

        # Get configuration
        config = self.read_config(filepath, pattoo_config)

        # Check validity of directories
        for key, value in sorted(config['pattoo'].items()):
            if 'directory' in key:
                if os.sep not in value:
                    log.log2die_safe(
                        51010, '{} is an invalid directory'.format(value))

                # Attempt to create directory
                full_directory = os.path.expanduser(value)
                if os.path.isdir(full_directory) is False:
                    files.mkdir(full_directory)

                    # Recursively set file ownership to pattoo user and group
                    config_obj.initialize_ownership(
                            'pattoo', 'pattoo', full_directory)

        # Write file
        with open(filepath, 'w') as f_handle:
            yaml.dump(config, f_handle, default_flow_style=False)

    def read_config(self, filepath, default_config):
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

    def secondary_key_check(self, config, primary, secondaries):
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
                log.log2die_safe(51009, log_message)

    def check_config(self):
        """Ensure agent configuration exists.

        Args:
            None

        Returns:
            None

        """
        # Initialize key variables
        config_directory = os.environ['PATTOO_CONFIGDIR']

        # Print Status
        print('??: Checking configuration parameters.')

        # Check config
        config_file = configuration.agent_config_filename('pattoo')
        config = files.read_yaml_file(config_file)

        # Check main keys
        keys = ['pattoo', 'pattoo_agent_api']
        for key in keys:
            if key not in config:
                log_message = ('''\
Section "{}" not found in configuration file {} in directory {}. Please fix.\
    '''.format(key, config_file, config_directory))
                log.log2die_safe(51008, log_message)

        # Check secondary keys
        secondaries = [
            'log_level', 'log_directory', 'cache_directory',
            'daemon_directory']
        self.secondary_key_check(config, 'pattoo', secondaries)
        secondaries = ['ip_address', 'ip_bind_port']
        self.secondary_key_check(config, 'pattoo_agent_api', secondaries)

        # Print Status
        print('OK: Configuration parameter check passed.')
