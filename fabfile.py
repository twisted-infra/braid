"""
Collection of utilities to automate the administration of Twisted's
infrastructure. Use this utility to install, update and start/stop/restart
services running on twistedmatrix.com.
"""

"""
This file is a simple entry point, nothing is final about it!
Just experimenting for now.
"""

from fabric.api import task, sudo

from braid import package, service, load_config, requires_root

from services import dns, trac


__all__ = ['trac', 'make_service_admin']


load_config('config')


# TODO: Add hooks to check if updated to upstream before running any command


@task
@requires_root
def install_exim():
    package.install('exim4')
    service.enable('exim4')


@task
@requires_root
def make_service_admin(username):
    """
    Simply add the given user to the 'service-admin' group. This allows the
    user to execute any command as any service-specific user through sudo.
    """
    sudo('usermod -a -G service-admin {}'.format(username))
