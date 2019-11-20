"""Module that defines constants shared between pattoo and its agents.

The aim is to have a single location for constants that may be used across
agents to prevent the risk of duplication.

"""
import collections

###############################################################################
# Universal constants for all agents
###############################################################################

DATA_FLOAT = 101
DATA_INT = 99
DATA_COUNT64 = 64
DATA_COUNT = 32
DATA_STRING = 2
DATA_NONE = None

###############################################################################
# Constants for data DB ingestion
###############################################################################

MAX_KEYPAIR_LENGTH = 512

PattooDBrecord = collections.namedtuple(
    'PattooDBrecord', '''\
timestamp value checksum data_type key source metadata''')

###############################################################################
# Constants for pattoo Agent API
###############################################################################

PATTOO_API_SITE_PREFIX = '/pattoo/api/v1'
PATTOO_API_AGENT_PREFIX = '{}/agent'.format(PATTOO_API_SITE_PREFIX)
PATTOO_API_AGENT_EXECUTABLE = 'pattoo-api-agentd'
PATTOO_API_AGENT_PROXY = '{}-gunicorn'.format(
    PATTOO_API_AGENT_EXECUTABLE)
