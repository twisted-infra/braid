from fabric.api import settings, sudo, run, put

from braid import pip, fails

from twisted.python.filepath import FilePath

base_service_directory = '/srv'

def bootstrap(service, python='pypy'):
    serviceUser = service

    # Add a new user for this specific service and delegate administration to
    # users in the service-admin group
    if fails('id {}'.format(serviceUser)):
        with settings(user='root'):
            sudo('useradd --base-dir /srv --groups service --user-group '
                '--create-home --system --shell /bin/bash '
                '{}'.format(serviceUser))

    with settings(user=serviceUser):
        # Install twisted
        pip.install('twisted')

        # Create base directory setup
        run('mkdir -p Run')

        stopFile = FilePath(__file__).sibling('stop')
        put(stopFile.path, 'stop', mode=0755)
