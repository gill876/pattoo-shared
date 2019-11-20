"""Module for classes that format variables."""

# Standard imports
from time import time

# pattoo imports
from pattoo_shared import data
from .constants import (
    DATA_INT, DATA_FLOAT, DATA_COUNT64, DATA_COUNT, DATA_STRING, DATA_NONE)


class DataPointMeta(object):
    """Metadata related to a DataPoint."""

    def __init__(self, key, value):
        """Initialize the class.

        Args:
            key: Metadata key
            value: Metadata value

        Returns:
            None

        Variables:
            self.key: Metadata key
            self.value: Metadata value
            self.valid: True if valid

        """
        # Initialize variables
        self.key = None
        self.value = None

        # Set variables
        if isinstance(key, (str, int, float)) is True and key is not True and (
                key is not False):
            self.key = str(key)
        if isinstance(value, (str, int, float)) is True and (
                value is not True and value is not False):
            self.value = str(value)

        self.valid = False not in [
            bool(self.key),
            self.key is not True,
            self.key is not False,
            self.key is not None,
            bool(self.value),
            self.value is not True,
            self.value is not False,
            self.value is not None,
            ]

    def __repr__(self):
        """Return a representation of the attributes of the class.

        Args:
            None

        Returns:
            result: String representation.

        """
        # Create a printable variation of the value
        result = ('<{0} key={1}, value={2}>'.format(
            self.__class__.__name__, repr(self.key), repr(self.value))
        )
        return result


class DataPoint(object):
    """Variable representation for data retreived from a device.

    Stores individual datapoints polled by pattoo agents

    """

    def __init__(self, key, value, data_type=DATA_INT, timestamp=None):
        """Initialize the class.

        Args:
            key: Key related to data value
            value: Data value
            data_type: This MUST be one of the types listed in constants.py

        Returns:
            None

        Variables:
            self.timestamp: Integer of epoch milliseconds
            self.valid: True if the object has a valid data_type
            self.checksum: Hash of self.key, self.data_type and metadata to
                ensure uniqueness when assigned to a device.

        """
        # Initialize variables
        self.key = key
        self.value = value
        self.data_type = data_type
        if bool(timestamp) is False:
            self.timestamp = int(time() * 1000)
        else:
            self.timestamp = timestamp
        self.metadata = {}
        self._metakeys = []

        # False validity if value is not of the right type
        self.valid = False not in [
            data_type in [DATA_INT, DATA_FLOAT, DATA_COUNT64, DATA_COUNT,
                          DATA_STRING, DATA_NONE],
            data_type is not False,
            data_type is not True,
            data_type is not None
        ]
        if False not in [
                data_type in [DATA_INT, DATA_FLOAT, DATA_COUNT64, DATA_COUNT],
                self.valid is True, data.is_numeric(value) is False]:
            self.valid = False

        # Convert floatable strings to float, and integers to ints
        if False not in [
                self.valid is True,
                data.is_numeric(value) is True,
                isinstance(value, str) is True]:
            if data_type in [DATA_FLOAT, DATA_COUNT64, DATA_COUNT]:
                self.value = float(value)
            elif data_type in [DATA_INT]:
                self.value = int(float(value))

        # Convert strings to string
        if data_type in [DATA_STRING]:
            self.value = str(value)

        # Create checksum
        self.checksum = data.hashstring(
            '{}{}'.format(self.key, self.data_type))

    def __repr__(self):
        """Return a representation of the attributes of the class.

        Args:
            None

        Returns:
            result: String representation.

        """
        # Create a printable variation of the value
        printable_value = _strip_non_printable(self.key)
        result = ('''\
<{} key={}, value={}, data_type={}, timestamp={}, valid={}>\
'''.format(self.__class__.__name__,
           repr(printable_value), repr(self.value),
           repr(self.data_type), repr(self.timestamp),
           repr(self.valid))
        )
        return result

    def add(self, items):
        """Add DataPointMeta to the internal self.metadata list.

        Args:
            items: A DataPointMeta object list

        Returns:
            None

        """
        # Test illegal keys
        datapoint_keys = [
            'checksum', 'metadata', 'data_type', 'key', 'value', 'timestamp']

        # Ensure there is a list of objects
        if isinstance(items, list) is False:
            items = [items]

        # Only append approved data types
        for item in items:
            if isinstance(item, DataPointMeta) is True:
                # Ignore invalid values
                if item.valid is False or item.key in datapoint_keys:
                    continue

                # Process
                if item.key not in self._metakeys:
                    self.metadata[item.key] = item.value
                    self._metakeys.append(item.key)
                    self.checksum = data.hashstring(
                        '{}{}{}'.format(self.checksum, item.key, item.value))


