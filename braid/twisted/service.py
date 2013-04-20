from fabric.api import settings, sudo, run, put, task, with_settings

from braid import pip, fails

from twisted.python.filepath import FilePath

base_service_directory = '/srv'

def bootstrap(service, python='pypy'):
    serviceUser = service

    # Add a new user for this specific service and delegate administration to
    # users in the service-admin group
    if fails('id {}'.format(serviceUser)):
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

def serviceTasks(service):
    @task
    @with_settings(user=service)
    def start():
        run('./start', pty=False)


    @task
    @with_settings(user=service)
    def stop():
        run('./stop')


    @task
    def restart():
        stop()
        start()

    @task
    @with_settings(user=service)
    def log():
        run('tail -f Run/twistd.log')

    return {fn.__name__: fn for fn in [start, stop, restart, log]}
