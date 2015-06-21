from twisted.protocols import http
from twisted.web import resource, util, error, twcgi, static

from twisted.web import server

import string, os, urllib

class EnvableCGIThing(twcgi.CGIScript):
    def __init__(self, filename, env):
        twcgi.CGIScript.__init__(self, filename)
        self.env = env

    #GAH HUGE RAPE'N'PASTE
    def render(self, request):
        script_name = "/"+string.join(request.prepath, '/')
        serverName = string.split(request.getRequestHostname(), ':')[0]
        env = {"SERVER_SOFTWARE":   server.version,
               "SERVER_NAME":       serverName,
               "GATEWAY_INTERFACE": "CGI/1.1",
               "SERVER_PROTOCOL":   request.clientproto,
               "SERVER_PORT":       str(request.getHost()[2]),
               "REQUEST_METHOD":    request.method,
               "SCRIPT_NAME":       script_name, # XXX
               "SCRIPT_FILENAME":   self.filename,
               "REQUEST_URI":       request.uri,

               # CGI is stupid who came up with this idea
               "HOME":              '/var/www',
        }
        env.update(self.env)
        

        client = request.getClient()
        if client is not None:
            env['REMOTE_HOST'] = client
        ip = request.getClientIP()
        if ip is not None:
            env['REMOTE_ADDR'] = ip
        pp = request.postpath
        if pp:
            env["PATH_INFO"] = "/"+string.join(pp, '/')

        qindex = string.find(request.uri, '?')
        if qindex != -1:
            qs = env['QUERY_STRING'] = request.uri[qindex+1:]
            if '=' in qs:
                qargs = []
            else:
                qargs = [urllib.unquote(x) for x in qs.split('+')]
        else:
            env['QUERY_STRING'] = ''
            qargs = []

        # Propogate HTTP headers
        for title, header in request.getAllHeaders().items():
            envname = string.upper(string.replace(title, '-', '_'))
            if title not in ('content-type', 'content-length'):
                envname = "HTTP_" + envname
            env[envname] = header
        # Propogate our environment
        for key, value in os.environ.items():
            if not env.has_key(key):
                env[key] = value
        # And they're off!
        self.runProcess(env, request, qargs)
        return server.NOT_DONE_YET




class BasicAuthWrapper(resource.Resource):
    def __init__(self, cgifile, env=None, basicRealm="foo"):
        if env is None: env = {}
        self.env = env
        resource.Resource.__init__(self)
        self.cgifile = cgifile
        self.basicRealm = basicRealm

    def getChild(self, path, request):
        request.postpath.insert(0,request.prepath.pop())
        env = self.env.copy()
        username = request.getUser()
        password = request.getPassword()

        if username:
            import md5crypt
            authdb = list(file('/var/www/trac.htpasswd'))
            for ent in authdb:
                u, p = ent.split(':', 1)
                if u == username:
                    print 'Found username', u, 'in auth db'
                    parts = p.split('$', 2)
                    print 'Found salt', parts[1], 'in md5'
                    if md5crypt.md5crypt(password, parts[1]) != p:
                        print 'It is a bad liar'
                        username = ''
                    else:
                        print 'Yay victory'
                break
            else:
                username = ''

        if request.postpath == ['login']:
            if not username:
                return BasicAuthError(http.UNAUTHORIZED,
                                      "Unauthorized",
                                      "401 Authentication required",
                                      self.basicRealm)
            return util.Redirect("/trac/")
        env['REMOTE_USER'] = username
        return EnvableCGIThing(self.cgifile, env=env)

    def render(self, request):
        return EnvableCGIThing(self.cgifile, env=self.env).render(request)

class BasicAuthError(error.ErrorPage):

    def __init__(self, status, brief, detail, basicRealm="default"):
        error.ErrorPage.__init__(self, status, brief, detail)
        self.basicRealm = basicRealm

    def render(self, request):
        request.setHeader('WWW-authenticate',
                          'Basic realm="%s"' % self.basicRealm)
        return error.ErrorPage.render(self, request)

