Introduction
============

``pattoo`` stores timeseries data in a database and makes it available for users via a GraphQL API.

PattooShared Objective
----------------------

The data posted by ``pattoo`` agents to the central server must be clearly defined. The data stuctures must be identical for easy interoperability.

The PattooShared ``pip`` module creates a universal set of classes to produce and consume ``pattoo`` compatible data.

Related Documentation
---------------------

There are a number of sets of documents that cover the ``pattoo`` portfolio.

Pattoo
~~~~~~
This is data collection server that acts as the central repository of data provided by the ``pattoo`` agents.

* The `Pattoo Server documentation <https://pattoo.readthedocs.io/>`_ can be found here.
* Visit the `Pattoo Server GitHub site <https://github.com/PalisadoesFoundation/pattoo>`_ to see the code.

Pattoo-Agents
~~~~~~~~~~~~~
The ``pattoo`` agents collect data from a variety of sources and send them to the central ``pattoo`` server over HTTP. We provide a few standard agents, but you can create your own. (See Pattoo-Shared for details)

* The `Pattoo Agents documentation <https://pattoo-agents.readthedocs.io/>`_ can be found here.
* Visit the `Pattoo Agents GitHub site <https://github.com/PalisadoesFoundation/pattoo-agents>`_ to see the code.

Pattoo-Shared
~~~~~~~~~~~~~
Both the ``pattoo`` agents and server use a shared python library which must be pre-installed using ``pip3`` for them to work.

You can use the ``pattoo-shared`` documentation to learn the basics of creating your own custom ``pattoo-agents`` to feed data to the ``pattoo`` server

* The `Pattoo Shared documentation <https://pattoo-shared.readthedocs.io/>`_ can be found here.
* Visit the `Pattoo Shared GitHub site <https://github.com/PalisadoesFoundation/pattoo-shared>`_ to see the code.
