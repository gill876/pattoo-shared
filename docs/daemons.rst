pattoo Daemon
=============

Pattoo makes use of daemons allow for processes to run independently. Currently
daemons are configured to accept agents when instantiated.

**Note:** Service files and the linux systemd can be used to run a
daemon/process at boot and allow for easier manipulation of daemon state.

Daemon
------

The standard Daemon offers the ability to:
    - start
    - stop
    - restart
    - force


GracefulDaemon
--------------

GracefulDaemon allows for a process to gracefully shutdown and restart of a
process.
