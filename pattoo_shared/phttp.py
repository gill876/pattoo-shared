#!/usr/bin/env python3
"""Pattoo HTTP data classes."""

# Standard libraries
import os
import sys
import json
import urllib
import collections
from time import time

# pip3 libraries
import requests

# Pattoo libraries
from pattoo_shared import log
from pattoo_shared.configuration import Config
from pattoo_shared import converter

# Save items needed for encrypted purging inside a named tuple
EncryptionSuite = collections.namedtuple(
    'EncryptionSuite',
    'post gpg symmetric_key session')


class _Post():
    """Abstract class to prepare data for posting to remote pattoo server."""
    def __init__(self, identifier, data):
        """Initialize the class.

        Args:
            identifier: Unique identifier for the source of the data. (AgentID)
            data: dict of data to post

        Returns:
            None

        """
        # Initialize key variables
        self.config = Config()

        # Get data and identifier
        self._data = data
        self._identifier = identifier

    def post(self):
        """Post data to API server.

        Args:
            None

        Returns:
            success (bool): True: if successful

        """
        pass

    def purge(self):
        """Delete cached data and post to API server.

        Args:
            None

        Returns:
            None

        """
        pass


class Post(_Post):
    """Class to prepare data for posting to remote pattoo server."""

    def __init__(self, identifier, data):
        """Initialize the class.

        Args:
            identifier: Agent identifier
            data: Data from agent

        Returns:
            None

        """

        _Post.__init__(self, identifier, data)
        # URL to post to API server
        self._url = self.config.agent_api_server_url(identifier)

    def post(self):
        """Post data to central server.

        Args:
            None

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
            None

        """
        # Initialize key variables
        purge(self._url, self._identifier)


class EncryptedPost(_Post):
    """Encrypted Post.

    Class to exchange public keys, set symmetric key and
    post symmetrically encrypted data to the API server

    First, the agent's information is exchanged. That
    information consists of the agent's email address
    and public key in ASCII. That information is received
    the the API server, the agent's public key is added to
    the API server's keyring and the agent's email address
    is stored in the API server's session to be used to
    retrieve the public key later on. Cookies are used to
    uniquely identity the agents. Secondly, the API
    server then sends a nonce encrypted by the agent's
    public key, the API sever's email address, and the
    API server's public key in ASCII. Then, the agent
    decrypts the nonce using its own private key. Having
    the decrypted nonce, the agent generates a symmetric
    key to symmetrically encrypt the nonce. The
    symmetric key is then encrypted using the API server's
    public key. Those two information are sent off to the
    API server. Finally, the encrypted symmetric key is
    decrypted using the API server's private key, then the
    symmetric key is used to decrypt the nonce. Once the
    nonce is verified to be the same that was sent off,
    the symmetric is stored, and all other information the
    API received is deleted. A response is sent to the
    agent and the agent proceeds to send data encrypted by
    the symmetric key. The data is decrypted once received
    by the API server. See encrypt.py for more details on
    the module.
    """

    def __init__(self, identifier, data, gpg):
        """Initialize the class.

        Args:
            gpg (obj): Pgpier object to accommodate encryption

        Returns:
            None
        """

        _Post.__init__(self, identifier, data)

        # Set Pgpier object
        self._gpg = gpg

        # Get URLs for encryption
        self._exchange_key = self.config.agent_api_key_url()
        self._validate_key = self.config.agent_api_validation_url()
        self._encryption = self.config.agent_api_encrypted_url()

        # Get requirements for key exchange
        self._session = requests.Session()
        # Turn off HTTP Persistent connection
        self._session.keep_alive = False

        # Encryption requirements
        # Random str of len 20
        self._symmetric_key = self._gpg.gen_symm_key(20)

    def purge(self):
        """Purge.

        Purge data from cache by posting encrypted data
        to the API server.

        Args:
            gpg (obj): Pgpier object to facilitate encryption

        Returns:
            None

        """
        result = False

        # Check if key was exchanged
        exchanged = self.set_encryption()

        # If the key exchanged failed, return result
        if exchanged is False:
            return result

        # Add data to named tuple for encrypted_post
        suite = EncryptionSuite(
            encrypted_post, self._gpg,
            self._symmetric_key, self._session)

        # Purge data, encrypt and send to API
        purge(self._encryption, self._identifier, suite)

    def post(self):
        """Send encrypted data to the API server.

        Args:
            gpg (obj): Pgpier object to facilitate encryption

        Returns (bool): True if data was posted successfully
                        False if data failed to post

        """
        # Predefine variables
        result = False

        # Check if key was exchanged
        exchanged = self.set_encryption()

        # If the key exchanged failed, return result
        if exchanged is False:
            return result

        # Post data
        if bool(self._data) is True:
            result = encrypted_post(self._gpg, self._symmetric_key,
                                    self._session, self._encryption,
                                    self._data, self._identifier)
        else:
            log_message = ('Blank data. No data to post from '
                           'identifier {}.'.format(self._identifier))
            log.log2warning(1056, log_message)

        return result

    def set_encryption(self):
        """Set up encryption.

        Exchanges public keys and
        sets a symmetric key for encryption

        Args:
            gpg (obj): Pgpier object to facilitate encryption

        Returns:
            (bool): True if the exchange was successful
                    False if the exchange failed
        """

        result = key_exchange(self._gpg, self._session, self._exchange_key,
                              self._validate_key, self._symmetric_key)

        return result


