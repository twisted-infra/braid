import urlparse

from twisted.internet.endpoints import UNIXClientEndpoint
from twisted.web.resource import Resource
from twisted.web.proxy import ProxyClientFactory
from twisted.web.server import NOT_DONE_YET
from twisted.python.urlpath import URLPath
from twisted.python.log import err

class ReverseProxyResource(Resource):
    """
    Resource that renders the results gotten from another server

    Put this resource in the tree to cause everything below it to be relayed
    to a different server.

    @ivar proxyClientFactoryClass: a proxy client factory class, used to create
        new connections.
    @type proxyClientFactoryClass: L{ClientFactory}

    @ivar reactor: the reactor used to create connections.
    @type reactor: object providing L{twisted.internet.interfaces.IReactorTCP}
    """

    proxyClientFactoryClass = ProxyClientFactory


    def __init__(self, endpoint, url):
        """
        @param url: the base path to fetch data from. Note that you shouldn't
            put any trailing slashes in it, it will be added automatically in
            request. For example, if you put B{/foo}, a request on B{/bar} will
            be proxied to B{/foo/bar}.  Any required encoding of special
            characters (such as " " or "/") should have been done already.

        @type path: C{str}
        """
        Resource.__init__(self)
        self.endpoint = endpoint
        self.url = url


    def getChild(self, path, request):
        """
        Create and return a proxy resource with the same proxy configuration
        as this one, except that its path also contains the segment given by
        C{path} at the end.
        """
        return ReverseProxyResource(self.endpoint, self.url.child(path))


    def render(self, request):
        """
        Render a request by forwarding it to the proxied server.
        """
        request.received_headers['host'] = 'twistedmatrix.com'
        request.content.seek(0, 0)
        rest = '/frack/'
        clientFactory = self.proxyClientFactoryClass(
            request.method, rest, request.clientproto,
            request.getAllHeaders(), request.content.read(), request)
        d = self.endpoint.connect(clientFactory)
        d.addErrback(
            lambda reason:
                (err(reason, "Frack Proxy Connection Error"),
                 clientFactory.clientConnectionFailed(None, reason)))
        return NOT_DONE_YET

def getFrackResource(reactor):
    return ReverseProxyResource(
        UNIXClientEndpoint(reactor, path='/var/run/frack/json.sock'),
        URLPath("http://twistedmatrix.com/"))
