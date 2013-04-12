#!/usr/bin/twistd-service

### BEGIN INIT INFO
# Provides:          trac
# Required-Start:    $named $network $time
# Required-Stop:     $named $network
# Should-Start:
# Should-Stop:
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Twisted Trac server
# Description:       Twisted's version of Trac
### END INIT INFO

# TODO: Check required start and required stop

export PYTHONPATH="/srv/trac/trac-env/deploy:$PYTHONPATH"

TWISTD='authbind --deep twistd'
SERVICE='trac'
ARGS='web --wsgi trac_wsgi.application --port 80'
