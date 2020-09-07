"""Encryption module."""

import uuid
import hashlib
import os
import random
import string
import stat
from collections import namedtuple

# PIP imports
import gnupg

# Pattoo imports
from pattoo_shared import configuration
from pattoo_shared import log
from pattoo_shared import files

# Create constant for processing
_METADATA = namedtuple('_METADATA', 'fingerprint passphrase')


class KeyRing():
    """Class for managing PGP keyring."""

    def __init__(self, agent_name, directory=None):
        """Instantiate the class.

        Args:
            agent_name: Name of agent generating the private key
            directory: Alternative key storage directory

        Returns:
            None

        """
        # Initialize key variables
        config = configuration.Config()
        self._agent_name = agent_name

        # Use the agent_id as the email address because it is a unique
        # identifier across all agents. This allows multiple agents with the
        # same name to have indepenent sessions.
        self.email = files.get_agent_id(agent_name, config)

        # Associate directories
        if directory is None:
            # Store keys and keyrings in directories named after the agent.
            # If the same directory were universally used there could be
            # conflicts in cases where the API daemon and agents run on the
            # same server This eliminates this risk.
            keyring_directory = config.keyring_directory(agent_name)
            self._keys_directory = config.keys_directory(agent_name)
        else:
            keyring_directory = '{}{}.keyring'.format(directory, os.sep)
            self._keys_directory = directory
            files.mkdir(directory)
            files.mkdir(keyring_directory)

        # Initialize GPG object. Note: options=['--pinentry-mode=loopback']
        # ensures the passphrase can be entered via python and won't prompt
        # the user.
        self._gpg = gnupg.GPG(
            gnupghome=keyring_directory,
            options=['--pinentry-mode=loopback'])

        # Import metadata for managing keys
        metadata = self._import()

        # Create and store metadata if nonexistent
        if metadata is None:
            metadata = self._generate(self.email)
            self._export(metadata)

        # Share passphrase
        self._passphrase = metadata.passphrase
        self._fingerprint = metadata.fingerprint

        # Get the public key ID
        self._public_keyid = self._get_public_keyid(metadata.fingerprint)

    def _import(self):
        """Import private key information.

        Method to import the fingerprint and passphrase of the owned public /
        private key pair of the user. The method also looks for a wrapper on
        the file to distinguish the public private key pair the user currently
        owns.

        Args:
            None

        Returns:
            result: Tuple of (fingerprint, passphrase), None if nonexistent

        """
        # Initialize key variables
        result = None
        directory = self._keys_directory

        # Get list of key files whose names end with the wrapper
        key = [_file for _file in os.listdir(
            directory) if _file.endswith(self.email)]

        # Process data
        count = len(key)
        if count > 1:
            # Die if we have duplicate keys found in the directory
            log_message = '''\
More than one agent_id "{}" key-pair stores found'''.format(self.email)
            log.log2die(1062, log_message)

        elif count == 1:
            # Get passphrase
            filename = key[0]
            filepath = os.path.abspath(os.path.join(directory, filename))
            try:
                fh_ = open(filepath, 'r')
            except PermissionError:
                log.log2die(1091, '''\
Insufficient permissions for reading the file:{}'''.format(filepath))
            except:
                log.log2die(1093, 'Error reading file:{}'.format(filepath))
            else:
                with fh_:
                    passphrase = fh_.read()

            # Basic validation
            if isinstance(passphrase, str) is False:
                log.log2die(1094, 'Corrupted keyfile:{}'.format(filepath))

            # Retrieve fingerprint from the filename
            fingerprint = filename.split('-')[0]
            result = _METADATA(fingerprint=fingerprint, passphrase=passphrase)

        return result

    def _export(self, metadata):
        """Export pertinent information.

        Method to store the passphrase for future retrieval and name the file
        by the fingerprint of the class. The method also adds a wrapper to the
        name of the file to assist in searching for the public private key
        pair, it finds the pair it owns.

        Args:
            None

        Returns:
            None
        """
        # Initialize variables
        directory = self._keys_directory
        filepath = os.path.abspath(os.path.join(
            directory, '{0}-{1}'.format(metadata.fingerprint, self.email)))

        # Export data
        try:
            fh_ = open(filepath, 'w')
        except PermissionError:
            log.log2die(1095, '''\
Insufficient permissions for writing the file:{}'''.format(filepath))
        except:
            log.log2die(1096, 'Error writing file:{}'.format(filepath))
        else:
            with fh_:
                fh_.write(metadata.passphrase)

        # Allow RW file access to only the current user
        os.chmod(filepath, stat.S_IRUSR | stat.S_IWUSR)

    def _generate(self, email, key_type='RSA', key_length=4096):
        """Generate public / private key-pairs.

        Args:
            email (str): Email of the user
            key_type (str): The key type of the private public key pair
            key_length (int): Key length of the private public key pair

        Returns:
            None
        """
        # Initialize key variables
        comment = 'Key pair generated for {}'.format(self._agent_name)

        # Generates random passphrase
        passphrase = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()

        # Generate key-pair
        data_ = self._gpg.gen_key_input(
            key_type=key_type,
            key_length=key_length,
            name_real=self._agent_name,
            name_comment=comment,
            name_email=email,
            passphrase=passphrase)
        key = self._gpg.gen_key(data_)
        fingerprint = key.fingerprint

        # Return results
        result = _METADATA(passphrase=passphrase, fingerprint=fingerprint)
        return result

    def _get_public_keyid(self, fingerprint):
        """Get the public key ID.

        Get the public key associated with the instance from a database of keys
        stored in the GnuPG keyring.

        Args:
            fingerprint: Fingerprint of the object instance

        Returns:
            result: Public key ID

        """
        # Initialize key variables
        result = None
        keys = self._gpg.list_keys()

        # Identify the public key
        for key in keys:
            if key['fingerprint'] == fingerprint:
                result = key['keyid']
                break

        # Return
        return result


