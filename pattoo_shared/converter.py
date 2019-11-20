#!/usr/bin/env python3
"""Pattoo Data Converter."""

# Standard imports
import re

# Pattoo libraries
from .variables import (
    DataPointMeta, DataPoint, AgentPolledData)
from .constants import (
    DATA_FLOAT, DATA_INT, DATA_COUNT64, DATA_COUNT, DATA_STRING, DATA_NONE,
    MAX_KEYPAIR_LENGTH, PattooDBrecord)
from pattoo_shared import data


def cache_to_keypairs(source, items):
    """Convert agent cache data to AgentPolledData object.

    Args:
        items: Cache data
        source: Source of the cache data

    Returns:
        result: Validated cache data. [] if invalid.

    """
    # Initialize key variables
    result = []
    datapoint_keys = [
        'checksum', 'metadata', 'data_type', 'key', 'value', 'timestamp']

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
            valids.append(key in datapoint_keys)
            valids.append(len(item) == len(datapoint_keys))
            valids.append(isinstance(key, str))

            # Work on metadata
            if key == 'metadata':
                # Must be a dict
                if isinstance(value, list) is False:
                    valids.append(False)
                    continue

                # Add metadata keypairs as a list of tuples
                for keypair_dict in value:
                    if isinstance(keypair_dict, dict) is False:
                        continue
                    keypairs.extend(_keypairs(keypair_dict, datapoint_keys))

            # Work on the data_type
            if key == 'data_type':
                valids.append(value in [
                    DATA_FLOAT, DATA_INT, DATA_COUNT64, DATA_COUNT,
                    DATA_STRING, DATA_NONE])

        # Append to result
        if False not in valids:
            # Add the datasource to the original checksum for better uniqueness
            checksum = data.hashstring(
                '{}{}'.format(source, item['checksum']), sha=512)
            pattoo_db_variable = PattooDBrecord(
                checksum=checksum,
                key=item['key'],
                source=source,
                timestamp=item['timestamp'],
                data_type=item['data_type'],
                value=item['value'],
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
                'key': datapoint.key,
                'data_type': datapoint.data_type,
                'value': datapoint.value,
                'timestamp': datapoint.timestamp,
                'checksum': datapoint.checksum
            }
            result.append(data_dict)

    return result


def _keypairs(_data, exclude_list):
    """Make key-pairs from metadata dict.

    Args:
        data: Metadata dict

    Returns:
        result: List of tuples of key-pair values

    """
    # Initialize key variables
    result = []

    # Loop around keys
    for _key, value in _data.items():
        # We want to make sure that we don't have
        # duplicate key-value pairs
        if _key in exclude_list:
            continue
        # Key-Value pairs must be strings
        if isinstance(_key, str) is False or isinstance(
                value, str) is False:
            continue

        # Standardize the keys
        splits = re.findall(r"[\w']+", _key)
        key = '_'.join(splits).lower()

        # Update the list
        result.append(
            (str(key)[:MAX_KEYPAIR_LENGTH], str(
                value)[:MAX_KEYPAIR_LENGTH])
        )

    return result
