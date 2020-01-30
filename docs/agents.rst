pattoo Agents
=============

A very important aspect of ``pattoo`` are its agents. Agents gather data and send it to the central ``pattoo`` server. The use the information in the configuration file to know where to send the data.

The data has a standardized format. Both the data format and instructions on how to create an agent are available in this document.

JSON Formatting for pattoo-agents
---------------------------------

Agents send data as key-value pairs from multiple sources. Rather than repeating each key-value pair, there is a normalization process that eliminates duplication to reduce the amount of data that needs to be sent and stored in caches.

This is an example of what that data looks like:

.. code-block:: json

    {"pattoo_agent_timestamp": 1578071455335,
     "pattoo_agent_id": "66cf7a8e560f75e23d557023ce591120abd094925bde6d97f09561b69b6ed3c4",
     "pattoo_agent_polling_interval": 20000,
     "pattoo_datapoints": {
        "key_value_pairs": {
          "0": ["unit", "000"],
          "1": ["pattoo_agent_hostname", "palisadoes"],
          "2": ["pattoo_agent_id", "66cf7a8e560f75e23d557023ce591120abd094925bde6d97f09561b69b6ed3c4"],
          "3": ["pattoo_agent_polled_target", "foo.example.org"],
          "4": ["pattoo_agent_polling_interval", "20000"],
          "5": ["pattoo_agent_program", "pattoo_agent_modbustcpd"],
          "6": ["pattoo_key", "agent_modbustcpd_input_register_30386"],
          "7": ["pattoo_data_type", 99],
          "8": ["pattoo_value", 732.0],
          "9": ["pattoo_timestamp", 1578071455233],
          "10": ["pattoo_checksum", "8e160e806f80fefbb66877555dfd90dc8328b3879e04a3283315b5cbcbb2e773"],
          "11": ["pattoo_key", "agent_modbustcpd_input_register_30388"],
          "12": ["pattoo_value", 727.0],
          "13": ["pattoo_timestamp", 1578071455238],
          "14": ["pattoo_checksum", "768b8b33168d3733b11a8875315e7f039bc4a3cf7dcc6d407d9146b05ed82e7d"]},
        "datapoint_pairs": [
          [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
          [0, 1, 2, 3, 4, 5, 11, 7, 12, 13, 14]]
        }
      }


JSON Formatting Description
...........................

The following explains how the JSON is formatted.

#. ``pattoo_agent_timestamp`` is a millisecond timestamp of when the agent started to retrieve data. Created by the python code ``int((time.time() * 1000))``
#. ``pattoo_agent_id`` is a unique identifier for the agent.
#. ``pattoo_agent_polling_interval`` is how often the agent polls data in milliseconds.
#. ``pattoo_datapoints`` is a series of key-value pairs, and the datapoints they create, related to the data being polled.
    #. ``key_value_pairs`` is a series of key-value pairs. Some are mandatory (starting with the string ``pattoo``), others are added my the agent as metadata.
        #. ``pattoo_agent_hostname``: The name of the host the agent was running on.
        #. ``pattoo_agent_id``: The universally unique ID for the agent
        #. ``pattoo_checksum``: The checksum of the data and metadata values being sent.
        #. ``pattoo_agent_polled_target``: The name of the ``thing`` being polled. This could be a server, website, etc.
        #. ``pattoo_agent_polling_interval``: How often the agent polls data from the ``pattoo_agent_polled_target``.
        #. ``pattoo_agent_program``: The name of the agent program that did the polling. This is used to help determine how to process language translations and other types of processing on the keys sent by the agent.
        #. ``pattoo_key``: The key to which the data value is to be associated.
        #. ``pattoo_value``: The value of the data associated with the key at the time of polling.
        #. ``pattoo_data_type``: The type of data represented by ``pattoo_value``. The ``pattoo_data_type`` value is a code for integer, float, various counters and string.
        #. ``pattoo_timestamp``: The millisecond timestamp of when the data was retrieved from the ``pattoo_agent_polled_target``.
    #. ``datapoint_pairs`` is a list of lists of key-value pairs that define a datapoint. In this example we have two datapoints defined by the key-value pair ids ``[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]`` and ``[0, 1, 2, 3, 4, 5, 11, 7, 12, 13, 14``].

How to Create an Agent
----------------------

Let's describe a possible scenario to explain how to create an agent.

Foo Bar want's to keep track of stock market prices, specifically tickers ``ABC``, ``DEF``, ``GHI`` and ``JKL``.

#. Foo can get ``ABC``, ``DEF`` quotes from a website ``SITE_A``.
#. Data on ``GHI`` and ``JKL`` can be obtained from a system run by Foo's IT department named ``WORK_1``.
#. Foo writes an agent script to gather the data from both sources and send it to the ``pattoo`` server. The agent will identify itself as ``LAVA_SCRIPT`` when sending data.

Preparing the Agent Environment
...............................

You will need to some basic configuration before running the agent.

First create the necessary directories.

#. ``etc/`` where the configuration file will be placed.
#. ``daemon/`` where the agent will store its ``pattoo_agent_id`` value.
#. ``log/`` where the agent will store logging information.

    .. code-block:: bash

        mkdir -p /tmp/pattoo/etc /tmp/pattoo/daemon /tmp/pattoo/log

#. Then you'll need to create an environment variable to make the script know where to find its configuration file.

    .. code-block:: bash

        export PATTOO_CONFIGDIR=/tmp/pattoo/etc

    #. This could also be done inside your script with statement like this (before) you import ``pattoo_shared`` libraries using:

        .. code-block:: python

            os.environ['PATTOO_CONFIGDIR'] = 'PATTOO_CONFIGDIR=/tmp/pattoo/etc'

Configuring the Agent
.....................

Finally, you'll need to create a YAML configuration file named ``pattoo.yaml`` in the ``PATTOO_CONFIGDIR`` directory. The configuration must specify:

.. code-block:: yaml

   pattoo:

       log_level: debug
       log_directory: PATTOO_LOG_DIRECTORY
       cache_directory: PATTOO_CACHE_DIRECTORY
       daemon_directory: PATTOO_DAEMON_DIRECTORY
       language: en

   pattoo_agent_api:

       ip_address: 192.168.1.100
       ip_bind_port: 20201

Configuration Explanation
~~~~~~~~~~~~~~~~~~~~~~~~~

This table outlines the purpose of each configuration parameter

.. list-table::
   :header-rows: 1

   * - Section
     - Config Options
     - Description
   * - ``pattoo``
     -
     - This section defines the locations of key directories for both operation and troubleshooting
   * -
     - ``log_directory``
     - Path to logging directory. Make sure the username running the daemons have RW access to files there.
   * -
     - ``log_level``
     - Default level of logging. ``debug`` is best for troubleshooting.
   * -
     - ``cache_directory``
     - Directory of unsuccessful data posts to ``pattoo``
   * -
     - ``daemon_directory``
     - Directory used to store daemon related data that needs to be maintained between reboots
   * -
   - ``language``
   - Language spoken by the human users of ``pattoo``. Defaults to ``en`` (English)
   * - ``pattoo_agent_api``
     -
     - This section provides information needed by ``pattoo`` agent clients when contacting the pattoo server
   * -
     - ``ip_address``
     - IP address of remote ``pattoo`` server
   * -
     - ``ip_bind_port``
     - Port of remote ``pattoo`` server accepting agent data. Default 20201.


Sample Agent Script
...................

There are two sample scripts in the ``examples/bin`` directory. `You can find them here<https://github.com/PalisadoesFoundation/pattoo-shared/tree/master/examples/bin>`_ on GitHub.

#. ``sample_agent.py`` which will post data to the ``pattoo`` server only once when run.
#. ``sample_agent_daemon.py`` which will run as a daemon, periodically posting data to the ``pattoo`` server.
    #. A sample ``systemd`` `configuration file template can be found here <https://github.com/PalisadoesFoundation/pattoo-shared/tree/master/examples/systemd>`_ on GitHub. Remember to change the settings for the ``user``, ``group``, ``script path`` and ``PATTOO_CONFIGDIR`` before setting it up.

Customizing the Agent Configuration
...................................

In our example scripts we have not mentioned how the data was obtained. One way would be to add your own custom parameters to a configuration file in the ``PATTOO_CONFIGDIR`` directory. Make sure the file isn't named ``pattoo.yaml`` as this is the file ``pattoo`` uses for its own configuration.

Translation of Agent key-value Pairs into Something Meaningful
..............................................................

``pattoo`` agents send data to the ``pattoo`` server as key-value pairs. The keys will automatically be converted into lowercase with whitespace converted to underscores.

The lowercase, underscore modification was done specifically to facilitate multi-lingual support. You will need to create translation files. `This is described in detail here. <https://pattoo.readthedocs.io/en/latest/cli.html>`_
