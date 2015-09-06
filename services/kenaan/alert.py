
from twisted.internet import reactor
from twisted.spread import pb
from twisted.python import log

import config

class Alert(pb.Copyable, pb.RemoteCopy):
    def __init__(self, hostname, service, returncode, output):
        self.hostname = hostname
        self.service = service
        self.returncode = returncode
        self.output = output

    def __repr__(self):
        return 'Alert(%r, %r, %r, %r)' % (
            self.hostname, self.service,
            self.returncode, self.output)
pb.setUnjellyableForClass(Alert, Alert)

class MuninAlertListener:
    """
    Mixin for a PB Referenceable which accepts Munin alerts.
    """
    def remote_alert(self, alert):
        self.proto.alert(alert)


class MuninAlert:
    alertMessageFormat = (
        'Alert from %(hostname)s [%(service)s]: %(output)s')

    def alert(self, alert):
        self.join(config.ALERT_CHANNEL)
        self.msg(
            config.ALERT_CHANNEL,
            self.alertMessageFormat % vars(alert),
            config.LINE_LENGTH)

def _sendAlert(alert):
    cf = pb.PBClientFactory()
    reactor.connectTCP(config.BOT_HOST, config.BOT_PORT, cf)

    def cbRoot(rootObj):
        return rootObj.callRemote('alert', alert)

    rootD = cf.getRootObject()
    rootD.addCallback(cbRoot)
    rootD.addErrback(log.err)
    rootD.addCallback(lambda ign: reactor.stop())

def main(alerts):
    reactor.callWhenRunning(lambda: [_sendAlert(Alert(hostname, service, returncode, output))
                                       for (hostname, service, returncode, output) in alerts])
    reactor.run()
