from fabric.api import settings, sudo, run, put, task

from braid import pip, fails

from twisted.python.filepath import FilePath
from twisted.python.reflect import prefixedMethods


TASK_PREFIX = 'task_'

def _stripPrefix(f):
    return f.__name__[len(TASK_PREFIX):]

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
                self.srcDir))

            # Create stop script
            stopFile = FilePath(__file__).sibling('stop')
            put(stopFile.path, '{}/stop'.format(self.binDir), mode=0755)

    def task_start(self):
        with settings(user=self.serviceUser):
            run('{}/start'.format(self.binDir), pty=False)

    def task_stop(self):
        with settings(user=self.serviceUser):
            run('{}/start'.format(self.binDir))

    def task_restart(self):
        self.stop()
        self.start()

    def task_log(self):
        with settings(user=self.serviceUser):
            run('tail -f {}/twistd.log'.format(self.logDir))

    def getTasks(self):
        tasks = [(t, _stripPrefix(t))
                 for t in prefixedMethods(self, TASK_PREFIX)]
        return { name: task(name=name)(t) for t, name in tasks }