class Encryption(KeyRing):
    """Class for managing PGP keypairs, currently using the python-gnupg.

    Resources:

    Chapter 7. Kurose J., Ross K.. (April, 2016).
    Computer Networking: A Top Down Approach.
    Pearson/Addison Wesley. Retrieved from
    http://www-net.cs.umass.edu/kurose-ross-ppt-7e/Chapter_8_V7.0.pptx

    Secure email style of encryption was used. So first, the key pairs
    are generated (public and private keys) so that it can be used to
    encrypt a randomly generated nonce and symmetric key. The nonce is
    used to provide a level of authentication. The symmetric key is
    used to encrypt the data since it is computationally less expensive
    than encrypting with a public key.

    What makes this module special, is it's ability to have a
    non-volatile approach to handle the passphrase, fingerprint
    and other variables with ease. The python-gnupg module
    provides most of the functionalities except keeping a track
    of the passphrase, the fingerprint, who owns the
    passphrase and fingerprint, etc. This module also simplifies
    the python-gnupg module to it can be widely used.

    The module uses one primary public private key pair to encrypt
    data. However, the module can also store other public keys.

    """

    def __init__(self, agent_name, directory=None):
        """Instantiate the class.

        Args:
            agent_name: Name of agent generating the private key
            email: Email address to use for encryption
            directory: Alternative key storage directory

        Returns:
            None

        """
        KeyRing.__init__(self, agent_name, directory=directory)

    def decrypt(self, data):
        """Decrypt data using a public key the GnuPG keyring.

        Args:
            data (str): Data in String ASCII to be decrypted

        Returns:
            result: Decrypted data into string

        """
        # Return
        result = self._decrypt(data)
        return result

    def sdecrypt(self, data, passphrase):
        """Decrypt data using an existing public key in the GnuPG keyring.

        Args:
            data (str): Data in ASCII string to be decrypted
            passphrase (str): Passphrase used in the encryption

        Returns:
            str: ASCII string of decrypted data
        """
        # Return
        result = self._decrypt(data, passphrase=passphrase)
        return result

    def _decrypt(self, data, passphrase=None):
        """Decrypt data using a public key the GnuPG keyring.

        Args:
            data (str): Data in String ASCII to be decrypted
            passphrase (str): Passphrase of the user

        Returns:
            result: Decrypted data into string

        """
        # Initialize the passphrase
        if bool(passphrase) is False:
            passphrase = self._passphrase
        decrypted = self._gpg.decrypt(data, passphrase=passphrase)

        # Return
        result = (decrypted.data).decode()
        return result

    def encrypt(self, data, recipients=None):
        """Encrypt data using expected key in the user's GnuPG keyring,

        Args:
            data (str): Data to be encrypted
            recipients (int): Fingerprint of recipient

        Returns:
            result (str): encrypted data in ASCII string

        """
        # Initialize key variables
        if recipients is None:
            recipients = self._fingerprint

        # Return
        result = str(
            self._gpg.encrypt(
                data,
                passphrase=None,
                recipients=recipients,
                symmetric=False
            )
        )
        return result

    def sencrypt(self, data, passphrase):
        """Symmetric encrypt.

        Method to encrypt data using symmmetric key encryption
        using a passphrase and encryption
        algorithm

        Args:
            data (str): String of data to be encrypted
            passphrase (str): Passphrase to be used to encrypt the data

        Returns:
            result: ASCII string of encrypted data

        """
        # Return
        result = str(
            self._gpg.encrypt(
                data,
                passphrase=passphrase,
                recipients=None,
                symmetric=True
            )
        )
        return result

    def trust(self, fingerprint, trustlevel='TRUST_ULTIMATE'):
        """Trust imported public key to encrypt data.

        Args:
            fingerprint (int): Fingerprint of pubic key to trust
            trustlevel (str): Trust level to assign to public key

        Returns:
            None
        """
        # Apply
        self._gpg.trust_keys(fingerprint, trustlevel)

    def fingerprint(self, email=None):
        """Get GnuPG keyring fingerprint that matches an email address.

        Args:
            email (str): Email address

        Returns:
            result: Fingerprint that is associated with the email

        """
        # Initialize key variables
        result = None

        # Go through each public key
        if email is None:
            result = self._fingerprint
        else:
            for key in self._gpg.list_keys():
                uids = list(filter((lambda item: email in item), key['uids']))
                if bool(uids) is True:
                    parts = uids[0].split()
                    wrapped_email = list(
                        filter((lambda item: '<' in item), parts))
                    unwrapped_email = wrapped_email[0].strip('<>')
                    if unwrapped_email == email:
                        result = key['fingerprint']
                        break

        return result

    def pdelete(self, fingerprint):
        """Delete public key from keyring.

        Args:
            fingerprint: Fingerprint of public key to be deleted

        Returns:
            result (bool): True if the public key was deleted False if the
                public key was not deleted

        """
        # Initialize key variables
        result = False

        # Delete public key
        if fingerprint != self._fingerprint:
            _result = self._gpg.delete_keys(fingerprint)
            result = str(_result).lower() == 'ok'
        return result

    def pexport(self, recipient=None):
        """Export the user's public key into ASCII.

        Args:
            recipient: fingerpint for which public key is required

        Returns:
            result: String of ASCII armored public key

        """
        # Initialize key variables
        result = None

        # Return result
        if recipient is None:
            keyid = self._public_keyid
        else:
            keyid = self._get_public_keyid(recipient)
        if keyid is not None:
            result = self._gpg.export_keys(keyid)
        return result

    def pimport(self, key):
        """Import public key into the current user's GnuPG keyring.

        Args:
            key (str): String of public key armored ASCII

        Returns:
            None

        """
        # Import
        self._gpg.import_keys(key)


def generate_key(length=70):
    """Generate a random string for use as a encryption key.

    Args:
        length (str): Maximum length of the key.

    Returns:
        result: key

    """
    # Return
    characters = string.ascii_letters + string.digits + string.punctuation
    result = ''.join(random.choice(characters) for i in range(length))
    return result
