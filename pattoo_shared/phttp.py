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
from pattoo_shared import encrypt

# Save items needed for encrypted purging inside a named tuple
EncryptionSuite = collections.namedtuple(
    'EncryptionSuite',
    'encrypted_post encryption symmetric_key session')

_KeyExchange = collections.namedtuple(
    '_KeyExchange',
    'encryption session key_exchange_url symmetric_key_url symmetric_key')

_EncrypedPost = collections.namedtuple(
    '_EncrypedPost',
    'encryption session symmetric_key encryption_url data identifier')


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
            None

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

    def __init__(self, identifier, data, encryption):
        """Initialize the class.

        Args:
            identifier: Agent identifier
            data: Data from agent
            encryption: encrypt.Encryption object

        Returns:
            None

        """
        # Instantiate Post class
        _Post.__init__(self, identifier, data)

        # Get URLs for encryption
        self._encryption = encryption

    def purge(self):
        """Purge.

        Purge data from cache by posting encrypted data
        to the API server.

        Args:
            None

        Returns:
            None

        """
        # Initialize key variables
        success = False
        key = encrypt.generate_key(20)

        # Create a session and post data
        with requests.Session() as session:
            # Turn off HTTP Persistent connection
            session.keep_alive = False

            # Exchange keys
            success = key_exchange(
                _KeyExchange(
                    encryption=self._encryption,
                    session=session,
                    key_exchange_url=self.config.agent_api_key_url(),
                    symmetric_key_url=self.config.agent_api_validation_url(),
                    symmetric_key=key
                )
            )

        # Purge data, encrypt and send to API
        if success is True:
            purge(
                self.config.agent_api_encrypted_url(),
                self._identifier,
                suite=EncryptionSuite(
                    encrypted_post=encrypted_post,
                    encryption=self._encryption,
                    symmetric_key=key,
                    session=session
                )
            )

    def post(self):
        """Send encrypted data to the API server.

        Args:
            None

        Returns:
            success: True if data was posted successfully

        """
        # Initialize key variables
        success = False
        key = encrypt.generate_key(20)

        # Create a session and post data
        with requests.Session() as session:
            # Turn off HTTP Persistent connection
            session.keep_alive = False

            # Exchange keys
            result = key_exchange(
                _KeyExchange(
                    encryption=self._encryption,
                    session=session,
                    key_exchange_url=self.config.agent_api_key_url(),
                    symmetric_key_url=self.config.agent_api_validation_url(),
                    symmetric_key=key
                )
            )
            # Return if exchange failed
            if result is False:
                return success

            # Post data
            if bool(self._data) is True:
                success = encrypted_post(
                    _EncrypedPost(
                        encryption=self._encryption,
                        session=session,
                        symmetric_key=key,
                        encryption_url=self.config.agent_api_encrypted_url(),
                        data=self._data,
                        identifier=self._identifier
                    )
                )

            else:
                log_message = '''\
Blank data. No data to post from identifier {}.'''.format(self._identifier)
                log.log2warning(1056, log_message)

        return success


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

    def __init__(self, agentdata, encryption):
        """Initialize the class.

        Args:
            agentdata: Agent data
            encryption: encrypt.Encryption object

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
        EncryptedPost.__init__(self, identifier, data, encryption)


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
        _exception = sys.exc_info()
        log_message = ('Data posting failure')
        log.log2exception(1097, _exception, message=log_message)
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


def key_exchange(metadata):
    """Exchange point for API and Agent public keys.

    Process:
        1) Post agent's email address and ASCII public key to API server.
        2) API server responds with its email address, ASCII pubic
           key and a nonce encrypted by the agent's public key.
        3) The agent decrypts the nonce and re-encrypts it with a randomly
           generated symmetric key.
        4) The symmetric key is then encrypted by the API server's public key.
        5) The encrypted nonce and encrypted symmetric key are sent to the API
           server.
        6) The API server decrypts this data and checks if nonce that was sent
           is the same as the nonce decrypted.
        7) If both nonces match, the server sends an OK signal to the agent.
        8) The symmetric key is used to encrypt data sent to the API server.

    Args:
        metadata: _KeyExchange object where:
            encryption: encrypt.Encryption object
            session: Requests session object
            symmetric_key: Symmetric key
            symmetric_key_url: API URL for symmetric key validation
            key_exchange_url: URL for key exchanges with the API server
            identifier: Agent identifier

    Returns:
        success: True if successful

    """
    # Predefine failure response
    success = False

    # Send the public key
    status = _send_agent_public_key(
        metadata.session,
        metadata.encryption,
        metadata.key_exchange_url
    )
    if status is False:
        return success

    # Get get API server's public key
    data = _get_api_public_key(
        metadata.session,
        metadata.key_exchange_url
    )
    if bool(data) is False:
        return success

    # Exchange symmetric key
    success = _send_symmetric_key(
        metadata.session,
        metadata.encryption,
        metadata.symmetric_key_url,
        metadata.symmetric_key,
        data
    )
    return success


def _send_agent_public_key(session, encryption, exchange_url):
    """Send public key to the remote API server.

    Args:
        session: Request Session object
        encryption: Encryption object
        exchange_url: URL to use for key exchange

    Returns:
        success: True is successful

    """
    # Predefine failure response
    success = False
    status = None

    # Data for POST
    send_data = {
        'pattoo_agent_email': encryption.email,
        'pattoo_agent_key': encryption.pexport()
    }

    # Convert dict to str
    send_data = json.dumps(send_data)

    try:
        # Send over data
        response = session.post(exchange_url, json=send_data)
        status = response.status_code
    except:
        _exception = sys.exc_info()
        log_message = ('Key exchange failure')
        log.log2exception(1077, _exception, message=log_message)

    # Checks that sent data was accepted
    if status in [202, 208]:
        success = True
    else:
        log_message = (
            'Cannot send public key to API server. Status: {}'.format(status))
        log.log2info(1069, log_message)

    return success


def _get_api_public_key(session, exchange_url):
    """Use previously established session to get the API server's public key.

    Args:
        session: Request Session object
        exchange_url: URL to use for key exchange

    Returns:
        result: JSON key data from API server

    """
    # Predefine failure response
    result = None
    status = None

    # Get API information
    try:
        response = session.get(exchange_url)
        status = response.status_code
    except:
        _exception = sys.exc_info()
        log_message = ('Key exchange failure')
        log.log2exception(1106, _exception, message=log_message)

    # Checks that the API sent over information
    if status == 200:
        # Process API server response
        result = response.json()
    else:
        log_message = (
            'Cannot get public key from API server. Status: {}'.format(status))
        log.log2info(1057, log_message)

    return result


def _send_symmetric_key(
        session, encryption, url, symmetric_key, data):
    """Send symmetric_key to the remote API server.

    Args:
        session: Request Session object
        encryption: Encryption object
        url: URL to use for exchanging the symmetric key
        symmetric_key: Symmetric key
        data: Data to post

    Returns:
        success: True if successful

    """
    # Predefine failure response
    success = False
    status = None

    # Process API server information
    api_email = data['api_email']
    api_key = data['api_key']
    encrypted_nonce = data['encrypted_nonce']

    # Import API public key
    encryption.pimport(api_key)
    api_fingerprint = encryption.fingerprint(api_email)
    encryption.trust(api_fingerprint)

    # Decrypt nonce
    decrypted_nonce = encryption.decrypt(encrypted_nonce)

    # Create JSON to post
    data_ = json.dumps(
        {
            'encrypted_nonce': encryption.sencrypt(
                decrypted_nonce, symmetric_key),
            'encrypted_sym_key': encryption.encrypt(
                symmetric_key, api_fingerprint)
        }
    )

    # POST data to API
    try:
        response = session.post(url, json=data_)
        status = response.status_code
    except:
        _exception = sys.exc_info()
        log_message = ('Symmetric key exchange failure')
        log.log2exception(1098, _exception, message=log_message)

    # Check that the transaction was validated
    if status == 200:
        success = True
    else:
        log_message = '''\
Cannot exchange symmetric keys with API server. Status: {}'''.format(status)
        log.log2info(1099, log_message)

    return success


def encrypted_post(metadata, save=True):
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
        metadata: _EncrypedPost object where:
            encryption: encrypt.Encryption object
            session: Requests session object
            symmetric_key: Symmetric key
            encryption_url: API URL to post the data to
            data: Data to post as a dict
            identifier: Agent identifier
        save: If True, save data to cache if API server is inaccessible

    Returns:
        success: True if successful

    """
    # Initialize key variables
    success = False
    status = None

    # Fail if nothing to post
    if isinstance(metadata.data, dict) is False or bool(
            metadata.data) is False:
        return success

    # Prepare data for posting
    data = json.dumps(
        {
            'data': metadata.data,
            'source': metadata.identifier
        }
    )

    # Symmetrically encrypt data
    encrypted_data = metadata.encryption.sencrypt(data, metadata.symmetric_key)

    # Post data save to cache if this fails
    try:
        response = metadata.session.post(
            metadata.encryption_url,
            json=json.dumps({'encrypted_data': encrypted_data})
        )
        status = response.status_code
    except:
        _exception = sys.exc_info()
        log_message = ('Encrypted posting failure')
        log.log2exception(1075, _exception, message=log_message)
        if save is True:
            # Save data to cache
            _save_data(metadata.data, metadata.identifier)
        else:
            # Proceed normally if there is a failure.
            # This will be logged later
            pass

    # Checks if data was posted successfully
    if status == 202:
        log_message = 'Posted to API. Response "{}" from URL: "{}"'.format(
            status, metadata.encryption_url)
        log.log2debug(1059, log_message)

        # The data was accepted successfully
        success = True
    else:
        log_message = 'Error posting. Response "{}" from URL: "{}"'.format(
            status, metadata.encryption_url)
        log.log2warning(1058, log_message)

    return success


def purge(url, identifier, suite=post):
    """Purge data from cache by posting to central server.

    Args:
        url: URL to receive posted data
        identifier: Unique identifier for the source of the data. (AgentID)
        suite: If a function, this will proceed to use the normal post function
            for unencrypted posting. If EncryptionSuite, the necessary
            variables from the named tuple will be used along with the
            encrypted_post function for encrypted posting

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
            success = suite.encrypted_post(
                _EncrypedPost(
                    encryption=suite.encryption,
                    session=suite.session,
                    symmetric_key=suite.symmetric_key,
                    encryption_url=url,
                    data=data,
                    identifier=identifier
                )
            )

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
