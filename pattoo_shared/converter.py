#!/usr/bin/env python3
"""Pattoo Data Converter."""

# Pattoo libraries
from .variables import (
    DataPointMeta, DataPoint, AgentPolledData)
from .constants import (
    DATA_FLOAT, DATA_INT, DATA_COUNT64, DATA_COUNT, DATA_STRING, DATA_NONE,
    MAX_KEYPAIR_LENGTH, PattooDBrecord)
from pattoo_shared import data


def cache_to_keypairs(data_source, items):
    """Convert agent cache data to AgentPolledData object.

    Args:
        items: Cache data
        data_source: Source of the cache data

    Returns:
        result: Validated cache data. [] if invalid.

    """
    # Initialize key variables
    result = []

    # Verify we are getting a list
    if isinstance(items, list) is False:
        return []

    # Verify contents of lists
    for item in items:
        # Initialize data
        valids = []
        keypairs = []

        # Verify dicts are in the list
        if isinstance(item, dict) is False:
            continue

        # Get all the key-pairs for the item
        keypairs = []
        for key, value in sorted(item.items()):
            # All the right keys
            keys = ['checksum', 'metadata', 'data_type', 'data_label',
                    'data_index', 'data_value', 'data_timestamp']
            valids.append(key in keys)
            valids.append(len(item) == len(keys))
            valids.append(isinstance(key, str))

            # Work on metadata
            if key == 'metadata':
                # Must be a dict
                if isinstance(value, list) is False:
                    valids.append(False)
                    continue

                # Add metadata keypairs as a list of tuples
                for keypair in value:
                    if isinstance(keypair, dict) is False:
                        continue
                    for m_key, m_value in keypair.items():
                        if isinstance(m_key, str) is False:
                            continue
                        if isinstance(m_value, str) is False:
                            continue
                        keypairs.append(
                            (str(m_key)[:MAX_KEYPAIR_LENGTH], str(
                                m_value)[:MAX_KEYPAIR_LENGTH])
                        )

            # Work on the data_type
            if key == 'data_type':
                valids.append(value in [
                    DATA_FLOAT, DATA_INT, DATA_COUNT64, DATA_COUNT,
                    DATA_STRING, DATA_NONE])

        # Append to result
        if False not in valids:
            # Add the datasource to the original checksum for better uniqueness
            checksum = data.hashstring(
                '{}{}'.format(data_source, item['checksum']), sha=512)
            pattoo_db_variable = PattooDBrecord(
                checksum=checksum,
                data_index=item['data_index'],
                data_label=item['data_label'],
                data_source=data_source,
                data_timestamp=item['data_timestamp'],
                data_type=item['data_type'],
                data_value=item['data_value'],
                metadata=keypairs
            )
            result.append(pattoo_db_variable)

    # Return
    return result


def agentdata_to_datapoints(agentdata):
    """Ingest data.

    Args:
        agentdata: AgentPolledData object

    Returns:
        rows: List of DataPoint objects

    """
    # Initialize key variables
    rows = []

    # Only process valid data
    if isinstance(agentdata, AgentPolledData) is True:
        # Return if invalid data
        if bool(agentdata.valid) is False:
            return []

        # Cycle through the data
        for gwd in agentdata.data:
            # Ignore bad data
            if gwd.valid is False:
                continue

            for ddv in gwd.data:
                # Ignore bad data
                if ddv.valid is False:
                    continue

                # Get data
                for _dv in ddv.data:
                    # Assign values to DataPoints
                    metadata = {
                        'agent_id': agentdata.agent_id,
                        'agent_program': agentdata.agent_program,
                        'agent_hostname': agentdata.agent_hostname,
                        'polling_interval': agentdata.polling_interval,
                        'gateway': gwd.device,
                        'device': ddv.device,
                        'device_type': ddv.device_type
                    }
                    for key, value in metadata.items():
                        _dv.add(DataPointMeta(key, value))
                    rows.append(_dv)

    # Return
    return rows


def datapoints_to_dicts(items):
    """Ingest data.

    Args:
        items: List of datapoints to convert

    Returns:
        result: List of datapoints converted to a list of dicts

    """
    # Initialize key variables
    datapoints = []
    result = []

    # Verify input data
    if isinstance(items, list) is False:
        items = [items]
    for item in items:
        if isinstance(item, DataPoint):
            datapoints.append(item)

    # Convert to a list of dicts
    for datapoint in datapoints:
        # Only convert valid data
        if datapoint.valid is True:
            data_dict = {
                'metadata': [
                    {str(key): str(value)} for key, value in sorted(
                        datapoint.metadata.items())],
                'data_label': datapoint.data_label,
                'data_type': datapoint.data_type,
                'data_index': datapoint.data_index,
                'data_value': datapoint.data_value,
                'data_timestamp': datapoint.data_timestamp,
                'checksum': datapoint.checksum
            }
            result.append(data_dict)

    return result
