# DynamicSite:
# A virtual hosting twisted.web2 HTTP server that uses subdirectories for
# virtual host content. Subdirectories can be python packages providing dynamic
# content with a root resource object, or sources of static content.
#
# Copyright (C) 2006 by Edwin A. Suominen, http://www.eepatents.com
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the file COPYING for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

"""
Provides C{twisted.web.resource.Resource} implementations for various external
web resources.
"""

import trac.web.main
import trac.web.standalone

from twisted.web.wsgi import WSGIResource
from twisted.web.static import File
from twisted.web.resource import Resource



class TwistedAuthenticator(trac.web.auth.BasicAuthentication):

    def test(self, user, password):
        # Re-load the password file because it might have changed since we loaded it.
        self.check_reload()

        the_hash = self.hash.get(user)
        if the_hash is None:
            return False

        return trac.web.auth.BasicAuthentication.test(self, user, password)



class AuthenticationMiddleware(object):

    def __init__(self, application, auths):
        self.application = application
        self.auths = auths

    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '')
        path_parts = filter(None, path_info.split('/'))
        if path_parts and path_parts[0] == 'login':
            env_name = path_parts[0]
            if env_name:
                auth = self.auths.get(env_name, self.auths.get('*'))
                if auth:
                    remote_user = auth.do_auth(environ, start_response)
                    if not remote_user:
                        return []
                    environ['REMOTE_USER'] = remote_user
        return self.application(environ, start_response)



class TracMixin:
    def middleware_auth(self, application):
        auths = {
            'twisted': TwistedAuthenticator(self.htpasswd, 'trac'),
            '*': TwistedAuthenticator(self.htpasswd, 'trac')}
        return AuthenticationMiddleware(
            application, auths)


    def tracApplication(self, environ, start_response):
        """
        This method is the callable object that provides access to my
        particular Trac environment via WSGI.
        """
        environ['trac.env_path'] = self.path
        environ['trac.base_url'] = 'https://twistedmatrix.com/trac'
        return trac.web.main.dispatch_request(environ, start_response)



class RootResource(Resource):

    def __init__(self, tracResource, htdocs, attachments):
        Resource.__init__(self)
        self.tracResource = tracResource
        self.htdocs = htdocs
        self.attachments = attachments


    def getChildWithDefault(self, name, request):
        if name != "trac":
            return File("/dev/null")
        if request.postpath and request.postpath[:1] == ["chrome"]:
            request.postpath.pop(0)
            return File(self.htdocs)
        else:
            return self.tracResource



class TracResource(WSGIResource, TracMixin):

    def __init__(self, reactor, threadpool, htpasswd, path):
        self.htpasswd = htpasswd
        self.path = path
        WSGIResource.__init__(
            self, reactor, threadpool, self.middleware_auth(
                self.tracApplication))



__all__ = ['RootResource', 'TracResource']
