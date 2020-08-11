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

# Groupings of reserved keys
DATAPOINT_KEYS = (
    'pattoo_checksum', 'pattoo_metadata', 'pattoo_data_type', 'pattoo_key',
    'pattoo_value', 'pattoo_timestamp'
)

# Metadata keys added to datapoints by agents
AGENT_METADATA_KEYS = (
    'pattoo_agent_id', 'pattoo_agent_polled_target', 'pattoo_agent_program',
    'pattoo_agent_hostname', 'pattoo_agent_polling_interval')

# Create reserved keys
_ = list(DATAPOINT_KEYS)
_.extend(AGENT_METADATA_KEYS)
RESERVED_KEYS = tuple(_)

PattooDBrecord = collections.namedtuple(
    'PattooDBrecord', ' '.join(RESERVED_KEYS))

# Keys of posted cached data. Based on keys in
# pattoo_shared.constants.PostingDataPoints
CACHE_KEYS = (
    'pattoo_agent_id', 'pattoo_datapoints', 'pattoo_agent_polling_interval',
    'pattoo_agent_timestamp')

###############################################################################
# Constants for pattoo Agent API
###############################################################################

_PATTOO = '/pattoo'
PATTOO_WEB_SITE_PREFIX = '{}'.format(_PATTOO)
PATTOO_API_SITE_PREFIX = '{}/api/v1'.format(_PATTOO)
PATTOO_API_AGENT_PREFIX = '{}/agent'.format(PATTOO_API_SITE_PREFIX)
PATTOO_API_WEB_PREFIX = '{}/web'.format(PATTOO_API_SITE_PREFIX)
