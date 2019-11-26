#!/usr/bin/env python3
"""Pattoo Data Converter."""

# Standard imports
import re

# Pattoo libraries
from .variables import (
    ConverterMetadata, DataPoint, AgentPolledData,
    PostingDataPoints)
from .constants import (
    DATA_FLOAT, DATA_INT, DATA_COUNT64, DATA_COUNT, DATA_STRING, DATA_NONE,
    MAX_KEYPAIR_LENGTH, PattooDBrecord, RESERVED_KEYS, DATAPOINT_KEYS,
    CACHE_KEYS)
from pattoo_shared import data
from pattoo_shared import log


def cache_to_keypairs(_data):
    """Convert agent cache data to AgentPolledData object.

    Args:
        items: Cache data
        source: Source of the cache data

    Returns:
        result: Validated cache data. [] if invalid.

    """
    # Initialize key variables
    result = []
    _log_message = 'Invalid cache data.'

    # Basic validation
    if isinstance(_data, dict) is False:
        log.log2warning(1032, _log_message)
        return []
    if len(_data) != len(CACHE_KEYS):
        log.log2warning(1033, _log_message)
        return []
    for key in _data.keys():
        if key not in CACHE_KEYS:
            log.log2warning(1034, _log_message)
            return []

    # Intialize variables needed later
    polling_interval = _data['pattoo_polling_interval'] * 1000
    items = _data['pattoo_datapoints']
    source = _data['pattoo_source']

    # Verify we are getting a list
    if isinstance(items, list) is False:
        log.log2warning(1035, _log_message)
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
            valids.append(key in DATAPOINT_KEYS)
            valids.append(len(item) == len(DATAPOINT_KEYS))
            valids.append(isinstance(key, str))

            # Work on metadata
            if key == 'pattoo_metadata':
                # Must be a dict
                if isinstance(value, list) is False:
                    valids.append(False)
                    continue

                # Add metadata keypairs as a list of tuples
                for keypair_dict in value:
                    if isinstance(keypair_dict, dict) is False:
                        continue
                    keypairs.extend(_keypairs(keypair_dict, RESERVED_KEYS))

            # Work on the data_type
            if key == 'pattoo_data_type':
                valids.append(value in [
                    DATA_FLOAT, DATA_INT, DATA_COUNT64, DATA_COUNT,
                    DATA_STRING, DATA_NONE])

        # Append to result
        if False not in valids:
            # Add the datasource to the original checksum for better uniqueness
            checksum = data.hashstring(
                '{}{}'.format(source, item['pattoo_checksum']), sha=512)
            pattoo_db_variable = PattooDBrecord(
                pattoo_checksum=checksum,
                pattoo_key=item['pattoo_key'],
                pattoo_source=source,
                pattoo_polling_interval=polling_interval,
                pattoo_timestamp=item['pattoo_timestamp'],
                pattoo_data_type=item['pattoo_data_type'],
                pattoo_value=item['pattoo_value'],
                pattoo_metadata=keypairs
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

        for ddv in agentdata.data:
            # Ignore bad data
            if ddv.valid is False:
                continue

            # Get data
            for _dv in ddv.data:
                # Assign values to DataPoints
                metadata = {
                    'pattoo_agent_id': agentdata.agent_id,
                    'pattoo_agent_program': agentdata.agent_program,
                    'pattoo_agent_hostname': agentdata.agent_hostname,
                    'pattoo_agent_polled_device': ddv.device
                }
                for key, value in sorted(metadata.items()):
                    _dv.add(ConverterMetadata(key, value))
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
                'pattoo_metadata': [
                    {str(key): str(value)} for key, value in sorted(
                        datapoint.metadata.items())],
                'pattoo_key': datapoint.key,
                'pattoo_data_type': datapoint.data_type,
                'pattoo_value': datapoint.value,
                'pattoo_timestamp': datapoint.timestamp,
                'pattoo_checksum': datapoint.checksum
            }
            result.append(data_dict)

    return result


def agentdata_to_post(agentdata):
    """Create data to post to the pattoo API.

    Args:
        agentdata: AgentPolledData object

    Returns:
        result: Dict of data to post

    """
    # Initialize key Variables
    source = agentdata.agent_id
    polling_interval = agentdata.polling_interval
    _data = agentdata_to_datapoints(agentdata)
    _datapoints = datapoints_to_dicts(_data)
    result = datapoints_to_post(source, polling_interval, _datapoints)
    return result


def datapoints_to_post(source, polling_interval, datapoints):
    """Create data to post to the pattoo API.

    Args:
        source: Unique source ID string
        polling_interval: Interval over which the data is periodically polled
        datapoints: List of DataPoint objects

    Returns:
        result: Dict of data to post

    """
    result = PostingDataPoints(source, polling_interval, datapoints)
    return result


def posting_data_points(_data):
    """Create data to post to the pattoo API.

    Args:
        _data: PostingDataPoints object

    Returns:
        result: Dict of data to post

    """
    result = {
        'pattoo_source_timestamp': _data.pattoo_timestamp,
        'pattoo_source': _data.pattoo_source,
        'pattoo_polling_interval': _data.pattoo_polling_interval,
        'pattoo_datapoints': _data.pattoo_datapoints}
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
