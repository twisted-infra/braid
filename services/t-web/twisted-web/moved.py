
from twisted.web.http import MOVED_PERMANENTLY
from twisted.web.util import ChildRedirector

def movedTo(request, url):
    request.setResponseCode(MOVED_PERMANENTLY)
    request.setHeader("location", url)
    return """
<html>
    <head>
        <meta http-equiv=\"refresh\" content=\"0;URL=%(url)s\">
    </head>
    <body bgcolor=\"#FFFFFF\" text=\"#000000\">
    <a href=\"%(url)s\">click here</a>
    </body>
</html>
""" % {'url': url}



class Moved(ChildRedirector):
    """
    Resource which issues a moved permanently redirect in response to any
    request.
    """
    def render(self, request):
        return movedTo(request, self.url)
