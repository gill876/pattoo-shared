"""Module for classes that format variables."""

# pattoo imports
from .constants import DATA_INT
from pattoo_shared import times


class DataVariable(object):
    """Variable representation for data retreived from a device."""

    def __init__(self, value=None, data_label=None,
                 data_index=0, data_type=DATA_INT):
        """Initialize the class.

        Args:
            value: Value of data for a given data_index and data_label
            data_label: data_label
            data_index: Unique index value of data point. The combination of
                data_index and data_label must be unique for any polled device.
            data_type: Data type

        Returns:
            None

        """
        # Initialize variables
        self.data_label = data_label
        self.data_index = data_index
        self.value = value
        self.data_type = data_type

    def __repr__(self):
        """Return a representation of the attributes of the class.

        Args:
            None

        Returns:
            result: String representation.

        """
        # Create a printable variation of the value
        printable_value = _strip_non_printable(self.value)
        result = (
            '<{0} value={1} data_label={2}, data_index={3}, data_type={4}>'
            ''.format(
                self.__class__.__name__,
                repr(printable_value), repr(self.data_label),
                repr(self.data_index), repr(self.data_type)
            )
        )
        return result

    def __setattr__(self, name, value):
        """Set attibutes.

        Args:
            name:
            value:

        Returns:
            None

        """
        # Set the attribute
        self.__dict__[name] = value


class DataVariablesHost(object):
    """Object defining a list of DataVariable objects."""

    def __init__(self, device):
        """Initialize the class.

        Args:
            device: Device polled to get the DataVariable objects

        Returns:
            None

        """
        # Initialize key variables
        self.data = []
        self.device = device
        self.active = False

    def append(self, item):
        """Append DataVariable to the list.

        Args:
            item: A DataVariable object

        Returns:
            None

        """
        # Only append approved data types
        if isinstance(item, DataVariable) is True:
            self.data.append(item)

            # Set object as being active
            self.active = False not in [bool(self.data), bool(self.device)]

    def extend(self, items):
        """Extend the DataVariable list.

        Args:
            items: A DataVariable object list

        Returns:
            None

        """
        # Do nothing if not a list
        if isinstance(items, list) is False:
            return

        # Extend the list
        for item in items:
            self.append(item)


class AgentPolledData(object):
    """Object defining data received from / sent by Agent."""

    def __init__(self, agent_id, agent_program, agent_hostname,
                 timestamp=None, polling_interval=None):
        """Initialize the class.

        Args:
            agent_id: Agent ID
            agent_program: Name of agent program collecting the data
            agent_hostname: Hostname on which the agent ran
            timestamp: Timestamp of data
            polling_interval: Polling interval used to collect the data

        Returns:
            None

        """
        # Initialize key variables
        self.agent_id = agent_id
        self.agent_program = agent_program
        self.agent_hostname = agent_hostname
        (self.timestamp, self.polling_interval) = times.normalized_timestamp(
            polling_interval, timestamp=timestamp)
        self.data = []
        self.active = False

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
polling_interval={5}, active={6}>\
'''.format(self.__class__.__name__, repr(self.agent_id),
           repr(self.agent_program), repr(self.agent_hostname),
           repr(self.timestamp), repr(self.polling_interval),
           repr(self.active)))
        return result

    def append(self, item):
        """Append DataVariable to the list.

        Args:
            item: A DataVariablesHost object

        Returns:
            None

        """
        # Only append approved data types
        if isinstance(item, DataVariablesHost) is True:
            self.data.append(item)

            # Set object as being active
            self.active = False not in [
                bool(self.agent_id), bool(self.agent_program),
                bool(self.agent_hostname), bool(self.timestamp),
                bool(self.polling_interval), bool(self.data)]

    def extend(self, items):
        """Extend the DataVariable list.

        Args:
            items: A DataVariablesHost object list

        Returns:
            None

        """
        # Do nothing if not a list
        if isinstance(items, list) is True:
            # Extend the list
            for item in items:
                self.append(item)


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

    def __setattr__(self, name, value):
        """Set attibutes.

        Args:
            name:
            value:

        Returns:
            None

        """
        # Set the attribute
        self.__dict__[name] = value


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
