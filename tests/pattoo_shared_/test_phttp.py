#!/usr/bin/env python3
"""Test the phttp module."""

# Standard imports
import json
import hashlib
import uuid
import os
import random
import tempfile
import sys
from time import time
import unittest
from unittest.mock import patch

# PIP imports
import requests_mock

# Try to create a working PYTHONPATH
EXEC_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(
    os.path.abspath(os.path.join(EXEC_DIR, os.pardir)), os.pardir))
_EXPECTED = '{0}pattoo-shared{0}tests{0}pattoo_shared_'.format(os.sep)
if EXEC_DIR.endswith(_EXPECTED) is True:
    # We need to prepend the path in case PattooShared has been installed
    # elsewhere on the system using PIP. This could corrupt expected results
    sys.path.insert(0, ROOT_DIR)
else:
    print('''This script is not installed in the "{0}" directory. Please fix.\
'''.format(_EXPECTED))
    sys.exit(2)

# Pattoo imports
from pattoo_shared import phttp
from pattoo_shared import data
from pattoo_shared import converter
from pattoo_shared import files
from pattoo_shared import encrypt
from tests.libraries.configuration import UnittestConfig
from tests.libraries import general as ta


class Test_Post(unittest.TestCase):
    """Test _Post."""

    # Create agent data
    agentdata = ta.test_agent()

    # Get agent variables
    identifier = agentdata.agent_id
    _data = converter.agentdata_to_post(agentdata)
    data = converter.posting_data_points(_data)

    def test___init__(self):
        """Testing method or function named __init__."""

        # Test
        _post = phttp._Post(self.identifier, self.data)

        self.assertEqual(_post._identifier, self.identifier)
        self.assertEqual(_post._data, self.data)


