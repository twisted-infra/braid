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
        self.install("pip")
        self.install("requests[security]")
        self.install("setuptools wheel")


    def remove(self):
        """
        Remove the virtualenv.
        """
        with settings(user=self._user):
            run("rm -rf {}".format(self._location))


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
            attrs==16.3.0
            cffi==1.9.1
            constantly==15.1.0
            cryptography==1.8.1
            enum34==1.1.6
            h2==2.5.1
            hpack==2.3.0
            hyperframe==4.0.1
            idna==2.1
            incremental==16.10.1
            ipaddress==1.0.17
            priority==1.2.2
            pyasn1==0.1.9
            pyasn1-modules==0.0.8
            pycparser==2.17
            pyOpenSSL==16.2.0
            service-identity==16.0.0
            six==1.10.0
            Twisted==17.1.0
            txacme==0.9.1
            zope.interface==4.3.2
        """.split()))

    def run(self, arg):
        with settings(user=self._user):
            run("{} {}".format(path.join(self._location, "bin", "python"), arg))
