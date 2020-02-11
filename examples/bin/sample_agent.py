#!/usr/bin/env python3

# Import from the PattooShared library
from pattoo_shared.constants import DATA_FLOAT
from pattoo_shared.phttp import PostAgent
from pattoo_shared.variables import (
    DataPoint, DataPointMetadata, TargetDataPoints, AgentPolledData)


def main():
    """Post data to pattoo server.

    Args:
        None

    Returns:
        None

    """
    '''
    NOTE:

    Scripts must be run at regular intervals and the polling_interval
    should be automatically provided to the main() function.

    Notes about CRON:
    When using cron, change this value to match the cron interval in seconds.
    It is not advised to use cron for polling unless you know the interval
    will not change. If using cron, remember to make the polling interval to
    match the cron interval in 'seconds'.

    Ideally your agents should run as daemons, not as cron jobs. See the daemon
    example script which explains how to do this.
    '''

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

    '''
    NOTE:

    The AgentPolledData object contains unique identification information
    that the pattoo server will use to differentiate the information source.
    This includes: the hostname of the system on which the object was created,
    a unique hashed identifier stored in the cache directory of the agent
    configuration.

    You just need to write an agent to do one thing well, such data collection
    from a type of target source. For example, you don't need to give each
    agent that does the same thing a different "agent_name".  Just make sure
    that different types of agents have different "agent_name" values.

    The PattooShared library will take care of the rest.
    '''

    # Setup the agent's AgentPolledData object.
    agent = AgentPolledData(agent_name, polling_interval)

    '''
    NOTE:

    Metadata is normally expected to stay constant. If it changes then the
    datapoint ID changes and you'll start plotting a brand new chart on the
    pattoo server. The old chart will stop at the time the metadata changed.

    In some cases, you may not want changing metadata to cause a brand new
    plot. For example, your metadata for computer resource charting may include
    the operating system version. This is useful background information, but
    shouldn't impact charting if it changes. This type of metadata should be
    dynamic.

    '''
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

        '''
        NOTE:

        You don't have to specify the time when the data was collected.
        The DataPoint object captures that information automatically. You can
        also specify it using the timestamp= argument. See the class
        documentation for details.

        The default data_type is DATA_INT (integer). Read the documentation
        for the various other data which cover float and counter values.
        '''
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

    # Post the data to pattoo
    post = PostAgent(agent)
    post.post()


if __name__ == "__main__":
    main()
