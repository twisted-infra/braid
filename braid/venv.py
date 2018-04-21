from fabric.api import run, settings
from os import path


class VirtualEnvironment(object):

    def __init__(self, user, location="~/virtualenv", python="python2.7"):

        if python == "pypy":
            self._python = "~pypy/bin/pypy"
        elif python == "python2.7":
            self._python = "/usr/bin/python2.7"
        else:
            self._python = python

        self._location = location
        self._user = user


    def create(self, site_packages=False):
        """
        Create the virtualenv. This uses "/usr/bin/env python2"'s virtualenv
        module.
        """
        with settings(user=self._user):
            run(("/usr/bin/env python2 -m virtualenv --clear "
                 "-p {} {} {}").format(self._python, self._location,
                                       '--system-site-packages' if site_packages else ''))

        # https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning
        self.install("-U pip")
        self.install("requests[security]")
        # We need to force setuptools, as otherwise it might use the old
        self.install("-U setuptools wheel")


    def install(self, package):
        """
        Install a package into the virtualenv. It updates if there is a newer
        matching version -- you should pin your dependencies if this is a
        concern.
        """
        with settings(user=self._user):
            pip = path.join(self._location, "bin", "pip")
            run("{} install {}".format(pip, package), pty=False)

    def install_twisted(self):
        """
        Install Twisted and its dependencies.
        """
        self.install(" ".join("""
            acme==0.23.0
            asn1crypto==0.24.0
            attrs==17.4.0
            automat==0.6.0
            certifi==2018.4.16
            cffi==1.11.5
            chardet==3.0.4
            constantly==15.1.0
            cryptography==2.2.2
            eliot==1.3.0
            enum34==1.1.6
            funcsigs==1.0.2
            h2==3.0.1
            hpack==3.0.0
            hyperframe==5.1.0
            hyperlink==18.0.0
            idna==2.6
            incremental==17.5.0
            ipaddress==1.0.22
            josepy==1.1.0
            mock==2.0.0
            pbr==4.0.2
            pem==17.1.0
            priority==1.3.0
            pyasn1-modules==0.2.1
            pyasn1==0.4.2
            pycparser==2.18
            pyopenssl==17.5.0
            pyrfc3339==1.0
            pyrsistent==0.14.2
            pytz==2018.4
            requests[security]==2.18.4
            service-identity==17.0.0
            six==1.11.0
            treq==17.8.0
            twisted[tls]==18.4.0pre1
            txacme==0.9.2
            txsni==0.1.9
            urllib3==1.22
            zope.interface==4.5.0
        """.split()))

    def run(self, arg):
        with settings(user=self._user):
            run("{} {}".format(path.join(self._location, "bin", "python"), arg))
