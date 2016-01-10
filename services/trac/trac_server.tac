# Insert config dir into python path.
import sys
from os import path
config = path.dirname(__file__)

sys.path.insert(0, config)

from external import TracResource, RootResource

from twisted.application.service import Application
from twisted.application.internet import TCPServer

application = Application('Trac')

from twisted.internet import reactor

from twisted.web.server import Site
from twisted.python.threadpool import ThreadPool


threadpool = ThreadPool(name="trac")
reactor.callWhenRunning(threadpool.start)
reactor.addSystemEventTrigger("during", "shutdown", threadpool.stop)
tracResource = TracResource(reactor, threadpool, path.join(config, 'htpasswd'),
                            path.join(config, 'trac-env'))
htdocs = path.join(config, "trac-env/htdocs")
attachments = path.join(config, "trac-env/attachments")
root = RootResource(tracResource, htdocs, attachments)
site = Site(root, logPath=path.expanduser("~/log/httpd.log"))
TCPServer(9881, site, interface="127.0.0.1").setServiceParent(application)
