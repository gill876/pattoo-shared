"""Module for classes that format variables."""

# Standard imports
from time import time
import socket
import re

# pattoo imports
from pattoo_shared import data
from pattoo_shared import files
from pattoo_shared import network
from pattoo_shared.constants import (
    DATA_INT, DATA_FLOAT, DATA_COUNT64, DATA_COUNT, DATA_STRING, DATA_NONE,
    DATAPOINT_KEYS, AGENT_METADATA_KEYS)


class Metadata():
    """Metadata related to a DataPoint."""

    def __init__(self, key, value):
        """Initialize the class.

        Args:
            key: Metadata key
            value: Metadata value

        Returns:
            None

        """
        # Initialize variables
        self.key = key
        self.value = value
        self.update_checksum = True

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


class ConverterMetadata(Metadata):
    """Metadata related to a Converter DataPoint."""

    def __init__(self, key, value, update_checksum=True):
        """Initialize the class.

        Args:
            key: Metadata key
            value: Metadata value
            update_checksum: When True, the Datapoint object will update its
                checksum using the metadata values of objects created with this
                class. The DataPoint checksums are used to create new database
                entries. Not all metadata changes should trigger the creation
                of a new datapoint for charting. The updating of an operating
                system kernel version as metadata may not necessarily mean a
                completely new data source.

        Returns:
            None

        Variables:
            self.key: Metadata key
            self.value: Metadata value
            self.valid: True if valid

        """
        # Inherit object
        Metadata.__init__(self, key, value)

        # Initialize variables
        self.update_checksum = bool(update_checksum)
        (self.key, self.value, self.valid) = _key_value_valid(
            key, value, metadata=True, override=True)

        # Reset valid
        self.valid = False not in [
            key in AGENT_METADATA_KEYS,
            self.valid
        ]


class DataPointMetadata(Metadata):
    """Metadata related to a Regular DataPoint."""

    def __init__(self, key, value, update_checksum=True):
        """Initialize the class.

        Args:
            key: Metadata key
            value: Metadata value
            update_checksum: When True, the Datapoint object will update its
                checksum using the metadata values of objects created with this
                class. The DataPoint checksums are used to create new database
                entries. Not all metadata changes should trigger the creation
                of a new datapoint for charting. The updating of an operating
                system kernel version as metadata may not necessarily mean a
                completely new data source.

        Returns:
            None

        Variables:
            self.key: Metadata key
            self.value: Metadata value
            self.valid: True if valid

        """
        # Inherit object
        Metadata.__init__(self, key, value)
        self.update_checksum = bool(update_checksum)

        # Initialize variables
        (self.key, self.value, self.valid) = _key_value_valid(
            key, value, metadata=True)


class DataPoint():
    """Variable representation for data retreived from a target.

    Stores individual datapoints polled by pattoo agents

    """

    def __init__(self, key, value, data_type=DATA_INT, timestamp=None):
        """Initialize the class.

        Args:
            key: Key related to data value
            value: Data value
            data_type: This MUST be one of the types listed in constants.py
            timestamp: Integer EPOCH timestamp in milliseconds

        Returns:
            None

        Variables:
            self.timestamp: Integer of epoch milliseconds
            self.valid: True if the object has a valid data_type
            self.checksum: Hash of self.key, self.data_type and metadata to
                ensure uniqueness when assigned to a target.

        """
        # Initialize variables
        (self.key, self.value, self.valid) = _key_value_valid(
            key, value, metadata=False)
        self.data_type = data_type
        self.metadata = {}
        self._metakeys = []

        # Round timestamp to the nearest millisecond.
        if data.is_numeric(timestamp) is False:
            self.timestamp = int(round(time(), 3) * 1000)
        else:
            self.timestamp = int(timestamp)

        # False validity if value is not of the right type
        self.valid = False not in [
            data_type in [
                DATA_INT,
                DATA_FLOAT,
                DATA_COUNT64,
                DATA_COUNT,
                DATA_STRING,
                DATA_NONE
            ],
            data_type is not False,
            data_type is not True,
            data_type is not None,
            self.valid is True
        ]

        # Validity check: Make sure numeric data_types have numeric values
        if False not in [
                data_type in [
                    DATA_INT,
                    DATA_FLOAT,
                    DATA_COUNT64,
                    DATA_COUNT
                ],
                self.valid is True,
                data.is_numeric(value) is False]:
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
        """Add DataPointMetadata to the internal self.metadata list.

        Args:
            items: A DataPointMetadata object list

        Returns:
            None

        """
        # Ensure there is a list of objects
        if isinstance(items, list) is False:
            items = [items]

        # Only append approved data types
        for item in items:
            if isinstance(item, Metadata) is True:
                # Ignore invalid values
                if item.valid is False or item.key in DATAPOINT_KEYS:
                    continue

                # Process
                if item.key not in self._metakeys:
                    self.metadata[item.key] = item.value
                    self._metakeys.append(item.key)
                    if bool(item.update_checksum) is True:
                        self.checksum = data.hashstring('''\
{}{}{}'''.format(self.checksum, item.key, item.value))


