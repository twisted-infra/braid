from fabric.api import settings, sudo, run, put, task as fabricTask

from braid import pip, fails

from twisted.python.filepath import FilePath


def task(func):
    func.isTask = True
    return func


class Service(object):

    baseServicesDirectory = '/srv'
    runDir = '~/run'
    logDir = '~/log'
    srcDir = '~/src'
    binDir = '~/bin'

    def __init__(self, serviceName):
        self.serviceName = serviceName
        self.serviceUser = serviceName

    def bootstrap(self, python='pypy'):
        # Create the user only if it does not already exist
        if fails('id {}'.format(self.serviceUser)):
            sudo('useradd --base-dir {} --groups service --user-group '
                 '--create-home --system --shell /bin/bash '
                 '{}'.format(self.baseServicesDirectory, self.serviceUser))

        with settings(user=self.serviceUser):
            # Install twisted
            pip.install('twisted')

            # Create base directory setup
            run('mkdir -p {} {} {} {}'.format(
                self.runDir,
                self.logDir,
                self.binDir,
                self.srcDir,
            ))

            # Create stop script
            stopFile = FilePath(__file__).sibling('stop')
            put(stopFile.path, '{}/stop'.format(self.binDir), mode=0755)

    @task
    def start(self):
        with settings(user=self.serviceUser):
            run('./{}/start'.format(self.binDir), pty=False)

    @task
    def stop(self):
        with settings(user=self.serviceUser):
            run('./{}/start'.format(self.binDir))

    @task
    def restart(self):
        self.stop()
        self.start()

    @task
    def log(self):
        with settings(user=self.serviceUser):
            run('tail -f {}/twistd.log'.format(self.logDir))

    def getTasks(self):
        tasks = (getattr(self, attr) for attr in dir(self))
        tasks = (task for task in tasks if getattr(task, 'isTask', False))
        tasks = (fabricTask(task) for task in tasks)
        return {task.__name__: task for task in tasks}
