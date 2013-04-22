from os import path
from fabric.api import cd, task, sudo

from braid import fails

pypyURL = 'https://bitbucket.org/pypy/pypy/downloads/pypy-2.0-beta2-linux64-libc2.15.tar.bz2'
setuptoolsURL = 'http://peak.telecommunity.com/dist/ez_setup.py'
pipURL = 'https://raw.github.com/pypa/pip/master/contrib/get-pip.py'

pypyDir = '/opt/pypy-2.0-beta2'


@task
def install():
    sudo('mkdir -p /opt')
    if fails('id {}'.format('pypy')):
        sudo('useradd --home-dir {} --gid bin '
             '-M --system --shell /bin/false '
             'pypy'.format(pypyDir))

    with cd('/opt'):
        for url in pypyURL, setuptoolsURL, pipURL:
            sudo('wget -nc {}'.format(url))
        sudo('tar xf {}'.format(path.basename(pypyURL)))
        for url in setuptoolsURL, pipURL:
            sudo('~pypy/bin/pypy {}'.format(path.basename(url)))
        sudo('~pypy/bin/pip install twisted')
