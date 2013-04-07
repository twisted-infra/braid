import os

from fabric.api import put, task

from fablib import authbind, requires_root
from fablib.twisted import service


@task
@requires_root
def install():
    # TODO:
    # - Setup zone files (incl. PYTHONPATH in script if needed)
    # - Rename dns to t-names or whatever (locations, scripts,...)

    # Bootstrap a new service environment
    service.bootstrap('dns')

    # Setup authbind
    authbind.install()
    authbind.allow('dns', 53)

    initscript = os.path.join(os.path.dirname(__file__), 'initscript.sh')
    put(initscript, '/srv/dns/etc/init.d/dns', use_sudo=True, mode=0755)


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
