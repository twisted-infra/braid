import os

from fabric.api import put, task, sudo, cd, settings

from fablib import authbind, requires_root, bazaar
from fablib.twisted import service

from twisted.python.filepath import FilePath

serviceName = 't-names'

@task
@requires_root
def install():
    # TODO:
    # - Setup zone files (incl. PYTHONPATH in script if needed)
    # - Rename dns to t-names or whatever (locations, scripts,...)

    # Bootstrap a new service environment
    service.bootstrap(serviceName, )

    # Setup authbind
    authbind.install()
    authbind.allow(serviceName, 53)

    bazaar.install()

    # Install initscript
    startFile = FilePath(__file__).sibling('start')
    put(startFile.path, '/srv/t-names/start', mode=0755)
    sudo('chown %s: /srv/t-names/start' % (serviceName,))

    update()

@task
def update():
    with cd('/srv/t-names'), settings(sudo_user=serviceName):
        # TODO: This is a temp location for testing
        bazaar.branch('http://cube.twistedmatrix.com/~tomprince/Zones', '/srv/t-names/Zones')
        # TODO restart


@task
def start():
    service.start('dns')


@task
def stop():
    service.stop('dns')


@task
def restart():
    service.restart('dns')