class PostingDataPoints():
    """Object defining DataPoint objects to post to the pattoo server."""

    def __init__(self, agent_id, polling_interval, datapoints):
        """Initialize the class.

        Args:
            agent_id: Unique ID of agent posting data
            polling_interval: Periodic interval over which the data was polled.
            datapoints: List of DataPoint objects

        Returns:
            None

        """
        # Initialize key variables
        self.pattoo_agent_id = agent_id
        self.pattoo_agent_polling_interval = polling_interval
        self.pattoo_datapoints = datapoints
        self.pattoo_timestamp = int(time() * 1000)

        # Validation tests
        self.valid = False not in [
            isinstance(self.pattoo_agent_id, str),
            isinstance(self.pattoo_agent_polling_interval, int),
            isinstance(self.pattoo_datapoints, dict),
            self.pattoo_agent_polling_interval is not False,
            self.pattoo_agent_polling_interval is not True,
        ]
        if self.valid is True:
            self.valid = False not in [
                self.valid,
                'datapoint_pairs' in datapoints.keys(),
                'key_value_pairs' in datapoints.keys()
                ]
        if self.valid is True:
            self.valid = False not in [
                self.valid,
                isinstance(datapoints['datapoint_pairs'], list),
                isinstance(datapoints['key_value_pairs'], dict)
                ]


class TargetDataPoints():
    """Object defining a list of DataPoint objects.

    Stores DataPoints polled from a specific ip_target.

    """

    def __init__(self, target):
        """Initialize the class.

        Args:
            target: Target polled to get the DataPoint objects

        Returns:
            None

        Variables:
            self.data: List of DataPoints retrieved from the target
            self.valid: True if the object is populated with DataPoints

        """
        # Initialize key variables
        self.data = []
        self.target = target
        self.valid = False
        self._checksums = []

    def __repr__(self):
        """Return a representation of the attributes of the class.

        Args:
            None

        Returns:
            result: String representation.

        """
        # Create a printable variation of the value
        result = (
            '<{0} target={1}, valid={2}, data={3}'
            ''.format(
                self.__class__.__name__,
                repr(self.target), repr(self.valid), repr(self.data)
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
                self.valid = False not in [bool(self.data), bool(self.target)]


class AgentPolledData():
    """Object defining data received from / sent by Agent.

    Only AgentPolledData objects can be submitted to the pattoo server through
    phttp.Post()

    """

    def __init__(self, agent_program, polling_interval):
        """Initialize the class.

        Args:
            agent_program: Name of agent program collecting the data
            polling_interval: Polling interval

        Returns:
            None

        Variables:
            self.data: List of TargetDataPoints objects created by polling
            self.valid: True if the object contains TargetDataPoints objects

        """
        # Initialize key variables
        self.agent_program = agent_program
        self.agent_hostname = socket.getfqdn()
        self.agent_timestamp = int(time() * 1000)
        self.data = []
        self.valid = False
        self.agent_polling_interval = polling_interval * 1000

        # Get the agent_id
        from .configuration import Config
        config = Config()
        self.agent_id = files.get_agent_id(agent_program, config)

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
           repr(self.agent_timestamp), repr(self.agent_polling_interval),
           repr(self.valid)))
        return result

    def add(self, items):
        """Append TargetDataPoints to the internal self.data list.

        Args:
            items: A TargetDataPoints object list

        Returns:
            None

        """
        # Do nothing if not a list
        if isinstance(items, list) is False:
            items = [items]

        # Only append approved data types
        for item in items:
            # Only append approved data types
            if isinstance(item, TargetDataPoints) is True:
                # Ignore invalid values
                if item.valid is False:
                    continue

                # Process
                self.data.append(item)

                # Set object as being.valid
                self.valid = False not in [
                    bool(self.agent_id),
                    bool(self.agent_program),
                    bool(self.agent_hostname),
                    bool(self.agent_polling_interval),
                    bool(self.data)]


class AgentAPIVariable():
    """Variable representation for data required by the AgentAPI."""

    def __init__(self, ip_bind_port=20201, ip_listen_address='0.0.0.0'):
        """Initialize the class.

        Args:
            ip_bind_port: ip_bind_port
            listen_address: TCP/IP address on which the API is listening.

        Returns:
            None

        """
        # Initialize variables
        self.ip_bind_port = ip_bind_port
        self.ip_listen_address = ip_listen_address

    def __repr__(self):
        """Return a representation of the attributes of the class.

        Args:
            None

        Returns:
            result: String representation.

        """
        result = ('''\
<{0} ip_bind_port={1}, ip_listen_address={2}>\
'''.format(self.__class__.__name__,
           repr(self.ip_bind_port),
           repr(self.ip_listen_address)
           )
        )
        return result


