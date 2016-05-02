from twisted.words.protocols import irc
from twisted.internet import reactor
from twisted.spread import pb

import config

# XXX Plugins or something, jeez stupid.
import ticket, alert, message

class Notifications(pb.Root, ticket.TicketChangeListener, alert.MuninAlertListener, message.MessageListener):
    def __init__(self, proto):
        self.proto = proto


class CommitBot(irc.IRCClient, ticket.TicketChange, ticket.TicketReview, alert.MuninAlert, message.Message):

    lineRate = config.LINE_RATE

    notificationPort = None

    def __init__(self, nickname, password):
        self.nickname = nickname
        self.password = password

    def connectionLost(self, reason):
        if self.notificationPort is not None:
            self.notificationPort.stopListening()

        for cls in self.__class__.__bases__[1:]:
            try:
                f = cls.connectionLost
            except AttributeError:
                pass
            else:
                f(self, reason)


    def signedOn(self):
        self.factory.resetDelay()
        sf = pb.PBServerFactory(Notifications(self))
        self.notificationPort = reactor.listenTCP(
            config.BOT_PORT, sf)

        for cls in self.__class__.__bases__[1:]:
            try:
                f = cls.signedOn
            except AttributeError:
                pass
            else:
                f(self)


    def noticed(self, user, channel, message):
        pass


    def privmsg(self, user, channel, message):
        for cls in self.__class__.__bases__[1:]:
            try:
                f = cls.privmsg
            except AttributeError:
                pass
            else:
                f(self, user, channel, message)
