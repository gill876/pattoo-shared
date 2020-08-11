#!/usr/bin/env python3

import gnupg
import uuid
import hashlib
import os
import random
import string
import stat


class Pgpier:
    """Pgpier class.

    A class that handles encryption and decryption
    using the python-gnupg module

    gpg, GPG, Pgpier and GnuPG is used interchangeably as the Pgpier
    class outside this file.

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

    def __init__(self, working_dir):
        """Instantiation of the class.

        The Pgpier class will instantiate with the working directory
        that also has a parent directory

        Args:
            working_dir (str): The path to the .gnupg directory where
                               GnuPG files will be stored
                               with a parent directory where this class
                               will store and handle pertinent
                               data

        Returns:
            None
        """

        self.wrk_dir = os.path.abspath(
            os.path.join(working_dir, os.pardir)
            )  # gets the parent of the working directory
        self.gnupghome = working_dir
        # , options=['--pinentry-mode=loopback']
        # the loopback option makes sure the passphrase can
        # be entered via python and won't prompt the user
        self.gpg = gnupg.GPG(gnupghome=working_dir,
                             options=['--pinentry-mode=loopback'])
        self.gpg.encoding = 'utf-8'  # sets encoding
        self.passphrase = None
        self.fingerprint = None
        self.keyid = None

    def key_pair(self, _name_email, _name_real,
                 _name_comment="auto generated using gnupg.py",
                 _key_type="RSA", _key_length=4096):
        """The generation of the private public key pairs.

        Args:
            _name_email (str): Email of the user
            _name_real (str): Full name of the user
            _name_comment (str): Optional comment for the user
            _key_type (str): The key type of the private public key pair
            _key_length (int): Key length of the private public key pair

        Returns:
            None
        """
        # generates random passphrase
        self.passphrase = hashlib.sha256(str(uuid.uuid4())
                                         .encode()).hexdigest()
        # helper method to get key configuration
        input_data = self.gpg.gen_key_input(key_type=_key_type,
                                            key_length=_key_length,
                                            name_real=_name_real,
                                            name_comment=_name_comment,
                                            name_email=_name_email,
                                            passphrase=self.passphrase)
        # generation of key pair
        key = self.gpg.gen_key(input_data)
        # print("stderr: ", key.stderr)
        self.fingerprint = key.fingerprint  # store fingerprint in class

    def set_passphrase(self, passphrase):
        """Method to set the passphrase in the class.

        The passphrase is needed to decrypt data encrypted
        by a public key.

        Args:
            passphrase (str): Passphrase to store in class

        Returns:
            None
        """
        self.passphrase = passphrase

    def set_fingerprint(self, fingerprint):
        """Method to set fingerprint in the class.

        Args:
            fingerprint (str): Fingerprint of the public private key pair

        Returns:
            None
        """
        self.fingerprint = fingerprint

    def set_keyid(self):
        """Set keyid in object.

        Method to set keyid by retrieving all keys stored
        in the GnuPG keyring and retrieve
        the keyid associated with the main public private key pair

        Args:
            None

        Returns:
            None
        """

        keys = self.list_pub_keys()
        fingerprint = self.fingerprint

        if keys != []:
            for key in keys:
                if key['fingerprint'] == fingerprint:
                    # set keyid associated with fingerprint in class
                    self.keyid = key['keyid']
        else:
            pass

    def list_pub_keys(self):
        """Method to list all the public keys stored in the GnuPG keyring.

        Args:
            None

        Returns:
            list: List of dictionaries of each public key stored
        """
        public_keys = self.gpg.list_keys()
        return public_keys

    def exp_main(self, _wrapper='(main)'):
        """Export pertinent information.

        Method to store the passphrase for future retrieval
        and name the file by the fingerprint of the
        class. The method also adds a wrapper to the
        name of the file so that when the Pgpier class is looking
        for the public private key pair, it finds the pair it owns.

        Args:
            _wrapper (str): The name of the wrapper

        Returns:
            None
        """
        # lists all files existing in a dir and checks if
        # the file ends with the wrapper
        _path = self.wrk_dir
        _filename = self.fingerprint
        # _wrapper = '(main)'
        _contents = self.passphrase

        file_names = [
            file_wrapper for file_wrapper in os.listdir(_path)
            if os.path.isfile(file_wrapper) and
            file_wrapper.endswith(_wrapper)
            ]
        if file_names != []:
            for f_name in file_names:

                # removes the wrapper
                file_name_len = len(f_name)
                wrapper_len = len(_wrapper)
                file_nowrap = file_name_len - wrapper_len
                clean_f_name = f_name[0:file_nowrap]

                # clean file name
                clean_f = os.path.abspath(os.path.join(_path, clean_f_name))
                # implement so that if the file already
                # exists it would make a copy
                try:
                    # renames the file without the wrapper
                    os.rename(f_name, clean_f)
                except Exception as e:
                    print(e)

        _file = os.path.abspath(os.path.join(_path, '{0}{1}'
                                .format(_filename, _wrapper)))
        with open('{}'.format(_file), 'w') as file_export:
            file_export.write(_contents)

        # Change filemode to 600
        # Only allow the user to access exported passphrase
        os.chmod(_file, stat.S_IRUSR | stat.S_IWUSR)

    def imp_main(self, _wrapper='(main)'):
        """Import pertinent information.

        Method to import the fingerprint and passphrase of the owned
        public private key pair of the
        user. The method also looks for a wrapper on the file to
        distinguish the public private key
        pair the user currently owns.

        Args:
            _wrapper (str): The name of the wrapper

        Returns:
            tuple: String of fingerprint and string of passphrase
            if it finds the public private key pairs
            the user currently owns

            None: If there are no public private key pair the user
            currently owns
        """

        # path to parent directory of gnupg home
        # where Pgpier will operate its own files
        _path = self.wrk_dir
        # _wrapper = '(main)'

        # returns list of files if it ends with the wrapper
        key = [_file for _file in os.listdir(_path)
               if _file.endswith(_wrapper)]

        key_len = len(key)
        if key_len > 1:
            raise Exception("critical error - 0: more than one main"
                            " keys\nreport issue")

        elif key_len == 1:
            _fingerprint = key[0]

            # removes the wrapper
            file_name_len = len(_fingerprint)
            wrapper_len = len(_wrapper)
            file_nowrap = file_name_len - wrapper_len
            clean_fp = _fingerprint[0:file_nowrap]

            fp_file = os.path.abspath(os.path.join(_path, _fingerprint))

            with open('{}'.format(fp_file), '{}'.format('r')) as f:
                _passphrase = f.read()

            if type(_passphrase) != str:
                raise Exception("critical error - 1: error reading for "
                                "passphrase\nreport issue")

            return clean_fp, _passphrase

        else:
            return None

    def set_from_imp(self, wrapper='(main)'):
        """Set object variables from import.

        Method to get the fingerprint and passphrase the user
        currently owns and then assign those values inside
        the class to utilize the user's public private key pair

        Args:
            None

        Returns:
            True: If it retrieved the fingerprint and passphrase from a file
            False: If it did not retrieve anything
        """
        result = None
        try:
            result = self.imp_main(wrapper)
        except Exception as e:
            print(e)

        if result is not None:
            self.set_fingerprint(result[0])
            self.set_passphrase(result[1])

        success = True if result is not None else False
        return success

    def exp_pub_key(self):
        """Method to export the user's public key into ASCII.

        Args:
            None

        Returns:
            str: String of ASCII armored public key
            None: If keyid is not set
        """
        ascii_armored_public_keys = None
        keyid = self.keyid
        gpg = self.gpg

        if keyid is not None:
            ascii_armored_public_keys = gpg.export_keys(keyid)
            return ascii_armored_public_keys
        else:
            return ascii_armored_public_keys

    def imp_pub_key(self, key_data):
        """Import public key.

        Method to import the ASCII public of a user
         into the current user's GnuPG keyring

        Args:
            key_data (str): String of public key armored ASCII

        Returns:
            result (dict): The number of imported keys and the
                           the number of keys not imported
        """
        gpg = self.gpg

        import_result = gpg.import_keys(key_data)

        # Returns the amount of: imported, not imported
        result = {"imported": import_result.imported,
                  "not_imported": import_result.not_imported}
        return result

    def pub_file(self):
        """Method to export the armored ASCII public key into an asc file.

        Args:
            None

        Returns:
            None
        """

        pub_key = self.exp_pub_key()
        fingerprint = self.fingerprint
        path = self.wrk_dir
        # export to parent directory of gnupg home
        pub_file = os.path.abspath(os.path.join(path, fingerprint))
        # checks that the class' public key was exported
        if pub_key is not None:
            with open('{0}{1}'.format(pub_file, '.asc'),
                      '{}'.format('w')) as f:
                f.write(pub_key)

    def sym_encrypt_files(self, symmetric_key, file_path, output,
                          delaf=False, algorithm='AES256', armor=True):
        """Method to encrypt files using a symmetric key.

        Args:
            symmetric_key (str): String of passphrase to be
            used to encrypt the data
            file_path (str): Absolute file path to the files to be encrypted
            output (str): Absolute file path to intended file output
            delaf (bool): True if the files should be deleted after encryption
                          Fasle if the files should be kept after
                          encryption
            algorithm (str): The type of algorithm to be used to encrypt
                             the data
            armor (bool): True for the return type to be in ASCII string
                          False for the return type to be Crypt object

        Returns:
            None
        """
        gpg = self.gpg

        files_dir = []

        files = [f for f in os.listdir(file_path)]

        for f in files:
            files_dir.append('{}'.format(f))

        for x in files_dir:
            with open('{}{}{}'.format(file_path, os.sep, x), '{}'
                      .format('r')) as f:
                contents = f.read()
                gpg.encrypt(contents, symmetric=algorithm,
                            passphrase=symmetric_key, armor=armor,
                            recipients=None, output='{}{}{}'.format(file_path,
                            os.sep, files_dir[files_dir.index(x)]))
                # print("ok: ", crypt.ok)
                # print("status: ", crypt.status)
                # print("stderr: ", crypt.stderr)
            if delaf:
                os.rename('{}{}{}'.format(file_path, os.sep,
                          files_dir[files_dir.index(x)]), '{}{}{}'
                          .format(output, os.sep,
                          files_dir[files_dir.index(x)]))

    def encrypt_data(self, data, recipients):
        """Encrypt data.

        Method to encrypt data using the imported recipient's public
        key from user's GnuPG keyring

        Args:
            data (str): Data to be encrypted
            recipients (int): Fingerprint of recipient

        Returns:
            str: encrypted data in ASCII string
        """
        gpg = self.gpg

        encrypted_ascii_data = gpg.encrypt(data, recipients=recipients)
        # print(encrypted_ascii_data.status)
        ascii_str = str(encrypted_ascii_data)
        return ascii_str

    def sym_decrypt_files(self, symmetric_key, file_path, output, delaf=False):
        """Method to decrypt files using a symmetric key.

        Args:
            symmetric_key (str): String of passphrase to be used
            to decrypt the data
            file_path (str): Absolute file path to the files to be
            encrypted
            output (str): Absolute file path to intended file output
            delaf (bool): True if the files should be deleted after
                          decryption
                          Fasle if the files should be kept after
                          decryption
            algorithm (str): The type of algorithm that was used to
                             encrypt the data
            armor (bool): True for the return type to be in ASCII string
                          False for the return type to be Crypt object

        Returns:
            None
        """
        gpg = self.gpg

        files_dir = []

        files = [f for f in os.listdir(file_path)]

        for f in files:
            files_dir.append('{}'.format(f))

        for x in files_dir:
            with open('{}{}{}'.format(file_path, os.sep, x),
                      '{}'.format('r')) as f:
                crypt = f.read()
                # print(crypt)
                data = gpg.decrypt(crypt, passphrase=symmetric_key)
                de_data = (data.data).decode('utf-8')
                # print('\n\n\n\n--->{}<---\n\n\n'.format(de_data))
                with open('{}{}{}'.format(output, os.sep,
                          files_dir[files_dir.index(x)]),
                          '{}'.format('w')) as decrypted:
                    decrypted.write(de_data)
                # print("ok: ", data.ok)
                # print("status: ", data.status)
                # print("stderr: ", data.stderr)
            if delaf:
                os.remove('{}{}{}'.format(file_path, os.sep, x))

    def decrypt_data(self, data, passphrase):
        """Decrypt data.

        Method to decrypt data using the imported recipient's
        public key from user's GnuPG keyring

        Args:
            data (str): Data in String ASCII to be decrypted
            passphrase (str): Passphrase of the user

        Returns:
            str: Decrypted data into string
        """
        gpg = self.gpg
        passphrase = self.passphrase

        decrypted_data = gpg.decrypt(data, passphrase=passphrase)

        data = (decrypted_data.data).decode('utf-8')
        return data

    def email_to_key(self, email):
        """Email to fingerprint.

        Method to retrieve fingerprint of associated
        email address from the GnuPG keyring

        Args:
            email (str): Email address

        Returns:
            int: Fingerprint that is associated with the email
            address if it is found
            None: If no associated fingerprint is found
        """

        # Gets all available public keys in keyring
        keys = self.list_pub_keys()

        result = None

        for key in keys:  # Go through each public key
            uids = list(filter((lambda item: email in item), key['uids']))
            if uids != []:
                parts = uids[0].split(' ')
                wrapped_email = list(filter((lambda item: '<' in item), parts))
                unwrapped_email = wrapped_email[0].strip('<>')
                if unwrapped_email == email:
                    return key['fingerprint']

        return result

    def trust_key(self, fingerprint, trustlevel='TRUST_ULTIMATE'):
        """Trust public key.

        Method to trust public key that was imported to have the
        ability to encrypt data using
        that public key

        Args:
            fingerprint (int): Fingerprint of pubic key to trust
            trustlevel (str): Trust level to assign to public key

        Returns:
            None
        """
        gpg = self.gpg

        gpg.trust_keys(fingerprint, trustlevel)

    def symmetric_encrypt(self, data, passphrase,
                          algorithm='AES256', armor=True):
        """Symmetric encrypt.

        Method to encrypt data using symmmetric key encryption
        using a passphrase and encryption
        algorithm

        Args:
            data (str): String of data to be encrypted
            passphrase (str): String of passphrase to
            be used to encrypt the data
            algorithm (str): The type of algorithm to
            be used to encrypte the data
            armor (bool): True for the return type to be in ASCII string
                          False for the return type to be Crypt object

        Returns:
            str: ASCII string of encrypted data
        """
        gpg = self.gpg

        crypt = gpg.encrypt(data, symmetric=algorithm, passphrase=passphrase,
                            armor=armor, recipients=None)
        # print(crypt.status)
        return str(crypt)

    def symmetric_decrypt(self, data, passphrase):
        """Method to decrypt data that was encrypted using symmetric encryption.

        Args:
            data (str): Data in ASCII string to be decrypted
            passphrase (str): Passphrase used in the encryption

        Returns:
            str: ASCII string of decrypted data
        """
        gpg = self.gpg

        data = gpg.decrypt(data, passphrase=passphrase)
        # print(data.status)
        return (data.data).decode('utf-8')

    def gen_symm_key(self, stringLength=70):
        password_characters = string.ascii_letters + string.digits\
                              + string.punctuation
        return ''.join(random.choice(password_characters)
                       for i in range(stringLength))

    def del_pub_key(self, fingerprint):
        """Deletes public key from keyring.

        Args:
            fingerprint: Fingerprint of public key to be deleted

        Returns:
            (bool): True if the public key was deleted
                    False if the public key was not deleted
        """

        output = False
        gpg = self.gpg

        # Deletes public key
        result = gpg.delete_keys(fingerprint)

        if str(result) == 'ok':
            output = True

        return output

    def set_email(self):
        """Set email.

        Retrieve email from keyring and set the correponding email address from
        the set fingperprint

        Args:
            None

        Returns:
            None
        """

        # Retrieve gnupg object and set fingerprint
        gpg = self.gpg
        fp = self.fingerprint

        # Lists keys from keyring
        keys = gpg.list_keys()

        for key in keys:
            if key['fingerprint'] == fp:
                # Removes space from uids value and returns the items in a list
                uids = key['uids'][0].split(' ')
                # Gets the email from the items which is
                # wrapped by "<"<email@example.com>">"
                wrapped_email = list(filter((lambda item: '<' in item), uids))
                # Removes "<" and ">" from email
                email = wrapped_email[0].strip('<>')
                self.email_addr = email
