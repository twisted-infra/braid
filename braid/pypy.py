import re
from os import path
from fabric.api import cd, task, sudo, abort

from braid import info
from braid.utils import fails

pypyURLs = {
    'x86_64': 'https://bitbucket.org/pypy/pypy/downloads/pypy-2.0.2-linux64.tar.bz2',
    'x86': 'https://bitbucket.org/pypy/pypy/downloads/pypy-2.0.2-linux.tar.bz2',
    }
pypyDir = '/opt/pypy-2.0.2'

setuptoolsURL = 'http://peak.telecommunity.com/dist/ez_setup.py'
pipURL = 'https://raw.github.com/pypa/pip/master/contrib/get-pip.py'


@task
def install():
    sudo('/bin/mkdir -p /opt')
    if fails('/usr/bin/id {}'.format('pypy')):
        sudo('/usr/sbin/useradd --home-dir {} --gid bin '
             '-M --system --shell /bin/false '
             'pypy'.format(pypyDir))
    else:
        sudo('/usr/sbin/usermod --home {} pypy'.format(pypyDir))

    with cd('/opt'):
        if info.arch() == 'x86_64':
            pypyURL = pypyURLs['x86_64']
        elif re.match('i.86', info.arch()):
            pypyURL = pypyURLs['x86']
        else:
            abort("Can't install pypy on unknown architecture.")

        for url in pypyURL, setuptoolsURL, pipURL:
            sudo('/usr/bin/wget -nc {}'.format(url))
        sudo('/bin/tar xf {}'.format(path.basename(pypyURL)))
        for url in setuptoolsURL, pipURL:
            sudo('~pypy/bin/pypy {}'.format(path.basename(url)))
        sudo('~pypy/bin/pip install pyopenssl')
        sudo('~pypy/bin/pip install svn+svn://svn.twistedmatrix.com/svn/Twisted/trunk/')
