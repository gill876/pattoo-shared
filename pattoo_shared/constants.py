"""Module that defines constants shared between pattoo and its agents.

The aim is to have a single location for constants that may be used across
agents to prevent the risk of duplication.

"""
import collections

###############################################################################
# Universal constants for all agents
###############################################################################

DATA_FLOAT = 1
DATA_INT = 0
DATA_COUNT64 = 64
DATA_COUNT = 32
DATA_STRING = 2
DATA_NONE = None

###############################################################################
# Constants for data DB ingestion
###############################################################################

PattooDBrecord = collections.namedtuple(
        'PattooDBrecord', '''\
agent_id agent_program agent_hostname timestamp polling_interval gateway \
device device_type data_label data_index value data_type checksum''')

###############################################################################
# Constants for pattoo Agent API
###############################################################################

PATTOO_API_SITE_PREFIX = '/pattoo/api/v1'
PATTOO_API_AGENT_PREFIX = '{}/agent'.format(PATTOO_API_SITE_PREFIX)
PATTOO_API_AGENT_EXECUTABLE = 'pattoo-api-agentd'
PATTOO_API_AGENT_PROXY = '{}-gunicorn'.format(
    PATTOO_API_AGENT_EXECUTABLE)

###############################################################################
# Constants for standard agents
###############################################################################

# pattoo-agent-os constants
PATTOO_AGENT_OS_SPOKED_API_PREFIX = '/pattoo-agent-os'
PATTOO_AGENT_OS_SPOKED = 'pattoo-agent-os-spoked'
PATTOO_AGENT_OS_SPOKED_PROXY = '{}-gunicorn'.format(PATTOO_AGENT_OS_SPOKED)
PATTOO_AGENT_OS_AUTONOMOUSD = 'pattoo-agent-os-autonomousd'
PATTOO_AGENT_OS_HUBD = 'pattoo-agent-os-hubd'

# pattoo-snmp constants
PATTOO_AGENT_SNMPD = 'pattoo-agent-snmpd'

# pattoo-modbus-tcp constants
PATTOO_AGENT_MODBUSTCPD = 'pattoo-agent-modbustcpd'

# pattoo-modbus-tcp constants
PATTOO_AGENT_BACNETIPD = 'pattoo-agent-bacnetipd'
