#!/usr/bin/env python3
"""Pattoo times library."""

import time

# Pattoo libraries
from pattoo_shared.configuration import Config
from pattoo_shared import data


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


def normalized_timestamp(_polling_interval, timestamp=None):
    """Normalize timestamp to a multiple of 'polling_interval' seconds.

    Args:
        timestamp: epoch timestamp in seconds
        _polling_interval: Polling interval for data

    Returns:
        value: Normalized value

    """
    # Initialize key variables
    if isinstance(_polling_interval, int) is False:
        polling_interval = abs(Config().polling_interval())
    else:
        polling_interval = abs(_polling_interval)

    # Don't allow 0 values for polling_interval
    if bool(polling_interval) is False:
        polling_interval = 1

    # Process data
    if (timestamp is None) or (data.is_numeric(timestamp) is False):
        value = (int(time.time()) // polling_interval) * polling_interval
    else:
        value = (int(timestamp) // polling_interval) * polling_interval

    # Return
    return (value, polling_interval)
