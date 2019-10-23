"""Module that defines universal constants.

The aim is to have a single location for constants that may be used across
agents to prevent the risk of duplication.

"""

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
# Constants for pattoo API
###############################################################################

PATTOO_API_SITE_PREFIX = '/pattoo'
PATTOO_API_AGENT_PREFIX = '{}/agent'.format(PATTOO_API_SITE_PREFIX)
PATTOO_API_AGENT_EXECUTABLE = 'pattoo-api-agentd'
PATTOO_API_AGENT_GUNICORN_AGENT = '{}-gunicorn'.format(
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
