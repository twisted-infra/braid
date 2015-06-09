import re
from os import path
from fabric.api import cd, task, sudo, abort

from braid import info
from braid.utils import fails

pypyURLs = {
    'x86_64': 'https://bitbucket.org/pypy/pypy/downloads/pypy-2.6.0-linux64.tar.bz2',
    'x86': 'https://bitbucket.org/pypy/pypy/downloads/pypy-2.6.0-linux.tar.bz2',
    }
pypyDirs = {
    'x86_64': '/opt/pypy-2.6.0-linux64',
    'x86': '/opt/pypy-2.6.0-linux',
    }

pipURL = 'https://raw.github.com/pypa/pip/master/contrib/get-pip.py'


@task
def install():
    arch = info.arch()
    if re.match('i?86', arch):
        arch = 'x86'
    pypyURL = pypyURLs.get(arch)
    pypyDir = pypyDirs.get(arch)
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

        for url in pypyURL, pipURL:
            sudo('/usr/bin/wget -nc {}'.format(url))
        sudo('/bin/tar xf {}'.format(path.basename(pypyURL)))
        sudo('~pypy/bin/pypy {}'.format(path.join('/opt/', path.basename(pipURL))), pty=False)
        sudo('~pypy/bin/pip install pyopenssl service_identity')
        sudo('~pypy/bin/pip install Twisted==15.2.1')
