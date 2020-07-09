"""Methods for configuring pattoo components"""
# Standard imports
import sys
import os
import getpass
import grp
import pwd
import shutil

from pathlib import Path

# Import project libraries
from pattoo_shared import files
import shared

def create_user(user_name, directory, shell):
    """Create user and their respective group.

    Args:
        user_name: The name and group of the user being created
        directory: The home directory of the user
        shell: The shell of the user

    Returns:
        None
    """
    # If the group specified does not exist, it gets created
    if not group_exists(user_name):
        shared._run_script('groupadd {0}'.format(user_name))
    # If the user specified does not exist, they get created
    if not user_exists(user_name):
        shared._run_script(
            'useradd -d {1} -s {2} -g {0} {0}'.format(
                user_name, directory, shell))


def group_exists(group_name):
    """Check if the group already exists.

    Args:
        group_name: The name of the group

    Returns
        True if the group exists and False if it does not
    """
    try:
        # Gets group name
        grp.getgrnam(group_name)
        return True
    except KeyError:
        return False


def user_exists(user_name):
    """Check if the user already exists.

    Args:
        user_name: The name of the user

    Returns
        True if the user exists and False if it does not

    """
    try:
        # Gets user name
        pwd.getpwnam(user_name)
        return True
    except KeyError:
        return False


def initialize_ownership(user, group,  dir_path):
    """Recursively change the ownership of the directory.

    Args:
        user: The name of the user
        group: The name of the group
        dir_name: The name of the directory

    Returns:
        None
    """
    # Set ownership of file specified at dir_path
    shared._run_script('chown -R {0}:{1} {2}'.format(user, group, dir_path))
