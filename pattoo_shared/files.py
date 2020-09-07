#!/usr/bin/env python3
"""Pattoo files library."""

import os
import time
import sys
import json
import stat
from random import random
import subprocess

# PIP imports
import yaml

# Pattoo libraries
from pattoo_shared import log
from pattoo_shared import data


class _Directory():
    """A class for creating the names of hidden directories."""

    def __init__(self, config):
        """Initialize the class.

        Args:
            config: Config object

        Returns:
            None

        """
        # Initialize key variables
        self._root = config.daemon_directory()
        self._system_root = config.system_daemon_directory()
        self._cache = config.cache_directory()

    def pid(self):
        """Define the hidden pid directory.

        Args:
            None

        Returns:
            value: pid directory

        """
        # Return
        value = '{}{}pid'.format(self._system_root, os.sep)
        return value

    def lock(self):
        """Define the hidden lock directory.

        Args:
            None

        Returns:
            value: lock directory

        """
        # Return
        value = '{}{}lock'.format(self._system_root, os.sep)
        return value

    def agent_id(self):
        """Define the hidden agent_id directory.

        Args:
            None

        Returns:
            value: agent_id directory

        """
        # Return
        value = '{}{}agent_id'.format(self._root, os.sep)
        return value


class _File():
    """A class for creating the names of hidden files."""

    def __init__(self, config):
        """Initialize the class.

        Args:
            config: Config object

        Returns:
            None

        """
        # Initialize key variables
        self._directory = _Directory(config)

    def pid(self, prefix):
        """Define the hidden pid directory.

        Args:
            prefix: Prefix of file

        Returns:
            value: pid directory

        """
        # Return
        mkdir(self._directory.pid())
        value = '{}{}{}.pid'.format(self._directory.pid(), os.sep, prefix)
        return value

    def lock(self, prefix):
        """Define the hidden lock directory.

        Args:
            prefix: Prefix of file

        Returns:
            value: lock directory

        """
        # Return
        mkdir(self._directory.lock())
        value = '{}{}{}.lock'.format(self._directory.lock(), os.sep, prefix)
        return value

    def agent_id(self, agent_name):
        """Define the hidden agent_id directory.

        Args:
            agent_name: Agent name

        Returns:
            value: agent_id directory

        """
        # Return
        mkdir(self._directory.agent_id())
        value = ('''{}{}{}.agent_id\
'''.format(self._directory.agent_id(), os.sep, agent_name))
        return value


def read_yaml_files(config_directory):
    """Read the contents of all yaml files in a directory.

    Args:
        config_directory: Directory with configuration files

    Returns:
        config_dict: Single dict of combined yaml read from all files

    """
    # Initialize key variables
    yaml_found = False
    yaml_from_file = ''
    all_yaml_read = ''

    if os.path.isdir(config_directory) is False:
        log_message = (
            'Configuration directory "{}" '
            'doesn\'t exist!'.format(config_directory))
        log.log2die_safe(1026, log_message)

    # Cycle through list of files in directory
    for filename in os.listdir(config_directory):
        # Examine all the '.yaml' files in directory
        if filename.endswith('.yaml'):
            # YAML files found
            yaml_found = True

            # Read file and add to string
            filepath = '{}{}{}'.format(config_directory, os.sep, filename)
            yaml_from_file = read_yaml_file(filepath, as_string=True, die=True)

            # Append yaml from file to all yaml previously read
            all_yaml_read = '{}\n{}'.format(all_yaml_read, yaml_from_file)

    # Verify YAML files found in directory. We cannot use logging as it
    # requires a logfile location from the configuration directory to work
    # properly
    if yaml_found is False:
        log_message = (
            'No configuration files found in directory "{}" with ".yaml" '
            'extension.'.format(config_directory))
        log.log2die_safe(1015, log_message)

    # Return
    config_dict = yaml.safe_load(all_yaml_read)
    return config_dict


