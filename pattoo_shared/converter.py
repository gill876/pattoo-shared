#!/usr/bin/env python3
"""Pattoo Data Converter."""

# Standard libraries
from collections import defaultdict
from copy import deepcopy
import collections

# Pattoo libraries
from .variables import (
    DataVariable, DeviceDataVariables, DeviceGateway, AgentPolledData)
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
        self._gateway_data = agentdata.data
        self._data['timestamp'] = agentdata.timestamp
        self._data['polling_interval'] = agentdata.polling_interval
        self._data['agent_id'] = agentdata.agent_id
        self._data['agent_program'] = agentdata.agent_program
        self._data['agent_hostname'] = agentdata.agent_hostname
        self._data['gateways'] = self._process()

    def _process(self):
        """Process.

        Args:
            None

        Returns:
            result: Data required

        """
        # Intitialize key variables
        result = {}

        if isinstance(self._gateway_data, list) is True:
            for gwd in self._gateway_data:
                if isinstance(gwd, DeviceGateway) is True:
                    if bool(gwd.active) is True:
                        # Get information from data
                        gwd_dict = _capd_gwd2dict(gwd)
                        for gateway, values in gwd_dict.items():
                            result[gateway] = values

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
    for gateway, gw_dict in sorted(polled_data.items()):
        # Create an populate the DeviceGateway object
        gwd = DeviceGateway(gateway)
        for device, devicedata in sorted(gw_dict['devices'].items()):
            # Append the DeviceDataVariables to the DeviceGateway object
            ddv = _create_ddv(device, devicedata)
            if ddv.active is True:
                gwd.add(ddv)

        # Append the DeviceGateway to the AgentPolledData object
        if gwd.active is True:
            agentdata.add(gwd)

    # Return
    if agentdata.active is False:
        return None
    else:
        return agentdata


def extract(agentdata):
    """Ingest data.

    Args:
        agentdata: AgentPolledData object

    Returns:
        rows: List of named tuples containing data

    """
    # Initialize key variables
    rows = []
    datatuple = collections.namedtuple(
        'Values', '''\
agent_id agent_program agent_hostname timestamp polling_interval gateway \
device data_label data_index value data_type''')

    # Only process valid data
    if isinstance(agentdata, AgentPolledData) is True:
        # Return if invalid data
        if bool(agentdata.active) is False:
            return []

        # Assign agent values
        agent_id = agentdata.agent_id
        agent_program = agentdata.agent_program
        agent_hostname = agentdata.agent_hostname
        timestamp = agentdata.timestamp
        polling_interval = agentdata.polling_interval
        agent_program = agentdata.agent_program

        # Cycle through the data
        for gwd in agentdata.data:
            # Ignore bad data
            if gwd.active is False:
                continue

            # Get gateway from which data came
            gateway = gwd.device

            for ddv in gwd.data:
                # Ignore bad data
                if ddv.active is False:
                    continue

                # Get data
                device = ddv.device
                for _dv in ddv.data:
                    data_label = _dv.data_label
                    data_index = _dv.data_index
                    value = _dv.value
                    data_type = _dv.data_type

                    # Assign values to tuple
                    row = datatuple(
                        agent_id=agent_id, agent_program=agent_program,
                        agent_hostname=agent_hostname, timestamp=timestamp,
                        polling_interval=polling_interval, gateway=gateway,
                        device=device, data_label=data_label,
                        data_index=data_index,
                        value=value, data_type=data_type)
                    rows.append(row)

    # Return
    return rows


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
        if 'gateways' in _data:
            if isinstance(_data['gateways'], dict) is True:
                polled_data = deepcopy(_data['gateways'])

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


def _create_ddv(device, devicedata):
    """Create a DeviceDataVariables object from Agent data.

    Args:
        device: Device polled by agent
        devicedata: Data polled from device by agent

    Returns:
        ddv: DeviceDataVariables object

    """
    # Initialize key variables
    ddv = DeviceDataVariables(device)

    # Ignore invalid data
    if isinstance(devicedata, dict) is True:
        # Iterate through the expected data_labels in the dict
        for data_label, label_dict in sorted(devicedata.items()):
            # Ignore invalid data
            if isinstance(label_dict, dict) is False:
                continue

            # Validate the presence of required keys, then process
            if ('data' in label_dict) and ('data_type' in label_dict):
                # Skip invalid data formats
                if isinstance(label_dict['data'], list) is False:
                    continue

                # Add to the DeviceDataVariables
                datavariables = _create_datavariables(data_label, label_dict)
                ddv.add(datavariables)

    # Return
    return ddv


def _create_datavariables(data_label, label_dict):
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
    found_type = False

    # Skip invalid types
    for next_type in [
            DATA_FLOAT, DATA_INT, DATA_COUNT64, DATA_COUNT,
            DATA_STRING, DATA_NONE]:
        if (data_type == next_type) and (data_type is not True) and (
                data_type is not False):
            found_type = True
    if found_type is False:
        return []

    # Add the data to the DeviceDataVariables
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


def _capd_gwd2dict(gwd):
    """Create dict representation of DeviceGateway object.

    Args:
        gwd: DeviceGateway object

    Returns:
        result: Representation of DeviceGateway as a dict

    """
    # Intitialize key variables
    result = {}

    # Verify data type
    if isinstance(gwd, DeviceGateway) is True:
        if bool(gwd.active) is True:
            # Get information from data
            gateway = gwd.device

            # Analyze each DeviceDataVariables  object in data
            gwd_data_dict = {}
            for ddv in gwd.data:
                ddv_data_dict = _capd_ddv2dict(ddv)
                for remote_device, remote_data in sorted(
                        ddv_data_dict.items()):
                    if bool(remote_data) is True and (
                            isinstance(remote_data, dict) is True):
                        gwd_data_dict[remote_device] = remote_data

            # Update the result
            if bool(gwd_data_dict) is True:
                result[gateway] = {
                    'devices': gwd_data_dict
                }

    # Return
    return result


def _capd_ddv2dict(ddv):
    """Create dict representation of DeviceDataVariables object.

    Args:
        ddv: DeviceDataVariables object

    Returns:
        result: Representation of DeviceDataVariables as a dict

    """
    # Intitialize key variables
    result = {}

    # Verify data type
    if isinstance(ddv, DeviceDataVariables) is True:
        if bool(ddv.active) is True:
            # Get information from data
            device = ddv.device

            # Pre-populate the result with empty dicts
            result[device] = {}

            # Analyze each DataVariable for the ddv
            for _dvar in ddv.data:
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
