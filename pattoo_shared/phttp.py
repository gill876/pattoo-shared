#!/usr/bin/env python3
"""Pattoo HTTP data classes."""

# Standard libraries
import os
import sys
import json
import urllib
from time import time

# pip3 libraries
import requests

# Pattoo libraries
from pattoo_shared import log
from pattoo_shared.configuration import Config
from pattoo_shared import converter


class Post(object):
    """Class to prepare data for posting to remote pattoo server."""

    def __init__(self, identifier, identifier_data=None):
        """Initialize the class.

        Args:
            identifier: Unique identifer for the source of the data.
            identifier_data: Data from the data source to post

        Returns:
            None

        """
        # Initialize key variables
        config = Config()

        # Test validity
        if isinstance(identifier, str) is False:
            log_message = ('''\
Data identifier isn\'t a string. Identifier: {}'''.format(identifier))
            log.log2die(1018, log_message)

        # Get posting URL
        self._identifier = identifier
        self._url = config.api_server_url(identifier)
        self._cache_dir = config.agent_cache_directory(identifier)
        self._identifier_data = identifier_data

    def post(self, save=True, data=None):
        """Post data to central server.

        Args:
            save: When True, save data to cache directory if postinf fails
            data: Data to post. If None, then uses self._post_data (
                Used for testing and cache purging)

        Returns:
            success: True: if successful

        """
        # Initialize key variables
        success = False
        response = False
        valid_data = False

        # Create data to post
        if bool(data) is True:
            valid_data = data
        else:
            valid_data = converter.datapoints_to_dicts(self._identifier_data)

        # Fail if nothing to post
        if isinstance(valid_data, list) is False or bool(valid_data) is False:
            return success

        # Post data save to cache if this fails
        try:
            result = requests.post(self._url, json=valid_data)
            response = True
        except:
            if save is True:
                # Save data to cache
                self._save(valid_data)
            else:
                # Proceed normally if there is a failure.
                # This will be logged later
                pass

        # Define success
        if response is True:
            if result.status_code == 200:
                success = True
            else:
                log_message = (
                    'HTTP {} error for identifier "{}" posted to server {}'
                    ''.format(result.status_code, self._identifier, self._url))
                log.log2debug(1017, log_message)
                # Save data to cache, remote webserver isn't working properly
                self._save(valid_data)

        # Log message
        if success is True:
            log_message = (
                'Data for identifier "{}" posted to server {}'
                ''.format(self._identifier, self._url))
            log.log2debug(1027, log_message)
        else:
            log_message = (
                'Data for identifier "{}" failed to post to server {}'
                ''.format(self._identifier, self._url))
            log.log2warning(1028, log_message)

        # Return
        return success

    def purge(self):
        """Purge data from cache by posting to central server.

        Args:
            None

        Returns:
            success: "True: if successful

        """
        # Initialize key variables
        identifier = self._identifier

        # Add files in cache directory to list only if they match the
        # cache suffix
        all_filenames = [filename for filename in os.listdir(
            self._cache_dir) if os.path.isfile(
                os.path.join(self._cache_dir, filename))]
        filenames = [
            filename for filename in all_filenames if filename.endswith(
                '.json')]

        # Read cache file
        for filename in filenames:
            # Only post files for our own UID value
            if identifier not in filename:
                continue

            # Get the full filepath for the cache file and post
            filepath = os.path.join(self._cache_dir, filename)
            with open(filepath, 'r') as f_handle:
                try:
                    data = json.load(f_handle)
                except:
                    # Log removal
                    log_message = (
                        'Error reading previously cached agent data file {} '
                        'for identifier {}. May be corrupted.'
                        ''.format(filepath, self._identifier))
                    log.log2die(1064, log_message)

            # Post file
            success = self.post(save=False, data=data)

            # Delete file if successful
            if success is True:
                os.remove(filepath)

                # Log removal
                log_message = (
                    'Purging cache file {} after successfully '
                    'contacting server {}'
                    ''.format(filepath, self._url))
                log.log2info(1007, log_message)

    def _save(self, data):
        """Save data to cache file.

        Args:
            cache_dir: Cache directory
            identifier: Identifier
            data: Dict to save

        Returns:
            success: True: if successful

        """
        # Initialize key variables
        cache_dir = self._cache_dir
        identifier = self._identifier
        timestamp = int(time() * 1000)

        # Create a unique very long filename to reduce risk of
        filename = '{}/{}_{}.json'.format(cache_dir, timestamp, identifier)

        # Save data
        with open(filename, 'w') as f_handle:
            json.dump(data, f_handle)


class PostAgent(Post):
    """Class to prepare data for posting to remote pattoo server."""

    def __init__(self, agentdata):
        """Initialize the class.

        Args:
            identifier: Unique identifer for the source of the data.
            identifier_data: Data from the data source to post

        Returns:
            None

        """
        # Get extracted data
        data = converter.agentdata_to_datapoints(agentdata)

        # Initialize key variables
        Post.__init__(
            self, agentdata.agent_id, identifier_data=data)


class PassiveAgent(object):
    """Class to handle data from passive Pattoo Agents."""

    def __init__(self, identifier, url):
        """Initialize the class.

        Args:
            url: URL to get
            identifer: Unique identifier to use for posting data

        Returns:
            None

        """
        # Initialize key variables
        self._url = url
        self._identifier = identifier

    def relay(self):
        """Forward data polled from remote pattoo passive agent.

        Args:
            None

        Returns:
            None

        """
        # Get data
        data_dict = self.get()

        # Post data
        if bool(data_dict) is True:
            # Post to remote server
            server = Post(self._identifier)
            success = server.post(data=data_dict)

            # Purge cache if success is True
            if success is True:
                server.purge()

    def get(self):
        """Get JSON from remote URL.

        Args:
            None

        Returns:
            result: dict of JSON retrieved.

        """
        # Initialize key variables
        result = {}
        url = self._url

        # Get URL
        try:
            with urllib.request.urlopen(url) as u_handle:
                try:
                    result = json.loads(u_handle.read().decode())
                except:
                    error = sys.exc_info()[:2]
                    log_message = (
                        'Error reading JSON from URL {}: ({} {})'
                        ''.format(url, error[0], error[1]))
                    log.log2info(1008, log_message)
        except:
            # Most likely no connectivity or the TCP port is unavailable
            error = sys.exc_info()[:2]
            log_message = (
                'Error contacting URL {}: ({} {})'
                ''.format(url, error[0], error[1]))
            log.log2info(1186, log_message)

        # Return
        return result
