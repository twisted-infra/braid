import os

from fabric.api import sudo, put, env, cd, prefix, settings, run
from fabric.contrib.files import upload_template

from fablib import package, pip, fails

from twisted.python.filepath import FilePath


def bootstrap_base(python):
    """
    Prepare the machine to be able to correctly install, configure and execute
    twisted services.
    """

    # Each service specific system user shall be added to the 'service' group
    sudo('groupadd -f --system service')

    # Each user which has to be able to administer services (for which a user
    # exists in the 'service' group) shall be added to the 'service-admin'
    # group
    sudo('groupadd -f --system service-admin')

    # Give all users in the 'service-admin' group permission to execute
    # commands as any user in the 'service' group
    sudoer_conf = os.path.join(os.path.dirname(__file__),
                               'service-admin-sudoer.conf')
    put(sudoer_conf, '/etc/sudoers.d/service-admin', use_sudo=True, mode=0440)
    sudo('chown root:root /etc/sudoers.d/service-admin')

    # Install required packages
    package.install('{}-dev'.format(python))
    package.install('python-virtualenv')


def bootstrap(service, python='pypy'):
    service_user = service
    service_directory = os.path.join(env.base_service_directory, service)
    virtualenv_directory = os.path.join(service_directory, 'venv')

    # Setup base environment for all services
    bootstrap_base(python)

    # Add a new user for this specific service and delegate administration to
    # users in the service-admin group
    if fails('id {}'.format(service_user)):
        sudo('useradd --base-dir /srv --groups service --user-group '
             '--create-home --system --shell '
             '/bin/false {}'.format(service_user))

    with settings(user=service_user):
        # Create a virtualenv
        if fails('ls {}'.format(virtualenv_directory)):
            run('virtualenv --python={} --prompt=\\({}\\) {}'.format(
                python,
                service,
                virtualenv_directory
                ))

        # Install twisted
        pip.install(virtualenv_directory, 'twisted')

        # Create base directory setup
        run('mkdir -p var/log var/run etc/init.d')

        stopFile = FilePath(__file__).sibling('stop')
        upload_template(stopFile.path, 'stop',
                        context={'service': service},
                        mode=0755)


def _service_action(service, action):
    service_user = service
    service_directory = os.path.join(env.base_service_directory, service)
    virtualenv_directory = os.path.join(service_directory, 'venv')
    venv = os.path.join(virtualenv_directory, 'bin', 'activate')
    initscript = os.path.join(service_directory, 'etc', 'init.d', service)

    with prefix('source {}'.format(venv)):
        return sudo('{} {}'.format(initscript, action), user=service_user)


def start(service):
    _service_action(service, 'start')


def stop(service):
    _service_action(service, 'stop')


def restart(service):
    _service_action(service, 'restart')
