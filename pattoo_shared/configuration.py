#!/usr/bin/env python3
"""Pattoo classes that manage various configurations."""

# Standard imports
import os

# Import project libraries
from pattoo_shared import files
from pattoo_shared import log
from pattoo_shared import url
from pattoo_shared.constants import (
    PATTOO_API_AGENT_PREFIX, PATTOO_API_WEB_PREFIX)
from pattoo_shared.variables import PollingPoint


class _Config(object):
    """Class gathers all configuration information.

    Only processes the following YAML keys in the configuration file:

        main:
        remote_api:

    """

    def __init__(self, filename):
        """Initialize the class.

        Args:
            filename: Name of file to read

        Returns:
            None

        """
        # Get the configuration directory
        # Expand linux ~ notation for home directories if provided.
        _config_directory = log.check_environment()
        config_directory = os.path.expanduser(_config_directory)
        config_file = '{}{}{}'.format(config_directory, os.sep, filename)
        self._pattoo_yaml_configuration = files.read_yaml_file(config_file)

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
        _result = search(key, sub_key, self._pattoo_yaml_configuration)

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
            key, sub_key, self._pattoo_yaml_configuration, die=False)
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
        _value = search(key, sub_key, self._pattoo_yaml_configuration)

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
        _value = search(key, sub_key, self._pattoo_yaml_configuration)

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
            key, sub_key, self._pattoo_yaml_configuration, die=False)

        # Default to 'en'
        if bool(intermediate) is False:
            result = 'en'
        else:
            result = str(intermediate).lower()
        return result


class Config(_Config):
    """Class gathers all configuration information."""

    def __init__(self):
        """Initialize the class.

        Args:
            None

        Returns:
            None

        """
        # Get the configuration
        _Config.__init__(self, 'pattoo.yaml')

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
            key, sub_key, self._pattoo_yaml_configuration, die=False)
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
            key, sub_key, self._pattoo_yaml_configuration, die=False)
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

    def web_api_ip_address(self):
        """Get web_api_ip_address.

        Args:
            None

        Returns:
            result: result

        """
        # Initialize key variables
        key = 'pattoo_web_api'
        sub_key = 'ip_address'

        # Get result
        result = search(
            key, sub_key, self._pattoo_yaml_configuration, die=True)
        return result

    def web_api_ip_bind_port(self):
        """Get web_api_ip_bind_port.

        Args:
            None

        Returns:
            result: result

        """
        # Initialize key variables
        key = 'pattoo_web_api'
        sub_key = 'ip_bind_port'

        # Get result
        intermediate = search(
            key, sub_key, self._pattoo_yaml_configuration, die=False)
        if intermediate is None:
            result = 20202
        else:
            result = int(intermediate)
        return result

    def web_api_server_url(self, graphql=True):
        """Get pattoo server's remote URL.

        Args:
            agent_id: Agent ID

        Returns:
            result: URL.

        """
        # Create the suffix
        if bool(graphql) is True:
            suffix = '/graphql'
        else:
            suffix = '/rest/data'

        # Return
        _ip = url.url_ip_address(self.web_api_ip_address())
        result = (
            'http://{}:{}{}{}'.format(
                _ip,
                self.web_api_ip_bind_port(),
                PATTOO_API_WEB_PREFIX, suffix))
        return result


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
            # Default multiplier
            multiplier = 1

            # Reject non dict data
            if isinstance(item, dict) is False:
                continue

            # Assign address value only if present
            if 'address' in item:
                address = item['address']
            else:
                continue

            # Assign replacement multiplier
            if 'multiplier' in item:
                multiplier = item['multiplier']

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
    if key in config_dict:
        # Make sure we don't have a None value
        if config_dict[key] is None:
            log_message = (
                '{}: value in configuration is blank. Please fix'.format(key))
            log.log2die_safe(1004, log_message)

        # Get value we need
        if sub_key in config_dict[key]:
            result = config_dict[key][sub_key]

    # Error if not configured
    if result is None and die is True:
        log_message = (
            '{}:{} not defined in configuration'.format(key, sub_key))
        log.log2die_safe(1016, log_message)

    # Return
    return result
