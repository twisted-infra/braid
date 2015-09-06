
from twisted.python.log import err
from twisted.internet import reactor
from twisted.spread.pb import PBClientFactory

from config import BOT_HOST, BOT_PORT, LINE_LENGTH

class MessageListener:
    """
    Mixin for a PB Referenceable which accepts arbitrary messages.
    """
    def remote_message(self, channel, message):
        """
        Forward the given message to C{self.proto}.
        """
        self.proto.message(channel, message)



class Message:
    def message(self, channel, message):
        if channel.startswith('#'):
            self.join(channel)
        self.msg(channel, message, LINE_LENGTH)



def _sendMessage(channel, message):
    """
    Establish a connection to the bot and direct it to send the given message
    to the given channel.

    @type channel: C{str}
    @type message: C{str}
    """
    messageFactory = PBClientFactory()
    reactor.connectTCP(BOT_HOST, BOT_PORT, messageFactory)

    def cbGotRoot(rootObj):
        return rootObj.callRemote('message', channel, message)

    rootDeferred = messageFactory.getRootObject()
    rootDeferred.addCallback(cbGotRoot)
    rootDeferred.addErrback(err)
    rootDeferred.addCallback(lambda ign: reactor.stop())

def main(channel, message):
    """
    Send the given message to the given channel and run the reactor until it's
    sent.

    @type channel: C{str}
    @type message: C{str}
    """
    reactor.callWhenRunning(_sendMessage, channel, message)
    reactor.run()

