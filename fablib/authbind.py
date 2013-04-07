import os

from fabric.api import sudo

from fablib import package


def install():
    package.install('authbind')


def allow(user, port):
    path = os.path.join('/etc/authbind/byport', str(port))
    sudo('touch {}'.format(path))
    sudo('chown {0}:{0} {1}'.format(user, path))
    sudo('chmod 0500 {}'.format(path))
