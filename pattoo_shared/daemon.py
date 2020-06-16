"""Generic linux daemon base class for python 3.x."""

from __future__ import print_function
import atexit
import signal
import sys
import os
import time

# Pattoo imports
from pattoo_shared import log
from pattoo_shared.constants import GRACEFUL_TIMEOUT

# Third party library
from pystemd.systemd1 import Unit


class Daemon():
    """A generic daemon class.

    Usage: subclass the daemon class and override the run() method.

    Modified from http://www.jejik.com/files/examples/daemon3x.py

    """

    def __init__(self, agent):
        """Initialize the class.

        Args:
            agent: Agent object

        Returns:
            None

        """
        self.name = agent.name()
        self.pidfile = agent.pidfile_parent
        self.lockfile = agent.lockfile_parent
        self._config = agent.config

    def _daemonize(self):
        """Deamonize class. UNIX double fork mechanism.

        Args:
            None

        Returns:
            None

        """
        # Initialize key variables
        daemon_log_file = self._config.log_file_daemon()

        # Create a parent process that will manage the child
        # when the code using this class is done.
        try:
            pid = os.fork()
            if pid > 0:
                # Exit first parent
                sys.exit(0)
        except OSError as err:
            log_message = 'Daemon fork #1 failed: {}'.format(err)
            log_message = '{} - PID file: {}'.format(log_message, self.pidfile)
            log.log2die(1060, log_message)

        # Decouple from parent environment
        os.chdir('{}'.format(os.sep))
        os.setsid()
        os.umask(0)

        # Do second fork
        try:
            pid = os.fork()
            if pid > 0:

                # exit from second parent
                sys.exit(0)
        except OSError as err:
            log_message = 'Daemon fork #2 failed: {}'.format(err)
            log_message = '{} - PID file: {}'.format(log_message, self.pidfile)
            log.log2die(1061, log_message)

        # Redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        f_handle_si = open(os.devnull, 'r')
        f_handle_so = open(daemon_log_file, 'a+')
        f_handle_se = open(daemon_log_file, 'a+')
        os.dup2(f_handle_si.fileno(), sys.stdin.fileno())
        os.dup2(f_handle_so.fileno(), sys.stdout.fileno())
        os.dup2(f_handle_se.fileno(), sys.stderr.fileno())

        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        with open(self.pidfile, 'w+') as f_handle:
            f_handle.write('{}\n'.format(pid))

    def delpid(self):
        """Delete the PID file.

        Args:
            None

        Returns:
            None

        """
        # Delete file
        if os.path.exists(self.pidfile) is True:
            try:
                os.remove(self.pidfile)
            except:
                log_message = (
                    'PID file {} already deleted'.format(self.pidfile))
                log.log2warning(1041, log_message)

    def dellock(self):
        """Delete the lock file.

        Args:
            None

        Returns:
            None

        """
        # Delete file
        if self.lockfile is not None:
            if os.path.exists(self.lockfile) is True:
                os.remove(self.lockfile)

    def start(self):
        """Start the daemon.

        Args:
            None

        Returns:
            None

        """
        # Check for a pidfile to see if the daemon already runs
        try:
            with open(self.pidfile, 'r') as pf_handle:
                pid = int(pf_handle.read().strip())

        except IOError:
            pid = None

        if pid:
            log_message = (
                'PID file: {} already exists. Daemon already running?'
                ''.format(self.pidfile))
            log.log2die(1062, log_message)

        # Start the daemon
        self._daemonize()

        # Log success
        log_message = (
            'Daemon {} started - PID file: {}'
            ''.format(self.name, self.pidfile))
        log.log2info(1070, log_message)

        # Run code for daemon
        self.run()

    def force(self):
        """Stop the daemon by deleting the lock file first.

        Args:
            None

        Returns:
            None

        """
        # Delete lock file and stop
        self.dellock()
        self.stop()

    def stop(self):
        """Stop the daemon.

        Args:
            None

        Returns:
            None

        """
        # Get the pid from the pidfile
        try:
            with open(self.pidfile, 'r') as pf_handle:
                pid = int(pf_handle.read().strip())
        except IOError:
            pid = None

        if not pid:
            log_message = (
                'PID file: {} does not exist. Daemon not running?'
                ''.format(self.pidfile))
            log.log2warning(1063, log_message)
            # Not an error in a restart
            return

        # Try killing the daemon process
        try:
            while 1:
                if self.lockfile is None:
                    os.kill(pid, signal.SIGTERM)
                else:
                    time.sleep(0.3)
                    if os.path.exists(self.lockfile) is True:
                        continue
                    else:
                        os.kill(pid, signal.SIGTERM)
                time.sleep(0.3)
        except OSError as err:
            error = str(err.args)
            if error.find("No such process") > 0:
                self.delpid()
                self.dellock()
            else:
                log_message = (str(err.args))
                log_message = (
                    '{} - PID file: {}'.format(log_message, self.pidfile))
                log.log2die(1068, log_message)
        except:
            log_message = (
                'Unknown daemon "stop" error for PID file: {}'
                ''.format(self.pidfile))
            log.log2die(1066, log_message)

        # Log success
        self.delpid()
        self.dellock()
        log_message = (
            'Daemon {} stopped - PID file: {}'
            ''.format(self.name, self.pidfile))
        log.log2info(1071, log_message)

    def restart(self):
        """Restart the daemon.

        Args:
            None

        Returns:
            None

        """
        # Restart with a wait period to make sure things shutdown smoothly
        self.stop()
        time.sleep(3)
        self.start()

    def status(self):
        """Get daemon status.

        Args:
            None

        Returns:
            None

        """
        # Get status
        if os.path.exists(self.pidfile) is True:
            print('Daemon is running - {}'.format(self.name))
        else:
            print('Daemon is stopped - {}'.format(self.name))

    def run(self):
        """You should override this method when you subclass Daemon.

        It will be called after the process has been daemonized by
        start() or restart().
        """
        # Simple comment to pass linter
        pass


