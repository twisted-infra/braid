#!/usr/bin/twistd-service

### BEGIN INIT INFO
# Provides:          dns
# Required-Start:    $syslog $named $network $time
# Required-Stop:     $syslog $named $network
# Should-Start:
# Should-Stop:
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Twisted DNS server
# Description:       dns is a DNS server based on Twisted Names
### END INIT INFO

TWISTD='authbind --deep twistd'
SERVICE='dns'
ARGS='dns'
