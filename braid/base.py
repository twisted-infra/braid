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

    package.install(['sudo'])

    # Each service specific system user shall be added to the 'service' group
    sudo('/usr/sbin/groupadd -f --system service')

    package.install(['python2.7', 'python2.7-dev'])
    # gcc is needed for 'pip install'
    package.install(['gcc', 'python-pip'])
    # For trac
    package.install(['python-subversion', 'enscript'])
    # For equivs
    package.install(['equivs'])
    # For buildbot/codespeed
    package.install(['sqlite3'])
    # Development and deployment
    package.install(['python-virtualenv'])
    package.install(['python-twisted', 'python-openssl'])
    pypy.install()
    authbind.install()
    git.install()
    bazaar.install()
    postgres.install()

    sshConfig()


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