class PostAgent(Post):
    """Class to post AgentPolledData to remote pattoo server."""

    def __init__(self, agentdata):
        """Initialize the class.

        Args:
            agentdata: AgentPolledData object

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


class EncryptedPostAgent(EncryptedPost):
    """Encrypted Post Agent.

    Class to prepare data for posting encrypted
    data to remote pattoo server."""

    def __init__(self, agentdata, gpg):
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
        EncryptedPost.__init__(self, identifier, data, gpg)


class PassiveAgent():
    """Gets data from passive Pattoo Agents for relaying to pattoo API."""

    def __init__(self, agent_program, identifier, url):
        """Initialize the class.

        Args:
            agent_program: Agent program name
            identifier: Unique identifier for the source of the data. (AgentID)
            url: URL of content to be retrieved from passive Pattoo agent

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
        identifier: Unique identifier for the source of the data. (AgentID)
        data: Data dict to post. If None, then uses self._post_data (
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
    """Exchange point for API and Agent public keys.

    First, post the agent information to the API to process and
    store the agent's email address and ASCII public key. Secondly,
    the API server sends the agent it's email address, ASCII pubic
    key and a nonce encrypted by the agent's public key. The agent
    decrypts the nonce and encrypts the nonce with a randomly
    generated symmetric key. The symmetric key is then encrypted by
    the API server's public key. The encrypted nonce and encrypted
    symmetric key are sent to the API server. The API server decrypts
    the two data and checks if nonce that was sent is the same as the
    nonce decrypted. If both nonces match, the server sends an OK
    signal to the agent. Lastly, the symmetric key is then used to
    encrypt data that is going to be sent to the API server.

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

    # Convert dict to str
    send_data = json.dumps(send_data)

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
                api_dict = post_resp.json()

                api_email = api_dict['data']['api_email']
                api_key = api_dict['data']['api_key']
                encrypted_nonce = api_dict['data']['encrypted_nonce']

                # Import API public key
                import_msg = gpg.imp_pub_key(api_key)
                api_fingerprint = gpg.email_to_key(api_email)
                gpg.trust_key(api_fingerprint)
                log.log2info(1069, 'Import: {}'.format(import_msg))

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

            # Convert dict to str
            validation_data = json.dumps(validation_data)

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

        # Check if a symmetric key was already set at the API
        elif general_response == 208:
            general_result = True
            msg = 'Symmetric key already set'
            log.log2info(1057, msg)

        else:
            except_msg = 'Could not send POST information. Status: {}'\
                         .format(general_response)
            raise Exception(except_msg)
    except Exception as e:
        log_msg = 'Error encountered: >>>{}<<<'.format(e)
        log.log2warning(1077, log_msg)

    return general_result


def encrypted_post(gpg, symmetric_key, req_session,
                   url, data, identifier, save=True):
    """Post encrypted data to the API server.

    First, the data is checked for its validity. Sencondly,
    the data and agent ID is stored in a dictionary with
    the key value pairs. The dictionary is converted to a
    string so that is can be encrypted. The encrypted data
    is then paired with a key, as a dictionary, distinguishing
    the data as encrypted. The dictionary is then converted
    to a string so it can be added to the request method
    as json. A response from the API server tells if the data
    was received and decrypted successfully.

    Args:
        gpg (obj): Pgpier object to accommodate encryption
        symmetric_key (str): Symmetric key used to encrypt data
        req_session (obj): Request session used to remember the session
                           used to communicate with the API server
        url (str): API URL to post the data to
        data (dict): Data to be posted to the API server
        identifier (str): The agent identification
        save (bool): True to save data to cache directory if
                     posting fails

    Returns:
        general_result (bool)

    """
    # Initialize key variables
    general_result = False

    # Fail if nothing to post
    if isinstance(data, dict) is False or bool(data) is False:
        return general_result

    # Prepare and encrypt data
    raw_data = {"data": data, "source": identifier}
    # Convert dictionary to string for encryption
    prep_data = json.dumps(raw_data)
    # Symmetrically encrypt data
    encrypted_data = gpg.symmetric_encrypt(prep_data, symmetric_key)
    post_data = {"encrypted_data": encrypted_data}
    post_data = json.dumps(post_data)

    # Post data save to cache if this fails
    response_code = None
    try:
        response = req_session.post(url, json=post_data)
        response_code = response.status_code
    except Exception as e:
        log_msg = 'Error encountered: >>>{}<<<'.format(e)
        log.log2warning(1075, log_msg)
        if save is True:
            # Save data to cache
            _save_data(data, identifier)
        else:
            # Proceed normally if there is a failure.
            # This will be logged later
            pass

    # Checks if data was posted successfully
    if response_code == 202:
        log_message = ('Posted to API. Response "{}".'
                       'from URL: "{}"'
                       .format(response_code, url)
                       )
        log.log2debug(1059, log_message)
        # The data was accepted successfully
        general_result = True
    else:
        log_message = ('Error posting. Response "{}".'
                       'from URL: "{}"'
                       .format(response_code, url)
                       )
        log.log2warning(1058, log_message)

    return general_result


def purge(url, identifier, suite=post):
    """Purge data from cache by posting to central server.

    Args:
        url: URL to receive posted data
        identifier: Unique identifier for the source of the data. (AgentID)
        suite (function)/ (EncryptionSuite): If function, this will
        proceed to use the normal post function for unencrypted posting.
        If EncryptionSuite, the necessary variables from the named tuple will
        be used along with the encrypted_post function for encrypted posting

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
        if callable(suite):  # Is it a function?
            # Post unencrypted data
            success = suite(url, data, identifier, save=False)
        elif isinstance(suite, EncryptionSuite):  # Is it EncryptionSuite?
            # Post encrypted data
            success = suite.post(
                suite.gpg, suite.symmetric_key, suite.session,
                url, data, identifier, save=False)

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
        identifier: Unique identifier for the source of the data. (AgentID)

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
        identifier: Unique identifier for the source of the data. (AgentID)

    Returns:
        None

    """
    # Log message that ties the identifier to an agent_program
    log_message = ('''\
Agent program {} posting data as {}'''.format(agent_program, identifier))
    log.log2debug(1038, log_message)
