#!/usr/bin/env python3
"""Pattoo classes that manage various URL manipulations."""

# Standard imports.
import ipaddress


def url_ip_address(ip_address):
    """Adjust address for IPv6 if necessary.

    Args:
        ip_address: IP address / hostname

    Returns:
        result: Fixed address for polling

    """
    # Initialize key variables
    result = None

    # Check IP address type
    try:
        ip_object = ipaddress.ip_address(ip_address)
    except:
        # Hostname string was presented
        result = '{}'.format(ip_address)

    if bool(result) is False:
        # Is this an IPv4 address?
        ipv4 = isinstance(ip_object, ipaddress.IPv4Address)
        if ipv4 is True:
            result = '{}'.format(ip_address)
        else:
            result = '[{}]'.format(ip_address)

    # Return result
    return result
