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


class Post():
    """Class to prepare data for posting to remote pattoo server."""

    def __init__(self, identifier, data):
        """Initialize the class.

        Args:
            identifier: Agent identifier
            data: Data from agent

        Returns:
            None

        """
        # Initialize key variables
        config = Config()

        # Get posting URL
        self._data = data
        self._identifier = identifier
        self._url = config.agent_api_server_url(identifier)

        # Get URLs for encryption
        self._exchange_key = config.agent_api_key_url
        self._validate_key = config.agent_api_validation_url

        # Get requirements for key exchange
        self._session = requests.Session()

        # Encryption requirements
        self._symmetric_key = None

    def post(self):
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

        # Post data
        if bool(self._data) is True:
            success = post(self._url, self._data, self._identifier)
        else:
            log_message = ('''\
Blank data. No data to post from identifier {}.'''.format(self._identifier))
            log.log2warning(1018, log_message)

        return success

    def purge(self):
        """Purge data from cache by posting to central server.

        Args:
            None

        Returns:
            success: "True: if successful

        """
        # Initialize key variables
        purge(self._url, self._identifier)

    def set_encryption(self, gpg):
        """ Set up encryption by exchanging public keys and
        setting a symmetric key for encryption

        Args:
            gpg (obj): Pgpier object to facilitate encryption

        Returns:
            (bool): True if the exchange was successful
                    False if the exchange failed
        """

        # Generate symmetric key
        self._symmetric_key = gpg.gen_symm_key(20)  # Random str of len 20
        result = key_exchange(gpg, self._session, self._exchange_key,
                              self._validate_key, self._symmetric_key)

        return result


class PostAgent(Post):
    """Class to prepare data for posting to remote pattoo server."""

    def __init__(self, agentdata):
        """Initialize the class.

        Args:
            agentdata: Agent data

        Returns:
            None

        """
        # Get extracted data
        identifier = agentdata.agent_id
        _data = converter.agentdata_to_post(agentdata)
        data = converter.posting_data_points(_data)

        # Log message that ties the identifier to an agent_program
        _log(agentdata.agent_program, identifier)

        # Don't post if agent data is invalid
        if agentdata.valid is False:
            data = None

        # Initialize key variables
        Post.__init__(self, identifier, data)


class PassiveAgent():
    """Class to handle data from passive Pattoo Agents."""

    def __init__(self, agent_program, identifier, url):
        """Initialize the class.

        Args:
            url: URL to get
            identifier: Unique identifier to use for posting data

        Returns:
            None

        """
        # Initialize key variables
        self._url = url
        self._identifier = identifier
        self._agent_program = agent_program

    def relay(self):
        """Forward data polled from remote pattoo passive agent.

        Args:
            None

        Returns:
            None

        """
        # Get data
        data = self.get()
        identifier = self._identifier

        # Post data
        if bool(data) is True:
            # Log message that ties the identifier to an agent_program
            _log(self._agent_program, identifier)

            # Post to remote server
            server = Post(identifier, data)
            success = server.post()

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
                    (etype, evalue, etraceback) = sys.exc_info()
                    log_message = (
                        'Error reading JSON from URL {}: [{}, {}, {}]'
                        ''.format(url, etype, evalue, etraceback))
                    log.log2info(1008, log_message)
        except:
            # Most likely no connectivity or the TCP port is unavailable
            (etype, evalue, etraceback) = sys.exc_info()
            log_message = (
                'Error contacting URL {}: [{}, {}, {}]'
                ''.format(url, etype, evalue, etraceback))
            log.log2info(1186, log_message)

        # Return
        return result


def post(url, data, identifier, save=True):
    """Post data to central server.

    Args:
        url: URL to receive posted data
        identifier: Identifier to use for posting
        data: Data to post. If None, then uses self._post_data (
            Used for testing and cache purging)
        save: When True, save data to cache directory if posting fails

    Returns:
        success: True: if successful

    """
    # Initialize key variables
    success = False
    response = False

    # Fail if nothing to post
    if isinstance(data, dict) is False or bool(data) is False:
        return success

    # Post data save to cache if this fails
    try:
        result = requests.post(url, json=data)
        response = True
    except:
        if save is True:
            # Save data to cache
            _save_data(data, identifier)
        else:
            # Proceed normally if there is a failure.
            # This will be logged later
            pass

    # Define success
    if response is True:
        if result.status_code == 200:
            success = True
        else:
            log_message = ('''\
HTTP {} error for identifier "{}" posted to server {}\
'''.format(result.status_code, identifier, url))
            log.log2warning(1017, log_message)
            # Save data to cache, remote webserver isn't 
            # working properly
            _save_data(data, identifier)

    # Log message
    if success is True:
        log_message = ('''\
Data for identifier "{}" posted to server {}\
'''.format(identifier, url))
        log.log2debug(1027, log_message)
    else:
        log_message = ('''\
Data for identifier "{}" failed to post to server {}\
'''.format(identifier, url))
        log.log2warning(1028, log_message)

    # Return
    return success


