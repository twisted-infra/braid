import os

from fabric.api import sudo, run, abort

from braid import package, hasSudoCapabilities


def install():
    package.install('authbind')


def allow(user, port):
    path = os.path.join('/etc/authbind/byport', str(port))
    state = run('stat -c %U:%a {}'.format(path))
    if state.strip().split(':') != (user, '500'):
        if not hasSudoCapabilities():
            abort('Trying to give {} access to port {} but have insufficient '
                  'capabilities.'.format(user, port))
        sudo('touch {}'.format(path))
        sudo('chown {0}:{0} {1}'.format(user, path))
        sudo('chmod 0500 {}'.format(path))
