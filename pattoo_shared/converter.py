#!/usr/bin/env python3
"""Pattoo helper for the Linux _data.

Description:

    Uses Python2 to be compatible with most Linux systems


"""
# Standard libraries
from collections import defaultdict
from copy import deepcopy


# Pattoo libraries
from .variables import (
    DataVariable, DataVariablesHost, AgentPolledData)
from .constants import (
    DATA_FLOAT, DATA_INT, DATA_COUNT64, DATA_COUNT, DATA_STRING, DATA_NONE)
from pattoo_shared import times


class ConvertAgentPolledData(object):
    """Converts AgentPolledData object to a standardized dict."""

    def __init__(self, agentdata):
        """Initialize the class.

        Args:
            agentdata: AgentPolledData object of data polled by agent

        Returns:
            None

        """
        # Initialize key variables
        self._data = defaultdict(lambda: defaultdict(dict))
        self._list_of_dv_host = agentdata.data
        self._data['timestamp'] = agentdata.timestamp
        self._data['polling_interval'] = agentdata.polling_interval
        self._data['agent_id'] = agentdata.agent_id
        self._data['agent_program'] = agentdata.agent_program
        self._data['agent_hostname'] = agentdata.agent_hostname
        self._data['devices'] = self._process()

    def _process(self):
        """Return the name of the _data.

        Args:
            None

        Returns:
            result: Data required

        """
        # Intitialize key variables
        # Yes we could have used Lambdas but pprint wouldn't fit on the screen
        result = {}

        # Get information from data
        for dv_host in self._list_of_dv_host:
            # Initialize variable for code simplicity
            device = dv_host.device

            # Pre-populate the result with empty dicts
            result[device] = {}

            # Analyze each DataVariable for the dv_host
            for _dvar in dv_host.data:
                # Add keys if not already there
                if _dvar.data_label not in result[device]:
                    result[device][_dvar.data_label] = {}

                # Assign data values to result
                data_tuple = (_dvar.data_index, _dvar.value)
                if 'data' in result[device][_dvar.data_label]:
                    result[device][_dvar.data_label][
                        'data'].append(data_tuple)
                else:
                    result[device][_dvar.data_label][
                        'data_type'] = _dvar.data_type
                    result[device][_dvar.data_label][
                        'data'] = [data_tuple]

        # Return
        return result

    def data(self):
        """Return that that should be posted.

        Args:
            None

        Returns:
            None

        """
        # Return
        return self._data


def convert(_data=None):
    """Convert agent cache data to AgentPolledData object.

    Args:
        _data: Agent data dict

    Returns:
        agentdata: AgentPolledData object

    """
    # Initialize key variables
    agent_id = None
    agent_program = None
    agent_hostname = None
    timestamp = None
    polling_interval = None

    # Get values to instantiate an AgentPolledData object
    (agent_id, agent_program, agent_hostname, timestamp, polling_interval,
     polled_data, agent_valid) = _valid_agent(_data)
    if agent_valid is False:
        return None
    agentdata = AgentPolledData(
        agent_id, agent_program, agent_hostname,
        timestamp=timestamp, polling_interval=polling_interval)

    # Iterate through devices polled by the agent
    for device, devicedata in sorted(polled_data.items()):
        # Create DataVariablesHost
        dv_host = _datavariableshost(device, devicedata)

        # Append the DataVariablesHost to the AgentPolledData object
        if dv_host.active is True:
            agentdata.append(dv_host)

    # Return
    if agentdata.active is False:
        return None
    else:
        return agentdata


def _valid_agent(_data):
    """Determine the validity of the Agent's data.

    Args:
        _data: Agent data dict

    Returns:
        result: Tuple of (
            agent_id, agent_program, agent_hostname,
            timestamp, polled_data, agent_valid)

    """
    # Initialize key variables
    agent_id = None
    agent_program = None
    agent_hostname = None
    timestamp = None
    polling_interval = None
    polled_data = None
    agent_valid = False

    # Verify values
    if isinstance(_data, dict) is True:
        if 'agent_id' in _data:
            agent_id = _data['agent_id']
        if 'agent_program' in _data:
            agent_program = _data['agent_program']
        if 'agent_hostname' in _data:
            agent_hostname = _data['agent_hostname']
        if 'timestamp' in _data:
            if isinstance(_data['timestamp'], int) is True:
                timestamp = _data['timestamp']
        if 'polling_interval' in _data:
            if isinstance(_data['polling_interval'], int) is True:
                polling_interval = _data['polling_interval']
        if 'devices' in _data:
            if isinstance(_data['devices'], dict) is True:
                polled_data = deepcopy(_data['devices'])

    # Valid timestamp related data?
    valid_times = times.validate_timestamp(timestamp, polling_interval)

    # Determine validity
    agent_valid = False not in [
        bool(agent_id), bool(agent_program),
        bool(agent_hostname), bool(timestamp),
        bool(polling_interval), bool(polled_data),
        bool(valid_times)]

    # Return
    result = (
        agent_id, agent_program, agent_hostname,
        timestamp, polling_interval, polled_data, agent_valid)
    return result


def _datavariableshost(device, devicedata):
    """Create a DataVariablesHost object from Agent data.

    Args:
        device: Device polled by agent
        devicedata: Data polled from device by agent

    Returns:
        datavariableshost: DataVariablesHost object

    """
    # Initialize key variables
    dv_host = DataVariablesHost(device)

    # Ignore invalid data
    if isinstance(devicedata, dict) is True:
        # Iterate through the expected data_labels in the dict
        for data_label, label_dict in sorted(devicedata.items()):
            # Ignore invalid data
            if isinstance(label_dict, dict) is False:
                continue

            # Validate the presence of required keys, then process
            if 'data' and 'data_type' in label_dict:
                # Skip invalid types
                if label_dict['data_type'] not in [
                        DATA_FLOAT, DATA_INT, DATA_COUNT64, DATA_COUNT,
                        DATA_STRING, DATA_NONE]:
                    continue
                if isinstance(label_dict['data'], list) is False:
                    continue

                # Add to the DataVariablesHost
                datavariables = _datavariables(data_label, label_dict)
                dv_host.extend(datavariables)

    # Return
    return dv_host


def _datavariables(data_label, label_dict):
    """Create a valid list of DataVariables for a specific label.

    Args:
        data_label: Label for data
        label_dict: Dict of data represented by the data_label

    Returns:
        datavariables: List of DataVariable objects

    """
    # Initialize key variables
    datavariables = []
    data_type = label_dict['data_type']

    # Add the data to the DataVariablesHost
    for item in label_dict['data']:
        if isinstance(item, list) is True:
            if len(item) == 2:
                data_index = item[0]
                value = item[1]

                # Skip invalid numerical data
                if data_type not in (DATA_STRING, DATA_NONE):
                    try:
                        float(value)
                    except:
                        continue

                # Update DataVariable with valid data
                datavariable = DataVariable(
                    value=value,
                    data_label=data_label,
                    data_index=data_index,
                    data_type=label_dict['data_type'])
                datavariables.append(datavariable)

    # Return
    return datavariables
