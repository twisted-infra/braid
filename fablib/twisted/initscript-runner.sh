#!/bin/bash

# This file provides a utility similar to Gentoo's 'runscript' to create
# 'twistd' specific initscript with the less possible amount of work.
# To create an initscript for a twistd service, simply create an executable
# file and use the following interpreter declaration:
#
#    #!/usr/bin/twistd-service
#
# (naturally, this file has to be placed at the above location or the line
# has to be adapted).
#
# The minimal content of the initscript is a SERVICE variable which sets the
# path for execution (/srv/$SERVICE), pidfile (/srv/$SERVICE/var/run/$SERVICE.pid),
# and logfile (/srv/$SERVICE/var/log/$SERVICE.log) and an ARGS variable which
# contains the service specification to be passed to 'twistd'.
# 
# Additional customization can be provided by either redefining other variables
# or functions as described through this script.


# {{{ Variables definition
#
# Define default configuration data. These can be overridden by the
# initscript.

TWISTD=twistd         # Service executable

SIGTERM_ATTEMPTS=5    # Number of TERM signals to send before KILLing
                      # the service

STARTUP_DELAY=1       # Seconds to wait before checking if the service
                      # correctly started (i.e. pidfile created)

SHUTDOWN_DELAY=1      # Seconds to wait before checking if the service
                      # correctly stopped (i.e. pidfile removed)

ALLOWED_ACTIONS='start|stop|restart|status|zap'
                      # A |-separated list of actions this script accepts.
                      # This can be extended in the iniscript by defining
                      # the ADDITIONAL_ACTIONS variable using the same
                      # syntax.

# }}}


# {{{ Utilities
#
# Utility functions which can be used either in this script or in the
# initscript itself to implement the required functionalities.

echoerr() {
	# Echo to stderr.
	echo "$@" 1>&2
}

function running() {
	# Check if the process is running by looking are the pidfile. If the
	# pidfile exists and contains a pid but the corresponding process does
	# not exist, we consider that it has crashed.
	_get_pidfile
	_get_user
	local pid=$(sudo -u $RUNAS cat "$PIDFILE" 2>/dev/null)

	if [ -z "$pid" ] ; then
		return 1  # No pid defined, process stopped
	elif sudo -u $RUNAS kill -0 $pid ; then
		return 0  # Pid defined and process killable, still running
	else
		return 2  # Pid defined but process not killable, crashed
	fi
}

function crashed() {
	# Simple boolean wrapper for 'running' which succeeds if the process
	# crashed (see the description of 'running' for the definition of
	# 'crashed').
	running
	if [ $? = "2" ] ; then
		return 0
	else
		return 1
	fi
}

function start_twistd() {
	# Start the twistd service if it is not running and has not crashed.
	# This function gets the pidfile and logfile locations from the environemnt
	# and exits with an error if they are not defined or cannot be inferred.
	# If the SERVICE environment variable, also sets the rundir, uid, and gid
	# arguments for the twistd executable.
	# This function also checks that the service was correctly started.
	if running ; then
		echo " * Service already running"
		return
	fi

	if crashed ; then
		echo " * Service crashed"
		return
	fi

	echo " * Starting twistd $@..."
	
	_get_pidfile
	_get_logfile
	_get_user

	local pidfile="--pidfile=$PIDFILE"
	local logfile="--logfile=$LOGFILE"

	if [ ! -z "$SERVICE" ] ; then
		local rundir="--rundir=$(_get_prefix)"
	fi

	local cmd="$venv $TWISTD $pidfile $logfile $rundir $uid $gid $@"

	sudo -u $RUNAS /bin/bash -c "source $(_get_prefix)/venv/bin/activate && $cmd"
	
	if [ $? = "0" ] ; then
		sleep $STARTUP_DELAY
		if running ; then
			echo " * Service started (pid=$(sudo -u $RUNAS cat "$PIDFILE" 2>/dev/null))"
		else
			echo " * Service failed to start (exit code was 0!)"
			echo "   (logfile saved to $LOGFILE)"
		fi
	else
		echo " * Service failed to start (logfile saved to $LOGFILE)"
		exit 1
	fi
}

