import os

from fabric.api import sudo, run, abort, quiet

from braid import package, hasSudoCapabilities


def install():
    package.install(['authbind'])


def allow(user, port):
    path = os.path.join('/etc/authbind/byport', str(port))
    needsUpdate = True
    with quiet():
        state = run('stat -c %U:%a {}'.format(path))
        needsUpdate = state.strip().split(':') != [user, '500']
    if needsUpdate:
        if not hasSudoCapabilities():
            abort('Trying to give {} access to port {} but have insufficient '
                  'capabilities.'.format(user, port))
        sudo('touch {}'.format(path))
        sudo('chown {0}:{0} {1}'.format(user, path))
        sudo('chmod 0500 {}'.format(path))
