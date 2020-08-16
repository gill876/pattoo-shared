#!/usr/bin/env python3
"""Creates test environment for daemon to start"""

# Standard imports
import os
import sys
import argparse

# Try to create a working PYTHONPATH
DEV_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(
    os.path.abspath(os.path.join(DEV_DIR, os.pardir)), os.pardir))
_EXPECTED = '{0}pattoo-shared{0}tests{0}bin'.format(os.sep)
if DEV_DIR.endswith(_EXPECTED) is True:
    sys.path.insert(0, ROOT_DIR)
else:
    print('''This script is not installed in the "{0}" directory. Please fix.\
'''.format(_EXPECTED))
    sys.exit(2)

# Pattoo imports
from pattoo_shared.daemon import Daemon
from pattoo_shared.agent import Agent
from pattoo_shared.configuration import Config

from tests.test_pattoo_shared.test_daemon import MockDaemon


def main():
    """Test all the pattoo-shared modules with unittests.

    Args:
        None

    Returns:
        None

    """
    # Initialize key variables
    config = Config()

    # Set up parser
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', help='Start daemon', action='store_true')
    parser.add_argument('--stop', help='Start daemon', action='store_true')
    parser.add_argument('--restart', help='Start daemon', action='store_true')
    parser.add_argument('--status', help='Daemon status', action='store_true')
    parser.add_argument(
        '--agent_name', help='Agent name', type=str, required=True)
    args = parser.parse_args()

    # Daemon manipulation
    agent_ = Agent(args.agent_name, config=config)
    daemon = MockDaemon(agent_)
    if bool(args.start):
        daemon.start()
    elif bool(args.stop):
        daemon.stop()
    elif bool(args.restart):
        daemon.restart()
    elif bool(args.status):
        daemon.status()
    else:
        print('No command matches')


if __name__ == '__main__':
    main()
