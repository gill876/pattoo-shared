#!/usr/bin/env python3
"""Pattoo times library."""

import time

# Pattoo libraries
from pattoo_shared import data
from pattoo_shared import log


def validate_timestamp(timestamp, polling_interval):
    """Validate timestamp to be a multiple of 'polling_interval' seconds.

    Args:
        timestamp: epoch timestamp in seconds
        polling_interval: Polling interval for data

    Returns:
        valid: True if valid

    """
    # Initialize key variables
    valids = []
    valid = False

    # Evaluate validity of the parameters
    valids.append(bool(polling_interval))
    valids.append(data.is_numeric(timestamp))
    valids.append(data.is_numeric(polling_interval))
    valids.append(isinstance(polling_interval, (int, float)))

    # Process data
    if False not in valids:
        test = (int(timestamp) // polling_interval) * polling_interval
        if test == timestamp:
            valid = True

    # Return
    return valid


def normalized_timestamp(_pi, timestamp=None):
    """Normalize timestamp to a multiple of 'polling_interval' seconds.

    Args:
        timestamp: epoch style timestamp in millseconds
        _pi: Polling interval for data in milliseconds. Defaults to assuming
            1000 if 'None'.

    Returns:
        value: Normalized value

    """
    # Initialize key variables
    if bool(_pi) is True:
        if isinstance(_pi, int) is False:
            log_message = ('''\
Invalid non-integer "polling_interval" value of {}'''.format(_pi))
            log.log2die(1029, log_message)
        else:
            polling_interval = abs(_pi)
    else:
        # Don't allow 0 values for polling_interval
        polling_interval = 1000

    # Process data
    if (timestamp is None) or (data.is_numeric(timestamp) is False):
        value = (
            int(time.time() * 1000) // polling_interval) * polling_interval
    else:
        value = (int(timestamp) // polling_interval) * polling_interval

    # Return
    return value


def timestamps(ts_start_raw, ts_stop_raw, _pi):
    """Get normalized timestamps list for every sampling_rate number of steps.

    Args:
        ts_start_raw: Timestamp of the start of the report
        ts_stop_raw: Timestamp of the end of the report
        _pi: Polling interval

    Returns:
        _timestamps: list of timstamps

    """
    # Normalize timestamps
    ts_start = normalized_timestamp(_pi, ts_start_raw)
    ts_stop = normalized_timestamp(_pi, ts_stop_raw)

    # Create a list of timestamps
    _timestamps = list(range(ts_start, ts_stop + _pi, _pi))

    # Returns
    return _timestamps
