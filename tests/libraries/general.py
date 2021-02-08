"""Module of general functions."""

# Standard imports
import random
import hashlib

# Import from the PattooShared library
from pattoo_shared.constants import DATA_FLOAT
from pattoo_shared.variables import (
    DataPoint, DataPointMetadata, TargetDataPoints, AgentPolledData)


def random_agent_name():
    """Creates random agent name.

    Args:
        None

    Return:
        result: Agent name

    """
    salt = str(random.getrandbits(128))
    result = hashlib.sha224(salt.encode()).hexdigest()
    return result


def test_agent():
    # Define the polling interval in seconds (integer).
    polling_interval = 300

    # Give the agent a name
    agent_name = 'sample_agent_script'

    # Let's assume the script has already received this data from SITE_A
    site_a_data = [
        ['ABC', 123.456],
        ['DEF', 456.789]
    ]

    # Let's assume the script has already received this data from WORK_1
    work_1_data = [
        ['GHI', 654.321],
        ['JKL', 987.654]
    ]

    # Setup the agent's AgentPolledData object.
    agent = AgentPolledData(agent_name, polling_interval)

    # Let's add some metadata that you don't want to affect charting in the
    # event of a change. Department names change all the time.
    metadata_static = DataPointMetadata(
        'Department Name', 'The Palisadoes Foundation', update_checksum=False)

    # Let's add some metadata that will change and trigger a new chart.
    metadata_dynamic = DataPointMetadata('Financial Year', '2020')

    # Create target objects for SITE_A
    target = TargetDataPoints('SITE_A')
    for quote in site_a_data:
        key, value = quote
        datapoint = DataPoint(key, value, data_type=DATA_FLOAT)
        datapoint.add(metadata_static)
        datapoint.add(metadata_dynamic)
        target.add(datapoint)
    agent.add(target)

    # Create target objects for WORK_1
    target = TargetDataPoints('WORK_1')
    for quote in work_1_data:
        key, value = quote
        datapoint = DataPoint(key, value, data_type=DATA_FLOAT)
        datapoint.add(metadata_static)
        datapoint.add(metadata_dynamic)
        target.add(datapoint)
    agent.add(target)

    # Return agent
    return agent