class GracefulDaemon(Daemon):
    """Daemon that allows for graceful shutdown

    This daemon should allow for stop/restart commands to perform graceful
    shutdown of a given process. A graceful shutdown involves checking that
    whether a current process is running and only ending the process once the
    current process has completed its currently running task.

    """
    class GracefulShutdown():
        """Facilities graceful shutdown during stop/restart daemon commands

        GracefulShutdown is a callable method which can be used as python
        decorator that can facilitate checks for a graceful stop/restart of a
        system daemon.

        """

        @staticmethod
        def __daemon_running(lock_file_name):
            """Determines if daemon is running

            Daemon is running based on whether it has an associated lockfile

            Args:
                None

            Return:
                running: True if daemon is currently running or conducing a process

            """
            running = False
            if lock_file_name is not None:
                if os.path.exists(lock_file_name) is True:
                    running = True

            return running

        def __call__(self, fn):
            """Wrapper class that handles graceful_shutdown prior to using
            callaback function `fn`

            Args:
                self: GracefulShutdown instance
                fn: callback method

            Return:
                wrapper

            """
            def wrapper(_self):
                """Wrapper function that facilitates graceful shutdown

                Args:
                    _self: daemon instance

                Return:
                    None

                """

                if self.__daemon_running(_self.lockfile):
                    log_message = '{} Lock file exists, Process still running'.format(_self.name)
                    log.log2info(1100, log_message)

                # Continually checks if daemon is still running
                # Exits loop once GRACEFUL_TIMEOUT limit reached
                # Indicating a failed attempt to gracefully shutdown
                timeout_counter = time.time()
                while True:

                    if not self.__daemon_running(_self.lockfile) is True:
                        log_message = 'Process {} no longer processing'.format(_self.name)
                        log.log2info(1101, log_message)

                        fn(_self) # method callback
                        break

                    # Checking whether GRACEFUL_TIMEOUT limit is reached
                    current_duration = time.time() - timeout_counter
                    if current_duration >= GRACEFUL_TIMEOUT:
                        log_message = 'Process {} failed to shutdown, DUE TO TIMEOUT'.format(_self.name)
                        log.log2info(1102, log_message)
                        break
            return wrapper

    def __init__(self, agent):
        """Initialize the class.

        Args:
            agent: Agent object

        Returns:
            None

        """
        # Creating unit using third-party dbus module pystemd
        self.unit = Unit('{}.service'.format(agent.name()))
        self.unit.load()

        # Manages active state based on agent script entry point
        self.is_active = 'inactive'

        # Daemon superclass instantiation
        Daemon.__init__(self, agent)

    def start(self):
        """Start GracefulDaemon

        Calls superclass start method only if related pidfile of daemon does not
        exist

        Args:
            None

        Return:
            None

        """
        if bool(self.pidfile and os.path.exists(self.pidfile)) is False:
            super(GracefulDaemon, self).start()
        else:
            log_message = 'Process {} already has PID file '.format(self.name)
            log.log2debug(1103, log_message)

        # Starting systemd service dbus unit object
        self.unit.Unit.Start(b'replace')

    @GracefulShutdown()
    def stop(self):
        """Stops the daemon gracefully.

        Uses parent class stop method after checking that daemon is no longer
        processing data or making use of a resource.

        Args:
            None

        Returns:
            None

        """
        super(GracefulDaemon, self).stop()

        # Changing systemd state to inactive
        self.unit.Unit.Stop(b'fail')

    @GracefulShutdown()
    def restart(self):
        """Restarts the daemon gracefully.

        Uses parent class restart method after checking that daemon is no longer
        processing data or making use of a resource.

        Args:
            None

        Returns:
            None

        """
        super(GracefulDaemon, self).restart()
