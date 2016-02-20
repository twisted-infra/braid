from __future__ import absolute_import

from braid.api import sudo, task, put

from twisted.python.filepath import FilePath

from braid import pypy, service, authbind, git, package, bazaar, postgres


__all__ = ['bootstrap', 'sshConfig']


@task
def bootstrap():
    """
    Prepare the machine to be able to correctly install, configure and execute
    twisted services.
    """
    sudo('apt-get update')

    package.install(['sudo'])

    # Each service specific system user shall be added to the 'service' group
    sudo('/usr/sbin/groupadd -f --system service')

    # pypy is installed with a tarball downloaded with wget.
    package.install(['wget'])
    # libssl-dev is needed for installing pyOpenSSL for PyPy.
    package.install(['libssl-dev'])

    package.install(['python2.7', 'python2.7-dev'])
    # gcc and svn is needed for 'pip install'
    package.install(['gcc', 'subversion'])
    # For trac
    package.install(['enscript', 'python-subversion'])
    # For equivs
    package.install(['equivs'])
    # For buildbot/codespeed
    package.install(['sqlite3'])
    pypy.install()
    authbind.install()
    git.install()
    bazaar.install()
    postgres.install()

    sshConfig()


@task
def sshConfig():
    """
    Install ssh config that allows anyone who can login as root
    to login as any service.
    """
    configFile = FilePath(__file__).sibling('sshd_config')
    put(configFile.path, '/etc/ssh/sshd_config', use_sudo=True)

    sudo('/bin/chgrp service /root/.ssh/authorized_keys')
    sudo('/bin/chmod go+X /root /root/.ssh')
    sudo('/bin/chmod g+r /root/.ssh/authorized_keys')
    service.restart('ssh')
