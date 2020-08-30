#!/usr/bin/env python3
"""Pattoo classes that manage various configurations."""

# Standard imports
import os
import stat

# Import project libraries
from pattoo_shared import files
from pattoo_shared import log
from pattoo_shared import url
from pattoo_shared.constants import (
    PATTOO_API_AGENT_PREFIX)
from pattoo_shared.variables import PollingPoint


def _config_reader(filename):
    """Read a configuration file.

    Args:
        filename: Name of file to read

    Returns:
        config_dict: Dict representation of YAML in the file

    """
    # Get the configuration directory
    # Expand linux ~ notation for home directories if provided.
    _config_directory = log.check_environment()
    config_directory = os.path.expanduser(_config_directory)
    config_file = '{}{}{}'.format(config_directory, os.sep, filename)
    config_dict = files.read_yaml_file(config_file)
    return config_dict


class BaseConfig():
    """Class gathers all configuration information."""

    def __init__(self):
        """Initialize the class.

        Args:
            None

        Returns:
            None

        """
        # Read data
        self._base_yaml_configuration = _config_reader('pattoo.yaml')

    def config_directory(self):
        """Get config_directory.

        Args:
            None

        Returns:
            result: result

        """
        # Return
        result = log.check_environment()
        return result

    def log_directory(self):
        """Get log_directory.

        Args:
            None

        Returns:
            result: result

        """
        # Get result
        sub_key = 'log_directory'
        result = None
        key = 'pattoo'

        # Get new result
        _result = search(key, sub_key, self._base_yaml_configuration)

        # Expand linux ~ notation for home directories if provided.
        result = os.path.expanduser(_result)

        # Check if value exists. We cannot use log2die_safe as it does not
        # require a log directory location to work properly
        if os.path.isdir(result) is False:
            log_message = (
                'log_directory: "{}" '
                'in configuration doesn\'t exist!'.format(result))
            log.log2die_safe(1003, log_message)

        # Return
        return result

    def log_file(self):
        """Get log_file.

        Args:
            None

        Returns:
            result: result

        """
        _log_directory = self.log_directory()
        result = '{}{}pattoo.log'.format(_log_directory, os.sep)
        return result

    def log_file_api(self):
        """Get log_file_api.

        Args:
            None

        Returns:
            result: result

        """
        # Get result
        _log_directory = self.log_directory()
        result = '{}{}pattoo-api.log'.format(_log_directory, os.sep)
        return result

    def log_file_daemon(self):
        """Get log_file_daemon.

        Args:
            None

        Returns:
            result: result

        """
        # Get result
        _log_directory = self.log_directory()
        result = '{}{}pattoo-daemon.log'.format(_log_directory, os.sep)
        return result

    def log_level(self):
        """Get log_level.

        Args:
            None

        Returns:
            result: result

        """
        # Get result
        sub_key = 'log_level'
        key = 'pattoo'
        result = None

        # Return
        intermediate = search(
            key, sub_key, self._base_yaml_configuration, die=False)
        if intermediate is None:
            result = 'debug'
        else:
            result = '{}'.format(intermediate).lower()
        return result

    def cache_directory(self):
        """Determine the cache_directory.

        Args:
            None

        Returns:
            value: configured cache_directory

        """
        # Initialize key variables
        key = 'pattoo'
        sub_key = 'cache_directory'

        # Get result
        _value = search(key, sub_key, self._base_yaml_configuration)

        # Expand linux ~ notation for home directories if provided.
        value = os.path.expanduser(_value)

        # Create directory if it doesn't exist
        files.mkdir(value)

        # Return
        return value

    def agent_cache_directory(self, agent_program):
        """Get agent_cache_directory.

        Args:
            agent_program: Name of agent

        Returns:
            result: result

        """
        # Get result
        result = '{}/{}'.format(self.cache_directory(), agent_program)

        # Create directory if it doesn't exist
        files.mkdir(result)

        # Return
        return result

    def daemon_directory(self):
        """Determine the daemon_directory.

        Args:
            None

        Returns:
            value: configured daemon_directory

        """
        # Initialize key variables
        key = 'pattoo'
        sub_key = 'daemon_directory'

        # Get result
        _value = search(key, sub_key, self._base_yaml_configuration)

        # Expand linux ~ notation for home directories if provided.
        value = os.path.expanduser(_value)

        # Create directory if it doesn't exist
        files.mkdir(value)

        # Return
        return value

    def keyring_directory(self, agent_name):
        """Get keyring_directory.

        Args:
            agent_name: Name of agent

        Returns:
            result: result

        """
        # Get result
        result = '{0}{1}.keyring'.format(
            self.keys_directory(agent_name), os.sep)

        # Create directory if it doesn't exist
        files.mkdir(result)

        # Make only accessible to the user
        os.chmod(result, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        # Return
        return result

    def keys_directory(self, agent_name):
        """Get keys_directory.

        Args:
            agent_name: Name of agent

        Returns:
            result: result

        """
        # Get result
        result = '{0}{1}keys{1}{2}'.format(
            self.daemon_directory(), os.sep, agent_name)

        # Create directory if it doesn't exist
        files.mkdir(result)

        # Make only accessible to the user
        os.chmod(result, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        # Return
        return result

    def system_daemon_directory(self):
        """Determine the system_daemon_directory.

        Args:
            None

        Returns:
            value: configured system_daemon_directory

        """
        # Initialize key variables
        key = 'pattoo'
        sub_key = 'system_daemon_directory'

        # Get result
        result = search(key, sub_key, self._base_yaml_configuration, die=False)
        _value = result if bool(result) else self.daemon_directory()

        # Expand linux ~ notation for home directories if provided.
        value = os.path.expanduser(_value)

        # Create directory if it doesn't exist
        files.mkdir(value)

        # Return
        return value

    def language(self):
        """Get language.

        Args:
            None

        Returns:
            result: result

        """
        # Get result
        key = 'pattoo'
        sub_key = 'language'
        intermediate = search(
            key, sub_key, self._base_yaml_configuration, die=False)

        # Default to 'en'
        if bool(intermediate) is False:
            result = 'en'
        else:
            result = str(intermediate).lower()
        return result


class ServerConfig(BaseConfig):
    """Class gathers all configuration information."""

    def __init__(self):
        """Initialize the class.

        Args:
            None

        Returns:
            None

        """
        # Get the configuration
        BaseConfig.__init__(self)
        self._server_yaml_configuration = _config_reader('pattoo_server.yaml')


class Config(BaseConfig):
    """Class gathers all configuration information."""

    def __init__(self):
        """Initialize the class.

        Args:
            None

        Returns:
            None

        """
        # Get the configuration
        BaseConfig.__init__(self)

        self._agent_yaml_configuration = _config_reader('pattoo_agent.yaml')

    def agent_api_ip_address(self):
        """Get api_ip_address.

        Args:
            None

        Returns:
            result: result

        """
        # Initialize key variables
        key = 'pattoo_agent_api'
        sub_key = 'ip_address'

        # Get result
        result = search(
            key, sub_key, self._agent_yaml_configuration, die=False)
        if result is None:
            result = 'localhost'
        return result

    def agent_api_ip_bind_port(self):
        """Get agent_api_ip_bind_port.

        Args:
            None

        Returns:
            result: result

        """
        # Initialize key variables
        key = 'pattoo_agent_api'
        sub_key = 'ip_bind_port'

        # Get result
        intermediate = search(
            key, sub_key, self._agent_yaml_configuration, die=False)
        if intermediate is None:
            result = 20201
        else:
            result = int(intermediate)
        return result

    def agent_api_uri(self):
        """Get agent_api_uri.

        Args:
            None

        Returns:
            result: result

        """
        # Return
        result = '{}/receive'.format(PATTOO_API_AGENT_PREFIX)
        return result

    def agent_api_key(self):
        """Get URL for key exchange.

        Args:
            None

        Returns:
            url (str): URL of the key exchange point
        """
        url_ = '{}/key'.format(PATTOO_API_AGENT_PREFIX)
        return url_

    def agent_api_validation(self):
        """Get URL to validate encryption status.

        Args:
            None

        Returns:
            url (str): URL of the validation point
        """
        url_ = '{}/validation'.format(PATTOO_API_AGENT_PREFIX)
        return url_

    def agent_api_encrypted(self):
        """Get URL to receive encrypted data.

        Args:
            None

        Returns:
            result: result

        """
        # Return
        result = '{}/encrypted'.format(PATTOO_API_AGENT_PREFIX)
        return result

    def agent_api_server_url(self, agent_id):
        """Get pattoo server's remote URL.

        Args:
            agent_id: Agent ID

        Returns:
            result: URL.

        """
        # Return
        _ip = url.url_ip_address(self.agent_api_ip_address())
        result = (
            'http://{}:{}{}/{}'.format(
                _ip,
                self.agent_api_ip_bind_port(),
                self.agent_api_uri(), agent_id))
        return result

    def agent_api_key_url(self):
        """Exchange point for public keys.

        Args:
            None

        Returns:
            link (str): Link of the key exchange point

        """
        # Initialize key variables
        _ip = url.url_ip_address(self.agent_api_ip_address())
        link = (
            'http://{}:{}{}'.format(
                _ip,
                self.agent_api_ip_bind_port(),
                self.agent_api_key()
                )
            )

        return link

    def agent_api_validation_url(self):
        """Validation point for encryption.

        Args:
            None

        Returns:
            link (str): Link of the validation point

        """

        _ip = url.url_ip_address(self.agent_api_ip_address())
        link = (
            'http://{}:{}{}'.format(
                _ip,
                self.agent_api_ip_bind_port(),
                self.agent_api_validation()
                )
            )

        return link

    def agent_api_encrypted_url(self):
        """Encrypted data reception point.

        Args:
            None

        Returns:
            link (str): Link of encrypted data receive point

        """

        _ip = url.url_ip_address(self.agent_api_ip_address())
        link = (
            'http://{}:{}{}'.format(
                _ip,
                self.agent_api_ip_bind_port(),
                self.agent_api_encrypted()
                )
            )

        return link


def agent_config_filename(agent_program):
    """Get the configuration file name.

    Args:
        agent_program: Agent program name

    Returns:
        result: Name of file

    """
    # Get the configuration directory
    # Expand linux ~ notation for home directories if provided.
    _config_directory = log.check_environment()
    config_directory = os.path.expanduser(_config_directory)
    result = '{}{}{}.yaml'.format(config_directory, os.sep, agent_program)
    return result


def get_polling_points(_data):
    """Create list of PollingPoint objects.

    Args:
        _data: List of dicts with 'address' and 'multiplier' as keys

    Returns:
        results: List of PollingPoint objects

    """
    # Start conversion
    results = []

    if isinstance(_data, list) is True:
        # Cycle through list
        for item in _data:
            # Reject non dict data
            if isinstance(item, dict) is False:
                continue

            # Assign address value only if present
            if 'address' in item:
                address = item['address']
            else:
                continue

            # Assign replacement multiplier
            multiplier = item.get('multiplier', 1)

            # Populate result
            result = PollingPoint(address=address, multiplier=multiplier)
            results.append(result)

    # Return
    return results


def search(key, sub_key, config_dict, die=True):
    """Get config parameter from YAML.

    Args:
        key: Primary key
        sub_key: Secondary key
        config_dict: Dictionary to explore
        die: Die if true and the result encountered is None

    Returns:
        result: result

    """
    # Get result
    result = None

    # Verify config_dict is indeed a dict.
    # Die safely as log_directory is not defined
    if isinstance(config_dict, dict) is False:
        log.log2die_safe(1021, 'Invalid configuration file. YAML not found')

    # Get new result
    if config_dict.get(key) is not None:
        # Make sure we don't have a None value
        if config_dict[key] is None:
            log_message = (
                '{}: value in configuration is blank. Please fix'.format(key))
            log.log2die_safe(1004, log_message)

        # Get value we need
        result = config_dict[key].get(sub_key)

    # Error if not configured
    if result is None and die is True:
        log_message = (
            '{}:{} not defined in configuration dict {}'.format(
                                                    key, sub_key, config_dict))
        log.log2die_safe(1016, log_message)

    # Return
    return result
