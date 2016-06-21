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


    def install(self, package):
        """
        Install a package into the virtualenv. It updates if there is a newer
        matching version -- you should pin your dependencies if this is a
        concern.
        """
        with settings(user=self._user):
            pip = path.join(self._location, "bin", "pip")
            run("{} install -U {}".format(pip, package), pty=False)

    def install_twisted(self):
        """
        Install Twisted and its dependencies.
        """
        self.install(("Twisted==16.2.0 "
                      "pyOpenSSL==16.0 "
                      "service_identity==14.0 "
                      "txsni==0.1.5"))

    def run(self, arg):
        with settings(user=self._user):
            run("{} {}".format(path.join(self._location, "bin", "python"), arg))
