#!/usr/bin/env python3

# Standard importations
from time import sleep, time

# Import from the PattooShared library
from pattoo_shared.agent import Agent, AgentCLI
from pattoo_shared.constants import DATA_FLOAT
from pattoo_shared.phttp import PostAgent
from pattoo_shared.variables import (
    DataPoint, TargetDataPoints, AgentPolledData)


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
        polling_interval = 20

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
        polling_interval: Polling interval

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

    # Setup AgentPolledData
    agent = AgentPolledData(agent_name, polling_interval)

    # Create target objects for SITE_A
    target = TargetDataPoints('SITE_A')
    for quote in site_a_data:
        key, value = quote
        target.add(DataPoint(key, value, data_type=DATA_FLOAT))
    agent.add(target)

    # Create target objects for WORK_1
    target = TargetDataPoints('WORK_1')
    for quote in work_1_data:
        key, value = quote
        target.add(DataPoint(key, value, data_type=DATA_FLOAT))
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
