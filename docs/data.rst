
JSON Formatting for pattoo-agents
=================================

This document shows the various key, value pairs used in the ``json`` data used by ``pattoo``. This data is either sent to, or retrieved from, a remote ``pattoo`` server.

.. code-block:: json

{'agent_hostname': 'palisadoes',
 'agent_id': '8273cf01a6ea9334a00b2023f92799cbdf3c72d2de084a45e344c0c487746cc0',
 'agent_program': 'pattoo_agent_os_autonomousd',
 'gateways': {
     'gw01': {
         'devices': {
             'palisadoes': {
                 'cpu_count': {
                     'data': [[0, 8]],
                     'data_type': 0},
                 'cpu_stats': {
                     'data': [
                         ['ctx_switches', 3721224481],
                         ['interrupts', 1708955737],
                         ['soft_interrupts', 781652003],
                         ['syscalls', 0]],
                     'data_type': 64},
                 'network_bytes_recv': {
                     'data': [
                         ['wlp3s0', 0],
                         ['enp2s0', 20112540291],
                         ['lo', 80301094]],
                     'data_type': 64},
                 'release': {
                     'data': [[0, '4.15.0-65-generic']],
                     'data_type': 2},
                 'system': {
                     'data': [[0, 'Linux']],
                     'data_type': 2},
                 'version': {
                     'data': [[0, '#74-Ubuntu SMP Tue Sep 17 17:06 UTC 2019']],
                     'data_type': 2}
                 }
             }
         }
     },
 'polling_interval': 10,
 'timestamp': 1572056400}


Formatting
----------