class TestPost(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    # Create agent data
    agentdata = ta.test_agent()

    # Get agent variables
    identifier = agentdata.agent_id
    _data = converter.agentdata_to_post(agentdata)
    data = converter.posting_data_points(_data)

    # Change tuple to list in the data
    _mod_data = json.dumps(data)
    mod_data = json.loads(_mod_data)

    def test___init__(self):
        """Testing method or function named __init__."""

        # Initialize
        post = phttp.Post(self.identifier, self.data)

        # Test
        expected_server_url = \
            '''http://127.0.0.6:50505/pattoo/api/v1/agent/receive/{}'''\
            .format(self.identifier)
        result_server_url = post._url

        self.assertEqual(result_server_url, expected_server_url)

    def test_post(self):
        """Testing method or function named post."""
        # Initialize
        post_test = phttp.Post(self.identifier, self.data)

        # Magically simulate post request
        with patch('pattoo_shared.phttp.requests.post') as mock_post:

            # Magically assign post response values
            mock_post.return_value.ok = True
            mock_post.return_value.text = 'OK'
            mock_post.return_value.status_code = 200

            # Run post
            success = post_test.post()

            # Check that the post request was to the right URL
            # and that it contained the right data
            mock_post.assert_called_with(
                '''http://127.0.0.6:50505/pattoo/api/v1/agent/receive/{}'''
                .format(self.identifier), json=self.data
                )

            # Assert that the success is True
            self.assertTrue(success)

    def test_purge(self):
        """Testing method or function named purge."""
        # Initialize
        purge_test = phttp.Post(self.identifier, self.data)

        # Magically simulate post request
        with patch('pattoo_shared.phttp.requests.post') as mock_post:

            # Magically assign post response values
            mock_post.return_value.ok = True
            mock_post.return_value.text = 'OK'
            mock_post.return_value.status_code = 200

            # Save data to cache
            phttp._save_data(self.data, self.identifier)

            # Run post
            purge_test.purge()

            # Check that the post request was to the right URL
            # and that it contained the right data
            mock_post.assert_called_with(
                '''http://127.0.0.6:50505/pattoo/api/v1/agent/receive/{}'''
                .format(self.identifier), json=self.mod_data
            )


class TestEncryptedPost(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    # Create agent data
    agentdata = ta.test_agent()

    # Get agent variables
    identifier = agentdata.agent_id
    _data = converter.agentdata_to_post(agentdata)
    data = converter.posting_data_points(_data)

    # Variables that will be modified by callback functions
    agent_publickey = None
    agent_email = None
    symmetric_key = None
    nonce = None

    # Initialize encrytion keys
    encrypt_agt = encrypt.Encryption(
        hashlib.md5('{}'.format(random.random()).encode()).hexdigest(),
        tempfile.mkdtemp()
    )
    encrypt_api = encrypt.Encryption(
        hashlib.md5('{}'.format(random.random()).encode()).hexdigest(),
        tempfile.mkdtemp()
    )

    # Create EncryptedPost object
    encrypted_post = phttp.EncryptedPost(identifier, data, encrypt_agt)

    def test___init__(self):
        """Testing method or function named __init__."""
        # Test variables
        pass

    def test_post(self):
        """Test EncryptedPost's post"""

        # Define callback functions

        # Key exchange callback for post request to process key exchange
        def exchange_post_callback(request, context):
            """Exchange callback for post request mock"""
            # Retrieve agent info from received request object
            json_data = request.json()
            json_dict = json.loads(json_data)

            self.agent_publickey = json_dict['pattoo_agent_key']
            self.agent_email = json_dict['pattoo_agent_email']

            # Import agent public key
            self.encrypt_api.pimport(self.agent_publickey)

            # Trust public keys to enable encryption with traded keys
            agent_fp = self.encrypt_api.fingerprint(self.agent_email)
            self.encrypt_api.trust(agent_fp)

            # Send accepted response
            context.status_code = 202
            return 'Noted'

        # Key exchange callback for post request to process key exchange
        def exchange_get_callback(request, context):
            """Exchange callback for post request mock"""
            # Status is OK
            context.status_code = 200
            # Generate nonce
            self.nonce = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()

            # Prepare API info to send to agent
            api_publickey = self.encrypt_api.pexport()

            # Encrypt nonce
            encrypted_nonce = self.encrypt_api.encrypt(
                self.nonce, self.encrypt_agt.fingerprint())

            json_response = {
                'api_email': self.encrypt_api.email,
                'api_key': api_publickey,
                'encrypted_nonce': encrypted_nonce
            }

            # Send data
            return json_response

        # Validation callback to respond to agent validation post request
        def validation_callback(request, context):
            """Validation callback for request mock"""
            # Retrieve agent info from received request object
            json_data = request.json()
            json_dict = json.loads(json_data)
            encrypted_nonce = json_dict['encrypted_nonce']
            encrypted_sym_key = json_dict['encrypted_sym_key']

            # Validate by decrypting the encrypted symmetric key
            # then using the symmetric key to decrypt the nonce
            # and check if it is the same as the one that was sent
            symmetric_key = self.encrypt_api.decrypt(encrypted_sym_key)
            nonce = self.encrypt_api.sdecrypt(encrypted_nonce, symmetric_key)

            if nonce == self.nonce:
                self.symmetric_key = symmetric_key
                context.status_code = 200
            else:
                context.status_code = 409

            return 'Result'

        # Encrypted post callback to respond to agent encrypted data
        def encrypted_callback(request, context):
            """Encrypted post callback for request mock"""
            # Retrieve encrypted data from received request object
            json_data = request.json()
            json_dict = json.loads(json_data)
            encrypted_data = json_dict['encrypted_data']
            # Decrypt data
            decrypted_data = self.encrypt_api.sdecrypt(
                encrypted_data, self.symmetric_key)
            # Unload
            data_dict = json.loads(decrypted_data)
            recv_data = data_dict['data']

            # Check that decrypted data is the same as the received
            # The two dictionaries are hashed then the values are compared
            agent_data = self.data
            agent_hash = hashlib.sha256(
                str(json.dumps(agent_data)).encode()).hexdigest()
            recv_hash = hashlib.sha256(
                str(json.dumps(recv_data)).encode()).hexdigest()
            if agent_hash == recv_hash:
                # Data received and decrypted successfully
                context.status_code = 202
            else:
                # Decryption failed
                context.status_code = 409

            return 'Noted'

        # Mock each requests
        with requests_mock.Mocker() as mock_:
            # Mock agent sending info to API server
            mock_.post(
                'http://127.0.0.6:50505/pattoo/api/v1/agent/key',
                text=exchange_post_callback)
            # Mock agent receiving API info
            mock_.get(
                'http://127.0.0.6:50505/pattoo/api/v1/agent/key',
                json=exchange_get_callback)
            # Mock agent validation
            mock_.post(
                'http://127.0.0.6:50505/pattoo/api/v1/agent/validation',
                text=validation_callback
            )

            mock_.post(
                'http://127.0.0.6:50505/pattoo/api/v1/agent/encrypted',
                text=encrypted_callback
            )

            # Run function
            success = self.encrypted_post.post()

            # Test
            self.assertTrue(success)

    def test_purge(self):
        """Test EncryptedPost's purge"""

        # Define callback functions

        # Key exchange callback for post request to process key exchange
        def exchange_post_callback(request, context):
            """Exchange callback for post request mock"""
            # Retrieve agent info from received request object
            json_data = request.json()
            json_dict = json.loads(json_data)

            self.agent_publickey = json_dict['pattoo_agent_key']
            self.agent_email = json_dict['pattoo_agent_email']

            # Import agent public key
            self.encrypt_api.pimport(self.agent_publickey)
            # Trust public keys to enable encryption with traded keys
            agent_fp = self.encrypt_api.fingerprint(self.agent_email)
            self.encrypt_api.trust(agent_fp)

            # Send accepted response
            context.status_code = 202
            return 'Noted'

        # Key exchange callback for post request to process key exchange
        def exchange_get_callback(request, context):
            """Exchange callback for post request mock"""
            # Status is OK
            context.status_code = 200
            # Generate nonce
            self.nonce = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()

            # Prepare API info to send to agent
            api_publickey = self.encrypt_api.pexport()

            # Encrypt nonce
            encrypted_nonce = self.encrypt_api.encrypt(
                self.nonce, self.encrypt_agt.fingerprint())

            # Create a json response
            json_response = {
                'api_email': self.encrypt_api.email,
                'api_key': api_publickey,
                'encrypted_nonce': encrypted_nonce
            }

            # Send data
            return json_response

        # Validation callback to respond to agent validation post request
        def validation_callback(request, context):
            """Validation callback for request mock"""
            # Retrieve agent info from received request object
            json_data = request.json()
            json_dict = json.loads(json_data)
            encrypted_nonce = json_dict['encrypted_nonce']
            encrypted_sym_key = json_dict['encrypted_sym_key']

            # Validate by decrypting the encrypted symmetric key
            # then using the symmetric key to decrypt the nonce
            # and check if it is the same as the one that was sent
            symmetric_key = self.encrypt_api.decrypt(encrypted_sym_key)
            nonce = self.encrypt_api.sdecrypt(encrypted_nonce, symmetric_key)

            if nonce == self.nonce:
                self.symmetric_key = symmetric_key
                context.status_code = 200
            else:
                context.status_code = 409

            return 'Result'

        # Encrypted post callback to respond to agent encrypted data
        def encrypted_callback(request, context):
            """Encrypted post callback for request mock"""
            # Retrieve encrypted data from received request object
            json_data = request.json()
            json_dict = json.loads(json_data)
            encrypted_data = json_dict['encrypted_data']
            # Decrypt data
            decrypted_data = self.encrypt_api.sdecrypt(
                encrypted_data, self.symmetric_key)
            # Unload
            data_dict = json.loads(decrypted_data)
            recv_data = data_dict['data']

            # Check that decrypted data is the same as the received
            # The two dictionaries are hashed then the values are compared
            agent_data = self.data
            agent_hash = hashlib.sha256(str(
                json.dumps(agent_data)).encode()).hexdigest()
            recv_hash = hashlib.sha256(str(
                json.dumps(recv_data)).encode()).hexdigest()
            if agent_hash == recv_hash:
                # Data received and decrypted successfully
                context.status_code = 202
            else:
                # Decryption failed
                context.status_code = 409

            return 'Noted'

        # Mock each requests
        with requests_mock.Mocker() as mock_:
            # Mock agent sending info to API server
            mock_.post(
                'http://127.0.0.6:50505/pattoo/api/v1/agent/key',
                text=exchange_post_callback)
            # Mock agent receiving API info
            mock_.get(
                'http://127.0.0.6:50505/pattoo/api/v1/agent/key',
                json=exchange_get_callback)
            # Mock agent validation
            mock_.post(
                'http://127.0.0.6:50505/pattoo/api/v1/agent/validation',
                text=validation_callback
            )

            mock_.post(
                'http://127.0.0.6:50505/pattoo/api/v1/agent/encrypted',
                text=encrypted_callback
            )

            # Save data to cache
            phttp._save_data(self.data, self.identifier)

            # Run purge
            self.encrypted_post.purge()

            # Check that URL's were called
            self.assertEqual(mock_.call_count, 4)


class TestPassiveAgent(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test___init__(self):
        """Testing method or function named __init__."""
        pass

    def test_relay(self):
        """Testing method or function named relay."""
        pass

    def test_get(self):
        """Testing method or function named get."""
        pass


class TestEncryptedPostAgent(unittest.TestCase):
    """Test EncryptedPostAgent"""

    # Initialize key variables
    encrypt_agt = encrypt.Encryption(
        hashlib.md5('{}'.format(random.random()).encode()).hexdigest(),
        tempfile.mkdtemp()
    )
    encrypt_api = encrypt.Encryption(
        hashlib.md5('{}'.format(random.random()).encode()).hexdigest(),
        tempfile.mkdtemp()
    )

    # Variables that will be modified by callback functions
    agent_publickey = None
    agent_email = None
    symmetric_key = None
    nonce = None

    def test_agent(self):
        """Test agent post and purge"""

        # Create agent data
        agentdata = ta.test_agent()

        # Get agent variables
        _data = converter.agentdata_to_post(agentdata)
        data2post = converter.posting_data_points(_data)

        # Create agent
        encrypted_agent = phttp.EncryptedPostAgent(agentdata, self.encrypt_agt)

        # Define callback functions

        # Key exchange callback for post request to process key exchange
        def exchange_post_callback(request, context):
            """Exchange callback for post request mock"""
            # Retrieve agent info from received request object
            json_data = request.json()
            json_dict = json.loads(json_data)

            self.agent_publickey = json_dict['pattoo_agent_key']
            self.agent_email = json_dict['pattoo_agent_email']

            # Import agent public key
            self.encrypt_api.pimport(self.agent_publickey)
            # Trust public keys to enable encryption with traded keys
            agent_fp = self.encrypt_api.fingerprint(self.agent_email)
            self.encrypt_api.trust(agent_fp)

            # Send accepted response
            context.status_code = 202
            return 'Noted'

        # Key exchange callback for post request to process key exchange
        def exchange_get_callback(request, context):
            """Exchange callback for post request mock"""
            # Status is OK
            context.status_code = 200
            # Generate nonce
            self.nonce = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()

            # Prepare API info to send to agent
            api_publickey = self.encrypt_api.pexport()

            # Encrypt nonce
            encrypted_nonce = self.encrypt_api.encrypt(
                self.nonce, self.encrypt_agt.fingerprint())

            json_response = {
                'api_email': self.encrypt_api.email,
                'api_key': api_publickey,
                'encrypted_nonce': encrypted_nonce
            }

            # Send data
            return json_response

        # Validation callback to respond to agent validation post request
        def validation_callback(request, context):
            """Validation callback for request mock"""
            # Retrieve agent info from received request object
            json_data = request.json()
            json_dict = json.loads(json_data)
            encrypted_nonce = json_dict['encrypted_nonce']
            encrypted_sym_key = json_dict['encrypted_sym_key']

            # Validate by decrypting the encrypted symmetric key
            # then using the symmetric key to decrypt the nonce
            # and check if it is the same as the one that was sent
            symmetric_key = self.encrypt_api.decrypt(encrypted_sym_key)
            nonce = self.encrypt_api.sdecrypt(encrypted_nonce, symmetric_key)

            if nonce == self.nonce:
                self.symmetric_key = symmetric_key
                context.status_code = 200
            else:
                context.status_code = 409

            return 'Result'

        # Encrypted post callback to respond to agent encrypted data
        def encrypted_callback(request, context):
            """Encrypted post callback for request mock"""
            # Retrieve encrypted data from received request object
            json_data = request.json()
            json_dict = json.loads(json_data)
            encrypted_data = json_dict['encrypted_data']

            # Decrypt data
            decrypted_data = self.encrypt_api.sdecrypt(
                encrypted_data, self.symmetric_key)

            # Unload
            data_dict = json.loads(decrypted_data)
            recv_data = data_dict['data']

            # Check that decrypted data is the same as the received
            # The two dictionaries are hashed then the values are compared
            agent_data = data2post
            if len(agent_data) == len(recv_data):
                # Data received and decrypted successfully
                context.status_code = 202
            else:
                # Decryption failed
                context.status_code = 409

            return 'Noted'

        # Mock each requests
        with requests_mock.Mocker() as mock_:
            # Mock agent sending info to API server
            mock_.post(
                'http://127.0.0.6:50505/pattoo/api/v1/agent/key',
                text=exchange_post_callback)

            # Mock agent receiving API info
            mock_.get(
                'http://127.0.0.6:50505/pattoo/api/v1/agent/key',
                json=exchange_get_callback)

            # Mock agent validation
            mock_.post(
                'http://127.0.0.6:50505/pattoo/api/v1/agent/validation',
                text=validation_callback
            )

            mock_.post(
                'http://127.0.0.6:50505/pattoo/api/v1/agent/encrypted',
                text=encrypted_callback
            )

            # Run function
            success = encrypted_agent.post()

            # Test
            self.assertTrue(success)

            # Get agent identifier from data
            identifier = agentdata.agent_id

            # Save data to cache
            phttp._save_data(data2post, identifier)

            # Encrypted purge
            encrypted_agent.purge()

            # Check that both the post and purge exchanged keys and
            # send data
            self.assertEqual(mock_.call_count, 8)


class TestBasicFunctions(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    def test_post(self):
        """Testing method or function named post."""
        pass

    def test_purge(self):
        """Testing method or function named purge."""
        pass

    def test__save_data(self):
        """Testing method or function named _save_data."""
        # Initialize key variables
        identifier = data.hashstring(str(time()))

        # Test valid
        _data = {'Test': 'data'}
        success = phttp._save_data(_data, identifier)
        self.assertTrue(success)

        # Test invalid
        _data = ''
        success = phttp._save_data(_data, identifier)
        self.assertTrue(success)

    def test__log(self):
        """Testing method or function named _log."""
        pass


if __name__ == '__main__':
    # Make sure the environment is OK to run unittests
    UnittestConfig().create()

    # Do the unit test
    unittest.main()
