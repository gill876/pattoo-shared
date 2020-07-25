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
    MAX_KEYPAIR_LENGTH, PattooDBrecord, RESERVED_KEYS, CACHE_KEYS,
    AGENT_METADATA_KEYS)
from pattoo_shared import data
from pattoo_shared import log


class Counter():
    """Count and format datapoint key-value pairs."""

    def __init__(self):
        """Initialize the class.

        Args:
            None

        Returns:
            None

        Variables:
            self._count: Number of key-value pairs processed

        """
        # Initialize key variables
        self._count = 0
        self.pairs = {}
        self.inverse_pairs = {}

    def counter(self, key, value):
        """Initialize the class.

        Args:
            key: Key
            value: Value

        Returns:
            result: Tuple of ((key, value), count)

        """
        # Return
        pair = (key, value)
        if pair not in self.pairs:
            self.pairs[pair] = self._count
            self.inverse_pairs[self._count] = pair
            self._count += 1
        result = self.pairs[pair]
        return result


def cache_to_keypairs(_data):
    """Convert agent cache data to AgentPolledData object.

    Args:
        _data: Data read from JSON cache file

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

    ####################################################################
    # Verify pattoo_datapoints
    ####################################################################

    # Verify we are getting a dict of datapoints
    if isinstance(_data['pattoo_datapoints'], dict) is False:
        log.log2warning(1035, _log_message)
        return []

    # Verify we are getting the correct key count
    if len(_data['pattoo_datapoints']) != 2:
        log.log2warning(1048, _log_message)
        return []

    # Verify we are getting the correct keys
    for item in ['key_value_pairs', 'datapoint_pairs']:
        if item not in _data['pattoo_datapoints']:
            log.log2warning(1049, _log_message)
            return []

    # Verify there are datapoint defining keys
    if isinstance(
            _data['pattoo_datapoints']['key_value_pairs'], dict) is False:
        log.log2warning(1050, _log_message)
        return []
    if isinstance(
            _data['pattoo_datapoints']['datapoint_pairs'], list) is False:
        log.log2warning(1051, _log_message)
        return []

    # Prepare for datapoint processing
    key_value_pairs = _data['pattoo_datapoints']['key_value_pairs']
    datapoint_pairs = _data['pattoo_datapoints']['datapoint_pairs']

    # Process each datapoint
    for pair_ids in datapoint_pairs:
        item = {}

        # Validate and assign key-values from datapoints
        for pair_id in pair_ids:
            # Lookup on a string of pair_id as the JSON in the cache file is
            # keyed by string integers
            _kv = key_value_pairs.get(str(pair_id))
            if isinstance(_kv, list) is False:
                log.log2warning(1046, _log_message)
                return []
            if len(_kv) != 2:
                log.log2warning(1045, _log_message)
                return []
            (key, value) = _kv
            item[key] = value

        # Assign datapoint values to PattooDBrecord
        pattoo_db_variable = _make_pattoo_db_record(item)
        if bool(pattoo_db_variable) is True:
            result.append(pattoo_db_variable)

    # Return
    return result


def _make_pattoo_db_record(item):
    """Ingest data.

    Args:
        item: Dict of key-value pairs DataPoint

    Returns:
        pattoo_db_variable: PattooDBrecord object

    """
    # Initialize data
    valids = []
    pattoo_db_variable = None
    _log_message = 'Invalid cache data.'
    reserved_keys_non_metadata = [
        _ for _ in RESERVED_KEYS if _ != 'pattoo_metadata']
    metadata = {}

    '''
    Make sure we have all keys required for creating a PattooDBrecord
    Omit 'pattoo_metadata' as we need to recreate it. 'pattoo_metadata' was
    extracted to its component key-value pairs before the agent posted it to
    the pattoo API
    '''
    for key in reserved_keys_non_metadata:
        valids.append(key in item.keys())
    for key in AGENT_METADATA_KEYS:
        valids.append(key in item.keys())
    if False in valids:
        log.log2warning(1047, _log_message)
        return None

    # Get metadata for item
    for key, value in sorted(item.items()):
        if key not in reserved_keys_non_metadata:
            metadata[key] = value
            valids.append(isinstance(key, str))

        # Work on the data_type
        if key == 'pattoo_data_type':
            valids.append(value in [
                DATA_FLOAT, DATA_INT, DATA_COUNT64, DATA_COUNT,
                DATA_STRING, DATA_NONE])

    # Append to result
    if False not in valids:
        # Add the datasource to the original checksum for better uniqueness
        checksum = _checksum(
            item['pattoo_agent_id'],
            item['pattoo_agent_polled_target'],
            item['pattoo_checksum'])
        pattoo_db_variable = PattooDBrecord(
            pattoo_checksum=checksum,
            pattoo_key=item['pattoo_key'],
            pattoo_agent_id=item['pattoo_agent_id'],
            pattoo_agent_polling_interval=item[
                'pattoo_agent_polling_interval'],
            pattoo_timestamp=item['pattoo_timestamp'],
            pattoo_data_type=item['pattoo_data_type'],
            pattoo_value=item['pattoo_value'],
            pattoo_agent_polled_target=item['pattoo_agent_polled_target'],
            pattoo_agent_program=item['pattoo_agent_program'],
            pattoo_agent_hostname=item['pattoo_agent_hostname'],
            pattoo_metadata=_keypairs(metadata)
        )

    # Return
    return pattoo_db_variable


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
                    True: {
                        'pattoo_agent_id': agentdata.agent_id,
                        'pattoo_agent_program': agentdata.agent_program,
                        'pattoo_agent_hostname': agentdata.agent_hostname,
                        'pattoo_agent_polled_target': ddv.target,
                    },
                    False: {
                        'pattoo_agent_polling_interval': (
                            agentdata.agent_polling_interval)
                        }
                }
                for update_checksum, items in sorted(metadata.items()):
                    for key, value in sorted(items.items()):
                        _dv.add(ConverterMetadata(
                            key, value, update_checksum=update_checksum))
                rows.append(_dv)

    # Return
    return rows


def datapoints_to_dicts(items):
    """Convert a list of DataPoint objects to a standardized dict for posting.

    Args:
        items: List of datapoints to convert

    Returns:
        result: Dict of 'key_value_pairs' and 'pattoo_datapoints' dicts
            key_value_pairs = Keyed by (key, value) with an ID value
            pattoo_datapoints = List of ID values with unique datapoint ID key

    """
    # Initialize key variables
    datapoints = []
    counter = Counter()
    all_dps = []

    # Verify input data
    if isinstance(items, list) is False:
        items = [items]
    for item in items:
        if isinstance(item, DataPoint):
            datapoints.append(item)

    # Populate dict to get unique key-value pairs
    for datapoint in datapoints:
        # Only convert valid data
        if datapoint.valid is True:
            dp_pair_ids = []
            dp_key_values = {}

            # Convert metadata into list of tuples
            key_values = list(datapoint.metadata.items())

            # Convert non metadata into list of tuples
            key_values.extend([
                ('pattoo_key', datapoint.key),
                ('pattoo_data_type', datapoint.data_type),
                ('pattoo_value', datapoint.value),
                ('pattoo_timestamp', datapoint.timestamp),
                ('pattoo_checksum', datapoint.checksum)])

            # Process tuples
            for key, value in key_values:
                # Assign ID to each key-value pair and store for later
                id_pair = counter.counter(key, value)
                dp_pair_ids.append(id_pair)
                dp_key_values[key] = value

            # Create a unique key tuple for the datapoint
            all_dps.append(dp_pair_ids)

    result = {
        'key_value_pairs': counter.inverse_pairs,
        'datapoint_pairs': all_dps}
    return result


def agentdata_to_post(agentdata):
    """Create data to post to the pattoo API.

    Args:
        agentdata: AgentPolledData object

    Returns:
        result: Dict of data to post

    """
    # Initialize key Variables
    agent_id = agentdata.agent_id
    polling_interval = agentdata.agent_polling_interval
    _data = agentdata_to_datapoints(agentdata)
    _datapoints = datapoints_to_dicts(_data)
    result = datapoints_to_post(agent_id, polling_interval, _datapoints)
    return result


def datapoints_to_post(agent_id, polling_interval, datapoints):
    """Create data to post to the pattoo API.

    Args:
        agent_id: Unique ID of agent posting data
        polling_interval: Interval over which the data is periodically polled
        datapoints: List of DataPoint objects

    Returns:
        result: Dict of data to post

    """
    result = PostingDataPoints(agent_id, polling_interval, datapoints)
    return result


def posting_data_points(_data):
    """Create data to post to the pattoo API.

    Args:
        _data: PostingDataPoints object

    Returns:
        result: Dict of data to post

    """
    result = {
        'pattoo_agent_timestamp': _data.pattoo_timestamp,
        'pattoo_agent_id': _data.pattoo_agent_id,
        'pattoo_agent_polling_interval': _data.pattoo_agent_polling_interval,
        'pattoo_datapoints': _data.pattoo_datapoints}
    return result


def _keypairs(_data):
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
        if _key in RESERVED_KEYS:
            continue
        # Key-Value pairs must be strings
        if isinstance(_key, str) is False or isinstance(
                value, str) is False:
            continue

        # Standardize the keys use underscores to separate words
        splits = re.findall(r"[\w']+", _key)
        key = '_'.join(splits).lower()

        # Update the list
        result.append(
            (str(key)[:MAX_KEYPAIR_LENGTH], str(
                value)[:MAX_KEYPAIR_LENGTH])
        )

    return result


def _checksum(agent_id, target, datapoint_checksum):
    """Create a unique checksum for a DataPoint based on agent and target.

    Args:
        record: PattooDBrecord converted to a Dict
        metadat: DataPoint Metadata

    Returns:
        result: Checksum

    """
    # Create checksum value
    result = data.hashstring('''{}{}{}\
'''.format(agent_id, target, datapoint_checksum), sha=512)
    return result