class PollingPoint():
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


class TargetPollingPoints():
    """Object defining a list of PollingPoint objects.

    Stores PollingPoints polled from a specific ip_target.

    """

    def __init__(self, target):
        """Initialize the class.

        Args:
            target: Target polled to get the PollingPoint objects

        Returns:
            None

        Variables:
            self.data: List of PollingPoints retrieved from the target
            self.target: Name of target from which the data was received
            self.valid: True if the object is populated with PollingPoints

        """
        # Initialize key variables
        self.data = []
        self.target = target
        self.valid = False
        self._checksums = []

    def __repr__(self):
        """Return a representation of the attributes of the class.

        Args:
            None

        Returns:
            result: String representation.

        """
        # Create a printable variation of the value
        result = (
            '<{0} target={1}, valid={2}, data={3}>'
            ''.format(
                self.__class__.__name__,
                repr(self.target), repr(self.valid), repr(self.data)
            )
        )
        return result

    def add(self, items):
        """Append PollingPoint to the internal self.data list.

        Args:
            items: A PollingPoint object list

        Returns:
            None

        """
        # Ensure there is a list of objects
        if isinstance(items, list) is False:
            items = [items]

        # Only add PollingPoint objects that are not duplicated
        for item in items:
            if isinstance(item, PollingPoint) is True:
                # Ignore invalid values
                if item.valid is False:
                    continue

                # Add data to the list
                if item.checksum not in self._checksums:
                    self.data.append(item)

                # Set object as being.valid
                self.valid = False not in [bool(self.data), bool(self.target)]


class IPTargetPollingPoints(TargetPollingPoints):
    """Object defining a list of PollingPoint objects.

    Stores PollingPoints polled from a specific ip_target.

    """

    def __init__(self, target):
        """Initialize the class.

        Args:
            target: Target polled to get the PollingPoint objects

        Returns:
            None

        Variables:
            self.data: List of PollingPoints retrieved from the target
            self.target: Name of target from which the data was received
            self.valid: True if the object is populated with PollingPoints

        """
        # Inherit object
        TargetPollingPoints.__init__(self, target)

    def add(self, items):
        """Append PollingPoint to the internal self.data list.

        Args:
            items: A PollingPoint object list

        Returns:
            None

        """
        # Ensure there is a list of objects
        if isinstance(items, list) is False:
            items = [items]

        # Only add PollingPoint objects that are not duplicated
        for item in items:
            if isinstance(item, PollingPoint) is True:
                # Ignore invalid values
                if item.valid is False:
                    continue

                # Add data to the list
                if item.checksum not in self._checksums:
                    self.data.append(item)

                # Set object as being.valid
                self.valid = False not in [
                    bool(self.data), bool(network.get_ipaddress(self.target))]


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


def _key_value_valid(key, value, metadata=False, override=False):
    """Create a standardized version of key, value.

    Args:
        key: Key
        value: Value
        metadata: If True, convert value to string and strip. Used for
            metadata key-value pairs.
        override: Allow the 'pattoo' string in the key. Used when posting
            DataPoint objects to the pattoo server.

    Returns:
        result: Tuple of (key, value, valid)

    """
    # Set variables
    valid = False not in [
        isinstance(key, (str, int, float)) is True,
        key is not True,
        key is not False,
        key is not None,
        isinstance(value, (str, int, float)) is True,
        value is not True,
        value is not False,
        value is not None,
        ]

    # Assign key, value
    if valid is True:
        key = str(key).lower().strip()

        # Reevaluate valid
        valid = False not in [
            valid,
            key != '']

        # 'pattoo' normally cannot be in the key.
        if override is False:
            valid = False not in [
                valid,
                'pattoo' not in key.lower()]

    # Assign values
    if valid is True:
        if bool(metadata) is True:
            value = str(value).strip()
    else:
        key = None
        value = None

    # Return
    result = (key, value, valid)
    return result


def _strip_pattoo(key):
    """Remove the string 'pattoo' from key.

    1) Remove the string 'pattoo' from key
    2) Replace dashes ('-') with underscores ('_')
    3) Remove leading underscores
    4) Strip leading and trailing white space
    5) Make the key lowercase

    Args:
        key: Key to process

    Returns:
        result: Key without string.

    """
    # Return
    result = str(key).lower().strip().replace('pattoo', '').replace('-', '_')
    result = re.sub(r'^(_)+(.*?)$', '\\2', result)
    return result
