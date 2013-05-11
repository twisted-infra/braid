from os import path
from fabric.api import cd, task, sudo

from braid import fails

pypyURL = 'https://bitbucket.org/pypy/pypy/downloads/pypy-2.0-linux64.tar.bz2'
setuptoolsURL = 'http://peak.telecommunity.com/dist/ez_setup.py'
pipURL = 'https://raw.github.com/pypa/pip/master/contrib/get-pip.py'

pypyDir = '/opt/pypy-2.0'

@task
def install():
    sudo('/bin/mkdir -p /opt')
    if fails('/usr/bin/id {}'.format('pypy')):
        sudo('/usr/sbin/useradd --home-dir {} --gid bin '
             '-M --system --shell /bin/false '
             'pypy'.format(pypyDir))
    else:
        sudo('/usr/sbin/usermod --home-dir {} pypy'.format(pypyDir))

    with cd('/opt'):
        for url in pypyURL, setuptoolsURL, pipURL:
            sudo('/usr/bin/wget -nc {}'.format(url))
        sudo('/bin/tar xf {}'.format(path.basename(pypyURL)))
        for url in setuptoolsURL, pipURL:
            sudo('~pypy/bin/pypy {}'.format(path.basename(url)))
        sudo('~pypy/bin/pip install twisted')
