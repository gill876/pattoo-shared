Data Classes
============

These classes are used to help create a standard way of polling from remote devices and reporting data back to the central ``pattoo`` server.

How Agents Poll Data
--------------------
Follow this process if you are attempting to creating your own ``pattoo`` agent.

#. Agents poll devices for ``DataPoint`` values.
#. All the ``DataPoint`` values polled from a device are added to a ``TargetDataPoints`` object.
#. All the ``TargetDataPoints`` objects polled by an agent are packaged into a ``AgentPolledData`` object.
#. The ``AgentPolledData`` object is then posted to the ``pattoo`` API through phttp.Post()

Variable Class Descriptions
---------------------------

This section describes the `PattooShared Variable Classes <https://github.com/PalisadoesFoundation/pattoo-shared/blob/master/pattoo_shared/variables.py>`_

.. list-table::
   :header-rows: 1

   * - Class
     - Description
   * - ``DataPoint``
     - Stores individual datapoints polled by ``pattoo`` agents
   * - ``TargetDataPoints``
     - Stores ``DataPoints`` polled from a specific ``ip_device``.
   * - ``AgentPolledData``
     - Stores data polled by an agent from all its assigned ``ip_devices``. The ``AgentPolledData`` object contains a list of ``TargetDataPoints`` objects.
   * - ``AgentAPIVariable``
     - Stores data used by ``pattoo`` APIs to serve data


pHTTP Class Descriptions
------------------------

This section describes the `PattooShared pHTTP Classes <https://github.com/PalisadoesFoundation/pattoo-shared/blob/master/pattoo_shared/phttp.py>`_

These classes are used to help create a standard way of using HTTP to poll remote devices and report data back to the central ``pattoo`` server.

.. list-table::
   :header-rows: 1

   * - Class
     - Description
   * - ``Post``
     - Posts an ``AgentPolledData`` object created by an agent to a remote ``pattoo`` server.
   * - ``PassiveAgent``
     - Retrieves JSON data from ``pattoo`` agents that run their own webserver.
