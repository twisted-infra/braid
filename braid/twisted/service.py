from fabric.api import settings, run, with_settings
from fabric.contrib.files import upload_template

from braid import package, pip, fails

from twisted.python.filepath import FilePath

base_service_directory = '/srv'

@with_settings(user='root')
def bootstrap_base():
    """
    Prepare the machine to be able to correctly install, configure and execute
    twisted services.
    """

    # Each service specific system user shall be added to the 'service' group
    run('groupadd -f --system service')

    # Each user which has to be able to administer services (for which a user
    # exists in the 'service' group) shall be added to the 'service-admin'
    # group
    run('groupadd -f --system service-admin')

    # Install required packages
    package.install('python-dev')
    package.install('pypy-dev')
    package.install('python-virtualenv')


def bootstrap(service, python='pypy'):
    serviceUser = service

    # Setup base environment for all services
    bootstrap_base()

    # Add a new user for this specific service and delegate administration to
    # users in the service-admin group
    if fails('id {}'.format(serviceUser)):
        with settings(user='root'):
            run('useradd --base-dir /srv --groups service --user-group '
                '--create-home --system --shell /bin/bash '
                '{}'.format(serviceUser))

    with settings(user=serviceUser):
        # Install twisted
        pip.install('twisted')

        # Create base directory setup
        run('mkdir -p Run')

        stopFile = FilePath(__file__).sibling('stop')
        upload_template(stopFile.path, 'stop',
                        context={'service': service},
                        mode=0755)
