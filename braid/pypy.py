import re
from os import path
from fabric.api import cd, task, sudo, abort

from braid import info
from braid.utils import fails

pypyVersion = "5.0.0"

pypyURLs = {
    'x86_64': 'https://bitbucket.org/pypy/pypy/downloads/pypy-{version}-linux64.tar.bz2',
    'x86': 'https://bitbucket.org/pypy/pypy/downloads/pypy-{version}-linux.tar.bz2',
    }
pypyDirs = {
    'x86_64': '/opt/pypy-{version}-linux64',
    'x86': '/opt/pypy-{version}-linux',
    }

@task
def install():
    arch = info.arch()
    if re.match('i?86', arch):
        arch = 'x86'
    pypyURL = pypyURLs.get(arch).format(version=pypyVersion)
    pypyDir = pypyDirs.get(arch).format(version=pypyVersion)
    if pypyURL is None or pypyDir is None:
        abort("Can't install pypy on unknown architecture.")

    sudo('/bin/mkdir -p /opt')
    if fails('/usr/bin/id {}'.format('pypy')):
        sudo('/usr/sbin/useradd --home-dir {} --gid bin '
             '-M --system --shell /bin/false '
             'pypy'.format(pypyDir))
    else:
        sudo('/usr/sbin/usermod --home {} pypy'.format(pypyDir))

    with cd('/opt'):

        sudo('/usr/bin/wget -nc {}'.format(pypyURL))
        sudo('/bin/tar xf {}'.format(path.basename(pypyURL)))
