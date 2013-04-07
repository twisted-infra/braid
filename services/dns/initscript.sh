#!/usr/bin/twistd-service

### BEGIN INIT INFO
# Provides:          dns
# Required-Start:    $named $network $time
# Required-Stop:     $named $network
# Should-Start:
# Should-Stop:
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Twisted DNS server
# Description:       dns is a DNS server based on Twisted Names
### END INIT INFO

# TODO: Check required start and required stop

TWISTD='authbind --deep twistd'
SERVICE='dns'
ARGS='dns'
