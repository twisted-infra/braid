from twisted.python import log
from twisted.web.client import getPage
from twisted.application import service

from twisted.application.internet import TimerService

class TracMonitor(service.MultiService):
    def __init__(self, restartCallback, checkInterval, tracURL, timeout):
        service.MultiService.__init__(self)
        self._restartCallback = restartCallback
        self._tracURL = tracURL
        self._timeout = timeout
        TimerService(checkInterval, self.check).setServiceParent(self)

    def restart(self, f):
        log.err(f, 'accessing trac.')
        log.msg('restarting trac.')
        self._restartCallback()

    def check(self):
        return (getPage(self._tracURL, timeout=self._timeout)
                .addErrback(self.restart))
