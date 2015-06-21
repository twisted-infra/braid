from functools import partial
from twisted.application import service, internet
from twisted.internet.protocol import ReconnectingClientFactory

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
del sys, os

import private as config
from commit_bot import CommitBot

application = service.Application('kenaan')

factory = ReconnectingClientFactory.forProtocol(
		partial(CommitBot, nickname=config.BOT_NICK, password=config.BOT_PASS))

svc = internet.TCPClient(config.IRC_SERVER, config.IRC_PORT, factory)
svc.setServiceParent(application)
