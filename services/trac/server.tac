import os
from os.path import expanduser
import socket

from twisted.application import service
from twisted.runner import procmon

import sys
from os.path import dirname
sys.path.insert(0, dirname(__file__))

from monitor import TracMonitor
import postcommit


TRAC_URL = 'https://twistedmatrix.com/trac/'
TRAC_TIMEOUT = 30
CHECK_INTERVAL = 30

VCS_SERVER = socket.gethostbyname('svn.twistedmatrix.com')
HOOK_PATH = expanduser('~/config/trac-post-commit-hook')
ENV_PATH = expanduser('~/config/trac-env')
COMMIT_SERVER_PORT = 38159

application = service.Application('trac')

# Setup trac server process monitor
processMonitor = procmon.ProcessMonitor()
processMonitor.addProcess('trac-server', [
    'twistd',
    '--reactor', 'epoll',
    '--logfile', expanduser('~/log/trac-twistd.log'),
    '--pidfile', expanduser('~/run/trac-twistd.pid'),
    '--rundir', expanduser('~/run/'),
    '--python', expanduser('~/config/trac_server.tac'),
    '--nodaemon',
], env=os.environ)
processMonitor.setServiceParent(application)

def restartTrac():
    processMonitor.stopProcess('trac-server')

# Setup monitoring service
(TracMonitor(restartTrac, CHECK_INTERVAL, TRAC_URL, TRAC_TIMEOUT)
    .setServiceParent(application))

(postcommit.service(VCS_SERVER, HOOK_PATH, ENV_PATH, TRAC_URL, COMMIT_SERVER_PORT)
    .setServiceParent(application))
