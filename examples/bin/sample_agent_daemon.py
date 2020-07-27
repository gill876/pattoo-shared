#!/usr/bin/env python3

# Standard importations
from time import sleep, time

# Import from the PattooShared library
from pattoo_shared.agent import Agent, AgentCLI
from pattoo_shared.constants import DATA_FLOAT
from pattoo_shared.phttp import PostAgent
from pattoo_shared.variables import (
    DataPoint, DataPointMetadata, TargetDataPoints, AgentPolledData)


class PollingAgent(Agent):
    """Agent that gathers data."""

    def __init__(self, parent):
        """Initialize the class.

        Args:
            parent: Name of parent program

        Returns:
            None

        """
        # Initialize key variables
        Agent.__init__(self, parent)
        self._agent_name = parent

    def query(self):
        """Query all remote targets for data.

        Args:
            None

        Returns:
            None

        """
        # Initialize key variables
        polling_interval = 300

        # Post data to the remote server
        while True:
            # Get start time
            ts_start = time()

            poller(self._agent_name, polling_interval)

            # Sleep
            duration = time() - ts_start
            sleep(abs(polling_interval - duration))


def poller(agent_name, polling_interval):
    """Post data to pattoo server.

    Args:
        agent_name: Name of agent
        polling_interval: Polling interval in seconds

    Returns:
        None

    """
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

    # Setup AgentPolledData
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


def main():
    """Start the pattoo agent.

    Args:
        None

    Returns:
        None

    """
    # Poll
    agent_program_name = 'sample_agent_daemon'
    agent_poller = PollingAgent(agent_program_name)

    # Do control
    cli = AgentCLI()
    cli.control(agent_poller)


if __name__ == "__main__":
    main()
