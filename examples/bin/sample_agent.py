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
    # Define the polling interval in seconds (integer).
    # Scripts must be run at regular intervals and the polling_interval
    # should be automatically provided to the main() function.
    #
    # Notes about CRON:
    # When using cron, change this value to match the cron interval in seconds.
    # It is not advised to use cron for polling unless you know the interval
    # will not change. If using cron, remember to make the polling interval to
    # match the cron interval in 'seconds'.
    polling_interval = 20

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
    agent = AgentPolledData('LAVA_SCRIPT', polling_interval)

    # Let's add some metadata that is unlikely to change
    metadata_static = DataPointMetadata(
        'Company Name', 'The Palisadoes Foundation', update_checksum=False)

    # Let's add some metadata that will change
    metadata_dynamic = DataPointMetadata(
        'Financial Year', '2020')

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

    # Post the data to pattoo
    post = PostAgent(agent)
    post.post()


if __name__ == "__main__":
    main()
