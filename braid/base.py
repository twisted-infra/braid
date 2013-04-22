from __future__ import absolute_import

from fabric.api import sudo, task, put

from twisted.python.filepath import FilePath

from braid import pypy, service, authbind, git, package, bazaar


@task
def bootstrap():
    """
    Prepare the machine to be able to correctly install, configure and execute
    twisted services.
    """

    # Each service specific system user shall be added to the 'service' group
    sudo('groupadd -f --system service')

    # gcc is needed for 'pip install'
    package.install('gcc')
    package.install('python-pip')
    pypy.install()
    authbind.install()
    git.install()
    bazaar.install()

    sshConfig()


def sshConfig():
    """
    Install ssh config that allows anyone who can login as root
    to login as any service.
    """
    configFile = FilePath(__file__).sibling('sshd_config')
    put(configFile.path, '/etc/ssh/sshd_config', use_sudo=True)

    sudo('chgrp service /root/.ssh/authorized_keys')
    sudo('chmod go+X /root /root/.ssh')
    sudo('chmod g+r /root/.ssh/authorized_keys')
    service.restart('ssh')
