import os

from fabric.api import put, task, sudo, cd, settings, run

from braid import authbind, requires_root, bazaar
from braid.twisted import service

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
    with settings(user=serviceName):
        startFile = FilePath(__file__).sibling('start')
        put(startFile.path, '/srv/t-names/start', mode=0755)

    update()

@task
def update():
    with settings(user=serviceName):
        # TODO: This is a temp location for testing
        bazaar.branch('http://cube.twistedmatrix.com/~tomprince/Zones', '/srv/t-names/Zones')
        # TODO restart


@task
def start():
    with settings(user=serviceName):
        run('./start', pty=False)


@task
def stop():
    with settings(user=serviceName):
        run('./stop')


@task
def restart():
    stop()
    start()

@task
def log():
    with settings(user=serviceName):
        run('tail -f twistd.log')