class DeviceDataPoints(object):
    """Object defining a list of DataPoint objects.

    Stores DataPoints polled from a specific ip_device.

    """

    def __init__(self, device, device_type=None):
        """Initialize the class.

        Args:
            device: Device polled to get the DataPoint objects
            device_type: Integer value identifying the type of device.
                Device_types are specific to the agent_program name. The
                intention is to make the combination of device_type and
                agent_program be the combined key in doing datapoint
                description lookups.

        Returns:
            None

        Variables:
            self.data: List of DataPoints retrieved from the device
            self.valid: True if the object is populated with DataPoints

        """
        # Initialize key variables
        self.data = []
        self.device = device
        self.valid = False
        self.device_type = None
        self._checksums = []
        self.device_type = _device_type(device_type)

    def __repr__(self):
        """Return a representation of the attributes of the class.

        Args:
            None

        Returns:
            result: String representation.

        """
        # Create a printable variation of the value
        result = (
            '<{0} device={1}, device_type={4}, valid={2}, data={3}'
            ''.format(
                self.__class__.__name__,
                repr(self.device), repr(self.valid), repr(self.data),
                repr(self.device_type)
            )
        )
        return result

    def add(self, items):
        """Append DataPoint to the internal self.data list.

        Args:
            items: A DataPoint object list

        Returns:
            None

        """
        # Ensure there is a list of objects
        if isinstance(items, list) is False:
            items = [items]

        # Only add DataPoint objects that are not duplicated
        for item in items:
            if isinstance(item, DataPoint) is True:
                if item.checksum not in self._checksums:
                    self.data.append(item)
                    self._checksums.append(item.checksum)

                # Set object as being.valid
                self.valid = False not in [bool(self.data), bool(self.device)]


class DeviceGateway(object):
    """Object defining a list of DeviceDataPoints objects.

    Stores DeviceDataPoints polled from a specific ip_device.

    """

    def __init__(self, device):
        """Initialize the class.

        Args:
            device: Device polled to get the DeviceDataPoints objects

        Returns:
            None

        Variables:
            self.data: List of DeviceDataPoints retrieved from the device
            self.valid: True if the object has assigned DeviceDataPoints

        """
        # Initialize key variables
        self.data = []
        self.device = device
        self.valid = False

    def __repr__(self):
        """Return a representation of the attributes of the class.

        Args:
            None

        Returns:
            result: String representation.

        """
        # Create a printable variation of the value
        result = (
            '<{0} device={1}, valid={2}, data={3}>'
            ''.format(
                self.__class__.__name__,
                repr(self.device), repr(self.valid), repr(self.data)
            )
        )
        return result

    def add(self, items):
        """Add DeviceDataPoints to the internal self.data list.

        Args:
            items: A DeviceDataPoints object list

        Returns:
            None

        """
        # Ensure there is a list of objects
        if isinstance(items, list) is False:
            items = [items]

        # Only append approved data types
        for item in items:
            if isinstance(item, DeviceDataPoints) is True:
                # Ignore invalid values
                if item.valid is False:
                    continue

                # Process
                self.data.append(item)

                # Set object as being valid
                self.valid = False not in [
                    bool(self.data), bool(self.device)]


class AgentPolledData(object):
    """Object defining data received from / sent by Agent.

    Only AgentPolledData objects can be submitted to the pattoo server through
    phttp.Post()

    """

    def __init__(self, agent_id, agent_program, agent_hostname,
                 polling_interval):
        """Initialize the class.

        Args:
            agent_id: Agent ID
            agent_program: Name of agent program collecting the data
            agent_hostname: Hostname on which the agent ran
            polling_interval: Polling interval used to collect the data

        Returns:
            None

        Variables:
            self.data: List of DeviceGateway objects created by polling
            self.valid: True if the object contains DeviceGateway objects

        """
        # Initialize key variables
        self.agent_id = agent_id
        self.agent_program = agent_program
        self.agent_hostname = agent_hostname
        self.agent_timestamp = int(time() * 1000)
        self.polling_interval = polling_interval
        self.data = []
        self.valid = False

    def __repr__(self):
        """Return a representation of the attributes of the class.

        Args:
            None

        Returns:
            result: String representation.

        """
        # Return
        result = ('''\
<{0} agent_id={1} agent_program={2}, agent_hostname={3}, timestamp={4} \
polling_interval={5}, valid={6}>\
'''.format(self.__class__.__name__, repr(self.agent_id),
           repr(self.agent_program), repr(self.agent_hostname),
           repr(self.agent_timestamp), repr(self.polling_interval),
           repr(self.valid)))
        return result

    def add(self, items):
        """Append DeviceGateway to the internal self.data list.

        Args:
            items: A DeviceGateway object list

        Returns:
            None

        """
        # Do nothing if not a list
        if isinstance(items, list) is False:
            items = [items]

        # Only append approved data types
        for item in items:
            # Only append approved data types
            if isinstance(item, DeviceGateway) is True:
                # Ignore invalid values
                if item.valid is False:
                    continue

                # Process
                self.data.append(item)

                # Set object as being.valid
                self.valid = False not in [
                    bool(self.agent_id), bool(self.agent_program),
                    bool(self.agent_hostname), bool(self.polling_interval),
                    bool(self.data)]


