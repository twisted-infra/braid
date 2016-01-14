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


    def create(self):
        """
        Create the virtualenv. This uses "/usr/bin/env python2"'s virtualenv
        module.
        """
        with settings(user=self._user):
            run(("/usr/bin/env python2 -m virtualenv --clear "
                 "-p {} {}").format(self._python, self._location))

        # https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning
        self.install("ndg-httpsclient")
        self.install("pip")
        self.install("setuptools")
        self.install("wheel")


    def install(self, package):
        """
        Install a package into the virtualenv. It updates if there is a newer
        matching version -- you should pin your dependencies if this is a
        concern.
        """
        with settings(user=self._user):
            run("{} -m pip install -U {}".format(
                path.join(self._location, "bin", "python"), package), pty=False)

    def install_twisted(self):
        """
        Install Twisted and its dependencies.
        """
        self.install("Twisted==15.5")
        self.install("pyOpenSSL==0.15.1")
        self.install("service_identity==14.0")
        self.install("txsni==0.1.5")

    def run(self, arg):
        with settings(user=self._user):
            run("{} {}".format(path.join(self._location, "bin", "python"), arg))
