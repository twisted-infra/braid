from twisted.application import service, strports
from buildbot.master import BuildMaster
from twisted.web import server, resource
from twisted.internet import endpoints

from os.path import expanduser
from twisted.python.util import sibpath

basedir = expanduser('~/data')
configfile = sibpath(__file__, 'master.cfg')

multiServe = service.MultiService()

bbApp = BuildMaster(basedir, configfile)
multiServe.addService(bbApp)


class Redirect(resource.Resource):

    isLeaf = True

    def render(self, request):
        request.redirect("https" + request.prePathURL()[4:-1] + request.uri)
        return b""


site = server.Site(Redirect())
redirector = strports.service("tcp:80", site)
redirector.setName('redirector')
multiServe.addService(redirector)

application = service.Application('buildmaster')
multiServe.setServiceParent(application)
