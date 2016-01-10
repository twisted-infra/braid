import os

from fabric.api import sudo, run, abort, quiet

from braid import package, hasSudoCapabilities


def allow(user, port):
    path = os.path.join('/etc/authbind/byport', str(port))
    needsUpdate = True
    with quiet():
        state = run('/usr/bin/stat -c %U:%a {}'.format(path))
        needsUpdate = state.strip().split(':') != [user, '500']
    if needsUpdate:
        if not hasSudoCapabilities():
            abort('Trying to give {} access to port {} but have insufficient '
                  'capabilities.'.format(user, port))
        sudo('/bin/touch {}'.format(path))
        sudo('/bin/chown {0}:{0} {1}'.format(user, path))
        sudo('/bin/chmod 0500 {}'.format(path))
