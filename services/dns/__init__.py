import os

from fabric.api import put, task, sudo

from fablib import authbind, requires_root
from fablib.twisted import service


args = ['dns',
        '--pyzone', '$Z/twistedmatrix.com',
        '--pyzone', '$Z/divunal.com',
        '--pyzone', '$Z/intarweb.us',
        '--pyzone', '$Z/ynchrono.us',
        '--pyzone', '$Z/divmod.com',
        ]

@task
@requires_root
def install():
    # TODO:
    # - Setup zone files (incl. PYTHONPATH in script if needed)
    # - Rename dns to t-names or whatever (locations, scripts,...)

    # Bootstrap a new service environment
    service.bootstrap('dns', )

    # Setup authbind
    authbind.install()
    authbind.allow('dns', 53)

    # Install initscript
    # TODO

@task
def update():
    # TODO
    pass


@task
def start():
    service.start('dns')


@task
def stop():
    service.stop('dns')


@task
def restart():
    service.restart('dns')
