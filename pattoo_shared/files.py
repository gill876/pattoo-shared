#!/usr/bin/env python3
"""Pattoo files library."""

import os
import sys
import json
import yaml

# Pattoo libraries
from pattoo_shared import log


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


def read_json_files(_directory, die=True):
    """Read the contents of all JSON files in a directory.

    Args:
        _directory: Directory with JSON files
        die: Die if there is an error
        tuples:

    Returns:
        result: List of tuples containing JSON read from each file and filepath
            [(filepath, JSON), (filepath, JSON) ...]

    """
    # Initialize key variables
    json_found = False
    result = []

    if os.path.isdir(_directory) is False:
        log_message = 'Directory "{}" doesn\'t exist!'.format(_directory)
        log.log2die(1009, log_message)

    # Cycle through list of files in directory
    for filename in os.listdir(_directory):
        # Examine all the '.json' files in directory
        if filename.endswith('.json'):
            # JSON files found
            json_found = True

            # Read file and add to string
            filepath = '{}{}{}'.format(_directory, os.sep, filename)
            result.append((filepath, read_json_file(filepath, die=die)))

    # Verify JSON files found in directory. We cannot use logging as it
    # requires a logfile location from the configuration directory to work
    # properly
    if (json_found is False) and (bool(die) is True):
        log_message = (
            'No JSON files found in directory "{}" with ".json" '
            'extension.'.format(_directory))
        log.log2die_safe(1102, log_message)

    # Return
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
            log_message = (
                'Error reading file {}. Check permissions, '
                'existence and file syntax.'
                ''.format(filepath))
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
