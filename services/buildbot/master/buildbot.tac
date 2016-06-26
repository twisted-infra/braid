#
# Twisted Application used to launch the Buildbot Master instance.
#
# Beside starting the main Buildbot application, it also starts a redirector
# from HTTP on port 80 to HTTPS on port default port 443.
#
from twisted.application import service, strports
from buildbot.master import BuildMaster
from twisted.web import server, resource

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


# Redirect HTTP port to HTTPS.
site = server.Site(Redirect())
redirector = strports.service("tcp:80", site)
redirector.setName('redirector')
multiServe.addService(redirector)

application = service.Application('buildmaster')
multiServe.setServiceParent(application)