def read_yaml_file(filepath, as_string=False, die=True):
    """Read the contents of a YAML file.

    Args:
        filepath: Path to file to be read
        as_string: Return a string if True
        die: Die if there is an error

    Returns:
        result: Dict of yaml read

    """
    # Initialize key variables
    if as_string is False:
        result = {}
    else:
        result = ''

    # Read file
    if filepath.endswith('.yaml'):
        try:
            with open(filepath, 'r') as file_handle:
                yaml_from_file = file_handle.read()
        except:
            log_message = (
                'Error reading file {}. Check permissions, '
                'existence and file syntax.'
                ''.format(filepath))
            if bool(die) is True:
                log.log2die_safe(1006, log_message)
            else:
                log.log2debug(1014, log_message)
                return {}

        # Get result
        if as_string is False:
            try:
                result = yaml.safe_load(yaml_from_file)
            except:
                log_message = (
                    'Error reading file {}. Check permissions, '
                    'existence and file syntax.'
                    ''.format(filepath))
                if bool(die) is True:
                    log.log2die_safe(1001, log_message)
                else:
                    log.log2debug(1002, log_message)
                    return {}
        else:
            result = yaml_from_file

    else:
        # Die if not a YAML file
        log_message = '{} is not a YAML file.'.format(filepath)
        if bool(die) is True:
            log.log2die_safe(1065, log_message)
        else:
            log.log2debug(1005, log_message)
            if bool(as_string) is False:
                return {}
            else:
                return ''

    # Return
    return result


def read_json_files(_directory, die=True, age=0, count=None):
    """Read the contents of all JSON files in a directory.

    Args:
        _directory: Directory with JSON files
        die: Die if there is an error
        age: Minimum age of files in seconds
        count: Return first X number of sorted filenames is not None

    Returns:
        result: sorted list of tuples containing JSON read from each file and
            filepath. Sorting is important as it causes the files with the
            older timestamp names to be processed first. This allows the
            last_timestamp column to be incrementally processed versus some
            unexpected order. [(filepath, JSON), (filepath, JSON) ...]

    """
    # Initialize key variables
    json_found = False
    result = []
    processed = 0

    # Set age
    try:
        age = float(age)
    except:
        age = 0

    # Verify directory
    if os.path.isdir(_directory) is False:
        log_message = 'Directory "{}" doesn\'t exist!'.format(_directory)
        log.log2die(1009, log_message)

    # Cycle through list of files in directory
    for filename in sorted(os.listdir(_directory)):
        # Examine all the '.json' files in directory
        if filename.endswith('.json'):
            # Read file and add to tuple list
            filepath = '{}{}{}'.format(_directory, os.sep, filename)
            fileage = time.time() - os.stat(filepath).st_mtime
            if fileage > age:
                _data = read_json_file(filepath, die=die)
                if bool(_data) is True:
                    # JSON files found
                    json_found = True
                    result.append((filepath, _data))
                else:
                    # Ignore, don't update 'processed' value
                    log_message = ('''\
Error reading file {}. Ignoring.'''.format(filepath))
                    log.log2debug(1053, log_message)
                    continue

            # Stop if necessary
            processed += 1
            if bool(count) is True:
                if processed == count:
                    break

    # Verify JSON files found in directory. We cannot use logging as it
    # requires a logfile location from the configuration directory to work
    # properly
    if (json_found is False) and (bool(die) is True):
        log_message = (
            'No valid JSON files found in directory "{}" with ".json" '
            'extension.'.format(_directory))
        log.log2die_safe(1060, log_message)

    # Return
    result.sort()
    return result


def read_json_file(filepath, die=True):
    """Read the contents of a YAML file.

    Args:
        filepath: Path to file to be read
        die: Die if there is an error

    Returns:
        result: Dict of JSON read

    """
    # Read file
    if filepath.endswith('.json'):
        try:
            with open(filepath, 'r') as file_handle:
                result = json.load(file_handle)
        except:
            log_message = ('''\
Error reading file {}. Check permissions, existence and file syntax.\
'''.format(filepath))
            if bool(die) is True:
                log.log2die_safe(1012, log_message)
            else:
                log.log2debug(1013, log_message)
                return {}

    else:
        # Die if not a JSON file
        log_message = '{} is not a JSON file.'.format(filepath)
        if bool(die) is True:
            log.log2die_safe(1010, log_message)
        else:
            log.log2debug(1011, log_message)
            return {}

    # Return
    return result