def key_exchange(gpg, req_session, exchange_url, validation_url,
                 symmetric_key):
    """Exchange point for API and Agent public keys

    Args:
        gpg (obj): Pgpier object
        req_session (obj): Request Session object

    Returns:
        True: If key exchange was successful
        False: If the key exchange failed
    """

    # Predefine failure response
    general_response = 409
    general_result = False

    # Set Pgpier key ID
    gpg.set_keyid()

    # Export public key to ASCII to send over
    public_key = gpg.exp_pub_key()

    # Retrieve email address from Pgpier object
    gpg.set_email()
    email_addr = gpg.email_addr

    # Data for POST
    send_data = {'pattoo_agent_email': email_addr,
                 'pattoo_agent_key': public_key}

    try:
        # Send over data
        xch_resp = req_session.post(exchange_url, json=send_data)

        # Checks that sent data was accepted
        general_response = xch_resp.status_code
        if general_response == 202:
            # Get API information
            post_resp = req_session.get(exchange_url)

            # Checks that the API sent over information
            general_response = post_resp.status_code
            if general_response == 200:
                api_data = post_resp.json()
                api_dict = json.loads(api_data)

                api_email = api_dict['api_email']
                api_key = api_dict['api_key']
                encrypted_nonce = api_dict['encrypted_nonce']

                # Import API public key
                import_msg = gpg.imp_pub_key(api_key)
                api_fingerprint = gpg.email_to_key(api_email)
                gpg.trust_key(api_fingerprint)
                log.log2warning(20601, 'Import: {}'.format(import_msg))

                # Decrypt nonce
                passphrase = gpg.passphrase
                decrypted_nonce = gpg.decrypt_data(encrypted_nonce,
                                                   passphrase)

                # Further processing happens out of this nesting
            else:
                except_msg = 'Could not retrieve GET information.'\
                             'Status: {}'.format(general_response)
                raise Exception(except_msg)

            # Futher processing continues here

            # Symmetrically encrypt nonce
            encrypted_nonce = gpg.symmetric_encrypt(decrypted_nonce,
                                                    symmetric_key)

            # Encrypt symmetric key
            encrypted_sym_key = gpg.encrypt_data(symmetric_key,
                                                 api_fingerprint)

            # Prepare data to send to API
            validation_data = {'encrypted_nonce': encrypted_nonce,
                               'encrypted_sym_key': encrypted_sym_key}

            # POST data to API
            validation_resp = req_session.post(validation_url,
                                               json=validation_data)

            # Check that the transaction was validated
            general_response = validation_resp.status_code
            if general_response == 200:

                # The exchange and validation has been successful
                general_result = True
            else:
                except_msg = 'Could not validate information.'\
                             'Status: {}'.format(general_response)
                raise Exception(except_msg)

        else:
            except_msg = 'Could not send POST information. Status: {}'\
                         .format(general_response)
            raise Exception(except_msg)
    except Exception as e:
        log_msg = 'Error encountered: >>>{}<<<'.format(e)
        log.log2warning(20600, log_msg)

    return general_result


def purge(url, identifier):
    """Purge data from cache by posting to central server.

    Args:
        url: URL to receive posted data
        identifier: Identifier to use for posting

    Returns:
        None

    """
    # Initialize key variables
    config = Config()
    cache_dir = config.agent_cache_directory(identifier)

    # Add files in cache directory to list only if they match the
    # cache suffix
    all_filenames = [filename for filename in os.listdir(
        cache_dir) if os.path.isfile(
            os.path.join(cache_dir, filename))]
    filenames = [
        filename for filename in all_filenames if filename.endswith(
            '.json')]

    # Read cache file
    for filename in filenames:
        # Only post files for our own UID value
        if identifier not in filename:
            continue

        # Get the full filepath for the cache file and post
        filepath = os.path.join(cache_dir, filename)
        with open(filepath, 'r') as f_handle:
            try:
                data = json.load(f_handle)
            except:
                # Log removal
                log_message = ('''\
Error reading previously cached agent data file {} for identifier {}. May be \
corrupted.'''.format(filepath, identifier))
                log.log2warning(1064, log_message)

                # Delete file
                if os.path.isfile(filepath) is True:
                    os.remove(filepath)

                    log_message = ('''\
Deleting corrupted cache file {} for identifier {}.\
'''.format(filepath, identifier))
                    log.log2warning(1036, log_message)

                # Go to the next file.
                continue

        # Post file
        success = post(url, data, identifier, save=False)

        # Delete file if successful
        if success is True:
            if os.path.exists(filepath) is True:
                os.remove(filepath)

                # Log removal
                log_message = ('''\
    Purging cache file {} after successfully contacting server {}\
    '''.format(filepath, url))
                log.log2info(1007, log_message)


def _save_data(data, identifier):
    """Save data to cache file.

    Args:
        data: Dict to save
        identifier: Identifier

    Returns:
        success: True: if successful

    """
    # Initialize key variables
    success = False
    config = Config()
    cache_dir = config.agent_cache_directory(identifier)
    timestamp = int(time() * 1000)

    # Create a unique very long filename to reduce risk of
    filename = ('''{}{}{}_{}.json\
'''.format(cache_dir, os.sep, timestamp, identifier))

    # Save data
    try:
        with open(filename, 'w') as f_handle:
            json.dump(data, f_handle)
        success = True
    except Exception as err:
        log_message = '{}'.format(err)
        log.log2warning(1030, log_message)
    except:
        (etype, evalue, etraceback) = sys.exc_info()
        log_message = ('''\
Cache-file save error: [{}, {}, {}]'''.format(etype, evalue, etraceback))
        log.log2warning(1031, log_message)

    # Delete file if there is a failure.
    # Helps to protect against full file systems.
    if os.path.isfile(filename) is True and success is False:
        os.remove(filename)
        log_message = ('''\
Deleting corrupted cache file {} for identifier {}.\
'''.format(filename, identifier))
        log.log2warning(1037, log_message)

    # Return
    return success


def _log(agent_program, identifier):
    """Create a standardized log message for posting.

    Args:
        agent_program: Agent program name
        identifier: Identifier

    Returns:
        None

    """
    # Log message that ties the identifier to an agent_program
    log_message = ('''\
Agent program {} posting data as {}'''.format(agent_program, identifier))
    log.log2debug(1038, log_message)
