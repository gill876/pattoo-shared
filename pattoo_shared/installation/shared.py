"""Shared functions and methods utilized by the pattoo installation."""
# Standard imports
import sys
import os
import subprocess
import traceback
import shutil
import getpass


def run_script(cli_string, die=True, verbose=True):
    """Run the cli_string UNIX CLI command and record output.

    Args:
        cli_string: String of command to run
        die: Exit with error if True

    Returns:
        (returncode, stdoutdata, stderrdata):
            Execution code, STDOUT output and STDERR output.

    """
    # Initialize key variables
    messages = []
    stdoutdata = ''.encode()
    stderrdata = ''.encode()
    returncode = 1

    # Enable verbose mode if True
    if verbose is True:
        print('Running Command: "{}"'.format(cli_string))

    # Run update_targets script
    do_command_list = cli_string.split()

    # Create the subprocess object
    try:
        process = subprocess.Popen(
            do_command_list,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdoutdata, stderrdata = process.communicate()
        returncode = process.returncode
    except:
        (exc_type, exc_value, exc_traceback) = sys.exc_info()
        messages.append('''\
Bug: Exception Type:{}, Exception Instance: {}, Stack Trace Object: {}]\
    '''.format(exc_type, exc_value, exc_traceback))
        messages.append(traceback.format_exc())

    # Crash if the return code is not 0
    if bool(returncode) is True:
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
        if verbose is True:
            print('messages: {}'.format(messages))
        if bool(messages) is True:
            for log_message in messages:
                if verbose is True:
                    print(log_message)

            if bool(die) is True:
                # All done
                sys.exit(2)

    # Return
    return (returncode, stdoutdata, stderrdata)


def log(message):
    """Log messages and exit abnormally.

    Args:
        message: Message to print

    Returns:
        None

    """
    # exit
    print('\nPATTOO Error: {}'.format(message))
    sys.exit(3)


def chown(directory):
    """Recursively change the ownership of files in a directory.

    The directory must have the string '/pattoo/' in it

    Args:
        directory: Directory to create

    Returns:
        None

    """
    # Initialize key variables
    username = 'pattoo'
    group = 'pattoo'

    if getpass.getuser() != 'root':
        log('''\
Current user is not root, please execute script as root to continue''')

    # Change ownership
    if '{}pattoo'.format(os.sep) in directory:
        # Change the parent directory
        shutil.chown(directory, user=username, group=group)

        # Recursively change the sub-directories and files
        for root, dirs, files_ in os.walk(directory):
            for dir_ in dirs:
                shutil.chown(
                    os.path.join(root, dir_), user=username, group=group)
            for file_ in files_:
                shutil.chown(
                    os.path.join(root, file_), user=username, group=group)
