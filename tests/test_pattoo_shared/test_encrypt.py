#!/usr/bin/env python3
"""Test the encrypt module."""

# Standard imports
import unittest
import os
import sys
import shutil
import stat


# Try to create a working PYTHONPATH
EXEC_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(
    os.path.abspath(os.path.join(EXEC_DIR, os.pardir)), os.pardir))
_EXPECTED = '{0}pattoo-shared{0}tests{0}test_pattoo_shared'.format(os.sep)
if EXEC_DIR.endswith(_EXPECTED) is True:
    # We need to prepend the path in case PattooShared has been installed
    # elsewhere on the system using PIP. This could corrupt expected results
    sys.path.insert(0, ROOT_DIR)
else:
    print('''This script is not installed in the "{0}" directory. Please fix.\
'''.format(_EXPECTED))
    sys.exit(2)

# Pattoo imports
import pattoo_shared.encrypt as pgp


class TestEncrypt(unittest.TestCase):
    """Test all methods of Pgpier class.
    """

    @classmethod
    def setUpClass(cls):
        """Class setup.

        Set up for the test class which generates the
        key pairs for twp Pgpier classes. This is done to
        faciliate the testing of the key exchange and
        public key encryption
        """

        # #####################Essential######################
        main_dir = os.path.abspath(
            os.path.join(
                os.getcwd(), '{}'.format('keys')
            )
        )

        cls.main_dir = main_dir
        # ###################################################

        # #####################1st Pgpier######################
        # Create sub directory for 1st Pgpier and change
        # permissions for the directory
        test1 = os.path.join(main_dir, '{}'.format('test1'))
        cls.test1 = test1
        person1 = os.path.join(test1, '{}'.format('.gnupg'))
        os.makedirs(person1)
        os.chmod(person1, stat.S_IRWXU)

        # Create Pgpier class
        gpg1 = pgp.Pgpier(person1)

        # Variables for 1st key pair generation
        # Some variables are saved in the class to
        # be accessed later.
        wrapper1 = '(Person1)'
        cls.wrapper1 = wrapper1
        person1_name = 'John Brown'
        person1_email = 'john_brown_2020_test@gmail.com'
        cls.person1_email = person1_email
        person1_comment = 'Unit testing with person1'

        # Checks if a passphrase has been exported already
        result1 = gpg1.set_from_imp(wrapper1)

        # If passphrase has not been export, a new key pair will be generated
        if not result1:
            gpg1.key_pair(person1_email, person1_name, person1_comment)
            gpg1.exp_main(wrapper1)
            cls.gpg1 = gpg1

        ####################################################

        # #####################2nd Pgpier######################
        # Create sub directory for 2nd Pgpier and change
        # permissions for the directory
        test2 = os.path.join(main_dir, '{}'.format('test2'))
        cls.test2 = test2
        person2 = os.path.join(test2, '{}'.format('.gnupg'))
        os.makedirs(person2)
        os.chmod(person2, stat.S_IRWXU)

        # Create Pgpier class
        gpg2 = pgp.Pgpier(person2)

        # Variables for 2nd key pair generation
        # Some variables are saved in the class to
        # be accessed later.
        wrapper2 = '(Person2)'
        cls.wrapper2 = wrapper2
        person2_name = 'Mary Jane'
        person2_email = 'mary_jane_2020_test@gmail.com'
        cls.person2_email = person2_email
        person2_comment = 'Unit testing with person2'

        # Checks if a passphrase has been exported already
        result2 = gpg2.set_from_imp(wrapper2)

        # If passphrase has not been export, a new key pair will be generated
        if not result2:
            gpg2.key_pair(person2_email, person2_name, person2_comment)
            gpg2.exp_main(wrapper2)
            cls.gpg2 = gpg2
        ####################################################

    @classmethod
    def tearDownClass(cls):
        """Class teardown.

        This will remove all test data by deleting the main
        generated directory
        """

        shutil.rmtree(cls.main_dir)

    def setUp(self):
        """This will run each time before a test is performed.
        """

        # Retrieves Pgpier object for each test Pgpier class
        self.gpg1 = self.__class__.gpg1
        self.gpg2 = self.__class__.gpg2

        # Retrieves directory for each test Pgpier class
        self.test1_dir = self.__class__.test1
        self.test2_dir = self.__class__.test2

        # Retrieves wrappers used to store passphrase for
        # each Pgpier class
        self.wrapper1 = self.__class__.wrapper1
        self.wrapper2 = self.__class__.wrapper2

        # Retrieves test email addresses of each Pgpier
        self.email_1 = self.__class__.person1_email
        self.email_2 = self.__class__.person2_email

    def tearDown(self):
        """This is performed after each test run.
        """

    def test_key_generation(self):
        """Checks if both Pgpier instances generated their key pairs.
        """

        # Gives initial False value
        # When unchanged, the test will fail
        key_gen1 = False
        key_gen2 = False

        # If a fingerprint was generated, a string value would be
        # assigned. If not, it would be an empty string
        if self.gpg1.fingerprint != '':
            key_gen1 = True

        if self.gpg2.fingerprint != '':
            key_gen2 = True

        # Retrieves public keys stored in each Pgpier object
        keys1 = self.gpg1.list_pub_keys()
        keys2 = self.gpg2.list_pub_keys()

        # Used to check if the keys were generated from the test
        # values assigned in the class set up
        person1_key = False
        person2_key = False

        # Checks if there are any public keys before searching
        if keys1 != []:
            for key in keys1:
                if key['uids'] == ['John Brown (Unit testing '
                                   'with person1) <john_brown'
                                   '_2020_test@gmail.com>']:
                    person1_key = True

        if keys2 != []:
            for key in keys2:
                if key['uids'] == ['Mary Jane (Unit testing '
                                   'with person2) <mary_jane'
                                   '_2020_test@gmail.com>']:
                    person2_key = True

        # Checks if the keys were generated from the specific
        # test values used in the class set up
        self.assertTrue(person1_key)
        self.assertTrue(person2_key)

        # Checks if any key pairs were generated at all
        self.assertTrue(key_gen1)
        self.assertTrue(key_gen2)

    def test_set_passphrase(self):
        """Test if set passphrase method works.
        """

        # Retrieves already set passphrases
        prev_passphrase1 = self.gpg1.passphrase
        prev_passphrase2 = self.gpg2.passphrase

        # Values to be used for next passphrase
        next_passphrase1 = 'password-123'
        next_passphrase2 = 'password-abc'

        # Assignment of new passphrases
        self.gpg1.set_passphrase(next_passphrase1)
        self.gpg2.set_passphrase(next_passphrase2)

        # Retrieves set passphrase from Pgpier objects
        set_passphrase1 = self.gpg1.passphrase
        set_passphrase2 = self.gpg2.passphrase

        # Checks if new passphrases were assigned
        self.assertEqual(set_passphrase1, next_passphrase1)
        self.assertEqual(set_passphrase2, next_passphrase2)

        # Resets to previous passphrases and check it they
        # were changed back
        self.gpg1.set_passphrase(prev_passphrase1)
        self.gpg2.set_passphrase(prev_passphrase2)

        set_passphrase1 = self.gpg1.passphrase
        set_passphrase2 = self.gpg2.passphrase

        self.assertEqual(set_passphrase1, prev_passphrase1)
        self.assertEqual(set_passphrase2, prev_passphrase2)

    def test_set_keyid(self):
        """Checks if set key ID methods works."""

        # Sets key ID's for each Pgpier object
        self.gpg1.set_keyid()
        self.gpg2.set_keyid()

        keyid1 = self.gpg1.keyid
        keyid2 = self.gpg2.keyid

        # Checks that the key ID's are not empty
        self.assertIsNotNone(keyid1)
        self.assertIsNotNone(keyid2)

    def test_list_pub_keys(self):
        """Test that public keys are listed
        """

        # List all public keys
        keys_lst1 = self.gpg1.list_pub_keys()
        keys_lst2 = self.gpg2.list_pub_keys()

        # Used to check that the lists are not empty
        is_keys_lst1 = False
        is_keys_lst2 = False

        if keys_lst1 != []:
            is_keys_lst1 = True

        if keys_lst2 != []:
            is_keys_lst2 = True

        # If the lists are not empty, the test will pass
        self.assertTrue(is_keys_lst1)
        self.assertTrue(is_keys_lst2)

    def test_exp_main(self):
        """Export main test.

        Checks that the file used to store the passphrase
        of the main public private key pair is created
        """

        # Used to determine if the test passes
        pass_result1 = False
        pass_result2 = False

        # New wrappers to export new files of Pgpier
        # objects that already have a key pair
        wrapper1 = '(ExportTest_1)'
        wrapper2 = '(ExportTest_2)'

        # Retrieves fingerprint which is the first part
        # of the exported file name and, the passphrase
        # which will be stored inside the files
        fingerprint1 = self.gpg1.fingerprint
        fingerprint2 = self.gpg2.fingerprint
        passphrase1 = self.gpg1.passphrase
        passphrase2 = self.gpg2.passphrase

        # Export the information
        self.gpg1.exp_main(wrapper1)
        self.gpg2.exp_main(wrapper2)

        # Checks that the files in the current directory has the
        # fingerprints and checks if the wrappers are also at the
        # end of the file and stores the results in a list
        files1 = [f for f in os.listdir(self.test1_dir)
                  if f.endswith(wrapper1) and fingerprint1 in f]
        files2 = [f for f in os.listdir(self.test2_dir)
                  if f.endswith(wrapper2) and fingerprint2 in f]

        # Checks that the files were found
        if files1 != [] and files2 != []:

            # Opens and checks contents of the files
            with open('{}{}{}'.format(self.test1_dir, os.sep, files1[0]),
                      '{}'.format('r')) as f1:
                contents1 = f1.read()
                if contents1 == passphrase1:
                    # Assigns passing value if intended contents were stored
                    pass_result1 = True

            with open('{}{}{}'.format(self.test2_dir, os.sep, files2[0]),
                      '{}'.format('r')) as f2:
                contents2 = f2.read()
                if contents2 == passphrase2:
                    pass_result2 = True

        # Passes if the passing values were assigned
        self.assertTrue(pass_result1)
        self.assertTrue(pass_result2)

    def test_set_from_imp(self):
        """Tests if the setter for the export file work.
        """
        result1 = self.gpg1.set_from_imp(self.wrapper1)
        result2 = self.gpg2.set_from_imp(self.wrapper2)

        # The results will be true if the export files were found
        self.assertTrue(result1)
        self.assertTrue(result2)

    def test_exp_pub_key(self):
        """Export public key test.

        Tests that the main public key of the Pgpier
        class is exported
        """

        # Sets key ID used to export public keys
        self.gpg1.set_keyid()
        self.gpg2.set_keyid()

        # Exports public keys
        pub_key1 = self.gpg1.exp_pub_key()
        pub_key2 = self.gpg2.exp_pub_key()

        # Test passes if the outputs are not None
        self.assertIsNotNone(pub_key1)
        self.assertIsNotNone(pub_key2)

    def test_imp_pub_key(self):
        """Tests that the importation of public keys work.
        """

        # Sets key ID's used to export public keys
        self.gpg1.set_keyid()
        self.gpg2.set_keyid()

        keys_lst1 = self.gpg1.list_pub_keys()
        keys_lst2 = self.gpg2.list_pub_keys()

        # Export public keys
        pub_key1 = self.gpg1.exp_pub_key()
        pub_key2 = self.gpg2.exp_pub_key()

        # Import public keys
        result_1 = self.gpg1.imp_pub_key(pub_key2)
        result_2 = self.gpg2.imp_pub_key(pub_key1)

        # Retrieves new list of public keys
        keys_lst1 = self.gpg1.list_pub_keys()
        keys_lst2 = self.gpg2.list_pub_keys()

        # Checks that each Pgpier object retrieve the other's
        # public key
        self.assertEqual(len(keys_lst1), 2)
        self.assertEqual(len(keys_lst2), 2)

    def test_email_to_key(self):
        """Email to fingerprint test.

        Test if the fingerprint is retrieved for a public key
        that has an assigned email address"""

        # Retrieves email addresses from class set up
        email1 = self.__class__.person1_email
        email2 = self.__class__.person2_email

        # Retrieves fingerprints from email addresses
        fp1 = self.gpg1.email_to_key(email1)
        fp2 = self.gpg2.email_to_key(email2)

        self.assertIsNotNone(fp1)
        self.assertIsNotNone(fp2)

    def test_encrypt_decrypt_data(self):
        """Test both public key encryption and decryption.
        """

        original_data = 'HELLO WORLD!'

        # Set key id's
        self.gpg1.set_keyid()
        self.gpg2.set_keyid()

        # Export public key to ASCII string
        pub_key1 = self.gpg1.exp_pub_key()
        pub_key2 = self.gpg2.exp_pub_key()

        # Import public key
        self.gpg1.imp_pub_key(pub_key2)  # Trade
        self.gpg2.imp_pub_key(pub_key1)  # Trade

        # Get email from class setup
        email1 = self.__class__.person1_email
        email2 = self.__class__.person2_email

        # Get fingerprint from email address
        fp1 = self.gpg1.email_to_key(email1)
        fp2 = self.gpg2.email_to_key(email2)

        # Both keys have to be trusted before data can be encrypted using an
        # imported public key

        # Trust public keys so that encryption and decryption can happen
        self.gpg1.trust_key(fp2)  # Trade
        self.gpg2.trust_key(fp1)  # Trade

        # Encrypt data from 1st Pgpier using 2nd Pgpier's public key
        encrypted_data = self.gpg1.encrypt_data(original_data, fp2)

        # Decrypt data using 2nd Pgpier's passphrase to access the keyring
        passphrase2 = self.gpg2.passphrase
        decrypted_data = self.gpg2.decrypt_data(encrypted_data, passphrase2)

        # Checks that the decrypted data is the same as the original
        self.assertEqual(original_data, decrypted_data)

    def test_gen_symm_key(self):
        """Generate symmetric key test.

        Checks the default length of random string
        generation"""

        string1 = self.gpg1.gen_symm_key()
        # string2 = self.gpg2.gen_symm_key()

        # Checks that the length of the generated data is the same
        # as the default and that the data is a string
        self.assertEqual(len(string1), 70)
        self.assertEqual(type(string1), str)

    def test_symmetric_encrypt_decrypt(self):
        """Tests both symmetric encryption and decryption.
        """

        original_data = 'HELLO WORLD!'

        # Generates random symmetric key
        password = self.gpg1.gen_symm_key()

        # Encrypts data
        encrypted_data = self.gpg1.symmetric_encrypt(original_data, password)

        # Decrypts data
        decrypted_data = self.gpg2.symmetric_decrypt(encrypted_data, password)

        self.assertEqual(original_data, decrypted_data)

    def test_set_email(self):
        """Set email test.

        Tests that the email address in the Pgpier class is
        set from the key pair"""

        # Sets email addresses
        self.gpg1.set_email()
        self.gpg2.set_email()

        # Retrieves email addresses in Pgpier objects
        set_email1 = self.gpg1.email_addr
        set_email2 = self.gpg2.email_addr

        # Checks that the assigned emails from the class set up
        # is the same as the ones stored in the Pgpier classes
        self.assertEqual(self.email_1, set_email1)
        self.assertEqual(self.email_2, set_email2)


if __name__ == '__main__':
    unittest.main()