class AgentAPIVariable(object):
    """Variable representation for data required by the AgentAPI."""

    def __init__(self, ip_bind_port=6000, listen_address='0.0.0.0'):
        """Initialize the class.

        Args:
            ip_bind_port: ip_bind_port
            listen_address: TCP/IP address on which the API is listening.

        Returns:
            None

        """
        # Initialize variables
        self.ip_bind_port = ip_bind_port
        self.listen_address = listen_address

    def __repr__(self):
        """Return a representation of the attributes of the class.

        Args:
            None

        Returns:
            result: String representation.

        """
        result = ('''\
<{0} ip_bind_port={1}, listen_address={2}>\
'''.format(self.__class__.__name__,
           repr(self.ip_bind_port),
           repr(self.listen_address)
           )
        )
        return result


class PollingTarget(object):
    """Object used to track data to be polled."""

    def __init__(self, address=None, multiplier=1):
        """Initialize the class.

        Args:
            address: Address to poll
            multiplier: Multiplier to use when polled

        Returns:
            None

        """
        # Initialize variables
        self.address = address
        if data.is_numeric(multiplier) is True:
            self.multiplier = multiplier
        else:
            self.multiplier = 1
        self.valid = address is not None

        # Create checksum
        seed = '{}{}'.format(address, multiplier)
        self.checksum = data.hashstring(seed)

    def __repr__(self):
        """Return a representation of the attributes of the class.

        Args:
            None

        Returns:
            result: String representation.

        """
        result = ('''\
<{0} address={1}, multiplier={2}>\
'''.format(self.__class__.__name__,
           repr(self.address),
           repr(self.multiplier)
           ))
        return result


class DevicePollingTargets(object):
    """Object defining a list of PollingTarget objects.

    Stores PollingTargets polled from a specific ip_device.

    """

    def __init__(self, device, device_type=None):
        """Initialize the class.

        Args:
            device: Device polled to get the PollingTarget objects
            device_type: Integer value identifying the type of device.
                Device_types are specific to the agent_program name. The
                intention is to make the combination of device_type and
                agent_program be the combined key in doing datapoint
                description lookups.

        Returns:
            None

        Variables:
            self.data: List of PollingTargets retrieved from the device
            self.device: Name of device from which the data was received
            self.device_type: Type of device
            self.valid: True if the object is populated with PollingTargets

        """
        # Initialize key variables
        self.data = []
        self.device = device
        self.valid = False
        self._checksums = []
        self.device_type = _device_type(device_type)

    def __repr__(self):
        """Return a representation of the attributes of the class.

        Args:
            None

        Returns:
            result: String representation.

        """
        # Create a printable variation of the value
        result = (
            '<{0} device={1}, device_type={4}, valid={2}, data={3}>'
            ''.format(
                self.__class__.__name__,
                repr(self.device), repr(self.valid), repr(self.data),
                repr(self.device_type)
            )
        )
        return result

    def add(self, items):
        """Append PollingTarget to the internal self.data list.

        Args:
            items: A PollingTarget object list

        Returns:
            None

        """
        # Ensure there is a list of objects
        if isinstance(items, list) is False:
            items = [items]

        # Only add PollingTarget objects that are not duplicated
        for item in items:
            if isinstance(item, PollingTarget) is True:
                # Ignore invalid values
                if item.valid is False:
                    continue

                # Add data to the list
                if item.checksum not in self._checksums:
                    self.data.append(item)

                # Set object as being.valid
                self.valid = False not in [bool(self.data), bool(self.device)]


def _strip_non_printable(value):
    """Strip non printable characters.

    Removes any non-printable characters and adds an indicator to the string
    when binary characters are found.

    Args:
        value: the value that you wish to strip

    Returns:
        printable_value: Printable string

    """
    # Initialize key variables
    printable_value = ''

    if isinstance(value, str) is False:
        printable_value = value
    else:
        # Filter all non-printable characters
        # (note that we must use join to account for the fact that Python 3
        # returns a generator)
        printable_value = ''.join(
            [x for x in value if x.isprintable() is True])
        if printable_value != value:
            if bool(printable_value) is True:
                printable_value = '{} '.format(printable_value)
            printable_value = '{}(contains binary)'.format(printable_value)

    # Return
    return printable_value


def _device_type(device_type):
    """Create a standardized device type.

    Args:
        device_type: Type of device

    Returns:
        result: Standardized device_type

    """
    # Initialize key variables
    valid = True

    # Set the device_type
    if device_type is None or device_type is True or device_type is False:
        valid = False
    if valid is True:
        try:
            result = abs(int(device_type))
        except:
            result = None
    else:
        result = None
    return result