function stop_twistd() {
	# Stop the twistd service if it is running. This functions sends up to
	# SIGTERM_ATTEMPTS term signals by waiting SHUTDOWN_DELAY between them
	# and checking if the service is still running. If after the maximum
	# number of attempts the process is still running, then it is killed
	if running ; then
		_get_pidfile
		_get_user
		local pid=$(sudo -u $RUNAS cat "$PIDFILE" 2>/dev/null)

		echo " * Stopping service..."
		sudo -u $RUNAS kill $pid
		sleep $SHUTDOWN_DELAY
		
		for i in $(seq $SIGTERM_ATTEMPTS) ; do
			if running ; then
				echo " * Still running..."
				sudo -u $RUNAS kill $pid
				sleep $SHUTDOWN_DELAY
			else
				echo " * Service stopped"
				break;
			fi
		done

		if running ; then
			echo " * Killing..."
			sudo -u $RUNAS kill -9 $pid
			rm -f $PIDFILE
		fi
	else
		echo " * Service not running"
	fi
}

# }}}


# {{{ Private API
#
# Private interface functions. These are to be used in this file only and
# provide different functionality to deal with the options the developer
# has to specifcy the environemnt and actions in the initscript.

function _check_service() {
	# Check that the SERVICE environment variable is defined and
	# raise an error otherwise.
	if [ -z "$SERVICE" ] ; then
		echoerr "Please define the SERVICE or $1 variable in your initscript."
		exit 1
	fi
}

function _get_pidfile() {
	# If the PIDFILE variable is not explicitly set, construct it using the
	# SERVICE variable.
	if [ -z "$PIDFILE" ] ; then
		_check_service 'PIDFILE'
		PIDFILE="$(_get_prefix)/var/run/$SERVICE.pid"
	fi
}

function _get_logfile() {
	# If the LOGFILE variable is not explicitly set, construct it using the
	# SERVICE variable.
	if [ -z "$LOGFILE" ] ; then
		_check_service 'LOGFILE'
		LOGFILE="$(_get_prefix)/var/log/$SERVICE.log"
	fi
}

function _get_user() {
	# If the RUNAS variable is not explicitly set, construct it using the
	# SERVICE variable.
	if [ -z "$RUNAS" ] ; then
		_check_service 'RUNAS'
		RUNAS="$SERVICE"
	fi
}

function _get_prefix() {
	# Echoes the prefix of the service instance. This is meant as a single
	# location where this behavior can be changed (e.g. to use this script
	# for a twistd instance installed at /.
	echo "/srv/$SERVICE"
}

# }}}


# {{{ Public API
#
# Public interface functions. These provide the basic functionality and
# are meant to be overridden in the initscript if the service requires
# specific behviors.

function start() {
	# Run the twistd daemon by loading all configuration from environment
	# variables. This function requires the ARGS environment variable to
	# be set and non-empty.
	if [ -z "$ARGS" ] ; then
		echoerr "Please define the ARGS variable or implement the 'start' function in your initscript."
		exit 1
	fi
	start_twistd $ARGS
}

function stop() {
	# Stop the twistd daemon by getting the location of the pidfile from
	# the environment variables.
	stop_twistd
}

function restart() {
	# Implementation of the simplest restarting functionality: stop and
	# start again
	stop ; start
}

function status() {
	# Print the running status of the service and exit.
	running
	case $? in
		0)
			echo " * Running"
			;;
		1)
			echo " * Stopped"
			;;
		2)
			echo " * Crashed"
			;;
		*)
			echo " * Unknown status"
			exit 1
	esac
}

function zap() {
	# Reset the status of the service to stopped if it is currently crashed.
	if crashed ; then
		_get_pidfile
		rm -f $PIDFILE
		echo " * Service reset to stopped state"
	fi
}

# }}}


# {{{ Script execution
#
# Ok, everything is set up. Let's run all this stuff...

# ...parse command line arguments
INITSCRIPT=$1
COMMAND=$2

# ...load service specific initscript
source $INITSCRIPT

# ...build the list of allowed actions
if [ ! -z "$ADDITIONAL_ACTIONS" ] ; then
	ALLOWED_ACTIONS="$ALLOWED_ACTIONS|$ADDITIONAL_ACTIONS"
fi
ALLOWED_PATTERN='+('$ALLOWED_ACTIONS')'

# ...execute requested action if it matches the pattern
shopt -s extglob
case $COMMAND in
	$ALLOWED_PATTERN)
		$COMMAND
		exit $?
		;;
	*)
		echo "Usage $INITSCRIPT {$ALLOWED_ACTIONS}"
		exit 1
esac

# }}}