def mkdir(directory):
    """Create a directory if it doesn't already exist.

    Args:
        directory: Directory name

    Returns:
        None

    """
    # Do work
    if os.path.exists(directory) is False:
        try:
            os.makedirs(directory, mode=0o775)
        except:
            log_message = (
                'Cannot create directory {}.'
                ''.format(directory))
            log.log2die(1090, log_message)

    # Fail if not a directory
    if os.path.isdir(directory) is False:
        log_message = (
            '{} is not a directory.'
            ''.format(directory))
        log.log2die(1043, log_message)


def pid_file(agent_name, config):
    """Get the pidfile for an agent.

    Args:
        agent_name: Agent name
        config: Config object

    Returns:
        result: Name of pid file

    """
    # Return
    f_obj = _File(config)
    result = f_obj.pid(agent_name)
    return result


def lock_file(agent_name, config):
    """Get the lockfile for an agent.

    Args:
        agent_name: Agent name
        config: Config object

    Returns:
        result: Name of lock file

    """
    # Return
    f_obj = _File(config)
    result = f_obj.lock(agent_name)
    return result


def agent_id_file(agent_name, config):
    """Get the agent_idfile for an agent.

    Args:
        agent_name: Agent name
        config: Config object


    Returns:
        result: Name of agent_id file

    """
    # Return
    f_obj = _File(config)
    result = f_obj.agent_id(agent_name)
    return result


def get_agent_id(agent_name, config):
    """Create a permanent UID for the agent_name.

    Args:
        agent_name: Agent name
        config: Config object

    Returns:
        agent_id: UID for agent

    """
    # Initialize key variables
    filename = agent_id_file(agent_name, config)

    # Read environment file with UID if it exists
    if os.path.isfile(filename):
        with open(filename) as f_handle:
            agent_id = f_handle.readline()
    else:
        # Create a UID and save
        agent_id = _generate_agent_id()
        with open(filename, 'w+') as env:
            env.write(str(agent_id))

    # Return
    return agent_id


def execute(command, die=True):
    """Run the command UNIX CLI command and record output.

    Args:
        command: CLI command to execute
        die: Die if errors found

    Returns:
        returncode: Return code of command execution

    """
    # Initialize key variables
    messages = []
    stdoutdata = ''.encode()
    stderrdata = ''.encode()
    returncode = 1

    # Run update_targets script
    do_command_list = list(command.split(' '))

    # Create the subprocess object
    try:
        process = subprocess.Popen(
            do_command_list,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdoutdata, stderrdata = process.communicate()
        returncode = process.returncode
    except:
        (etype, evalue, etraceback) = sys.exc_info()
        log_message = ('''\
Command failure: [Exception:{}, Exception Instance: {}, Stack Trace: {}]\
'''.format(etype, evalue, etraceback))
        log.log2warning(1052, log_message)

    # Crash if the return code is not 0
    if returncode != 0:
        # Print the Return Code header
        messages.append(
            'Return code:{}'.format(returncode)
        )

        # Print the STDOUT
        for line in stdoutdata.decode().split('\n'):
            messages.append(
                'STDOUT: {}'.format(line)
            )

        # Print the STDERR
        for line in stderrdata.decode().split('\n'):
            messages.append(
                'STDERR: {}'.format(line)
            )

        # Log message
        for log_message in messages:
            log.log2warning(1042, log_message)

        # Die if required after error found
        if bool(die) is True:
            log.log2die(1044, 'Command Failed: {}'.format(command))

    # Return
    return returncode


def _generate_agent_id():
    """Generate a UID.

    Args:
        None

    Returns:
        agent_id: the UID

    """
    # Create a UID and save
    prehash = '{}{}{}{}{}'.format(
        random(), random(), random(), random(), time.time())
    agent_id = data.hashstring(prehash)

    # Return
    return agent_id
