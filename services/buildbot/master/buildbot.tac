#
# Twisted Application used to launch the Buildbot Master instance.
#
# Beside starting the main Buildbot application, it also starts a redirector
# from HTTP on port 80 to HTTPS on port default port 443.
#
from hyperlink import URL
from twisted.internet import reactor
from twisted.web import http, static
from twisted.application import service, strports
from buildbot.master import BuildMaster

from twisted.python import filepath
from twisted.web import server, resource

from os.path import expanduser

from josepy.jwa import RS256

from txacme.challenges import HTTP01Responder
from txacme.client import Client
from txacme.endpoint import load_or_create_client_key
from txacme.service import AcmeIssuingService
from txacme.store import DirectoryStore
from txacme.urls import LETSENCRYPT_DIRECTORY


basedir = expanduser('~/data')
configfile = filepath.FilePath(__file__).sibling('master.cfg')

multiServe = service.MultiService()

bbApp = BuildMaster(basedir, configfile.path)
multiServe.addService(bbApp)


def movedTo(request, url, encoding):
    """
    Permanently redirect C{request} to C{url}.

    @param request: The L{twisted.web.server.Reqeuest} to redirect.

    @param url: The new URL to which to redirect the request.
    @type url: L{bytes}

    @param encoding: The encoding of the response as a byte string.
    @type encoding: L{bytes}

    @return: The redirect HTML page.
    @rtype: L{bytes}
    """
    request.setResponseCode(http.MOVED_PERMANENTLY)
    request.setHeader(b"location", url)
    return (b"""
<html>
  <head>
    <meta charset="%(charset)s" http-equiv="refresh" content="0;URL=%(url)s">
  </head>
  <body bgcolor="#FFFFFF" text="#000000">
  <a href="%(url)s">click here</a>
  </body>
</html>
""" % {b'charset': encoding, b'url': url})


class RespondToHTTP01AndRedirectToHTTPS(resource.Resource):
    """
    Allow an L{HTTP01Responder} to handle requests for
    C{.well_known/acme-challenges} only.  Redirect any other requests
    to their HTTPS equivalent.
    """
    def __init__(self, responderResource):
        resource.Resource.__init__(self)
        wellKnown = resource.Resource()
        wellKnown.putChild(b'acme-challenge', responderResource)
        self.putChild(b'.well-known', wellKnown)
        self.putChild(b'check', static.Data(b'OK', b'text/plain'))

    def render(self, request):
        # request.args can include URL encoded bodies, so extract the
        # query from request.uri
        _, _, query = request.uri.partition(b'?')
        # Assume HTTPS is served over 443
        httpsURL = URL(
            scheme=u'https',
            # I'm sure ASCII will be fine for hostnames.
            host=request.getRequestHostname().decode('ascii'),
            path=tuple(segment.decode('utf-8')
                       for segment in request.prepath + request.postpath),

        )
        httpsLocation = httpsURL.asText().encode('utf-8')
        if query:
            httpsLocation += (b'?' + query)
        return movedTo(request, httpsLocation, encoding=b'UTF-8')

    def getChild(self, path, request):
        return self


txacmeResponder = HTTP01Responder()
certificates = filepath.FilePath('/srv/bb-master/config/certs')
issuingService = AcmeIssuingService(
    cert_store=DirectoryStore(certificates),
    client_creator=(lambda: Client.from_url(
        reactor=reactor,
        url=LETSENCRYPT_DIRECTORY,
        key=load_or_create_client_key(certificates),
        alg=RS256,
    )),
    clock=reactor,
    responders=[txacmeResponder],
)
multiServe.addService(issuingService)

LOG_PATH = expanduser('~/log/httpd.log')
site = server.Site(
    RespondToHTTP01AndRedirectToHTTPS(txacmeResponder.resource),
    logPath=LOG_PATH,
)
redirector = strports.service("tcp:80", site)
redirector.setName('redirector')
multiServe.addService(redirector)

application = service.Application('buildmaster')
multiServe.setServiceParent(application)
