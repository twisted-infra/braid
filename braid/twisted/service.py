from cStringIO import StringIO

from fabric.api import settings, sudo, run, put, task, abort

from braid import pip, fails
from braid.utils import hasSudoCapabilities

from twisted.python.filepath import FilePath
from twisted.python.reflect import prefixedMethods


TASK_PREFIX = 'task_'


def _stripPrefix(f):
    """
    Get the unprefixed name of C{f}.
    """
    return f.__name__[len(TASK_PREFIX):]


class Service(object):

    baseServicesDirectory = '/srv'
    runDir = '~/run'
    logDir = '~/log'
    configDir = '~/config'
    binDir = '~/bin'

    def __init__(self, serviceName):
        self.serviceName = serviceName
        self.serviceUser = serviceName

    def bootstrap(self, python='pypy'):
        # Create the user only if it does not already exist
        if fails('id {}'.format(self.serviceUser)):
            if not hasSudoCapabilities():
                abort("User {} doesn't exist and we can't create it."
                      .format(self.serviceUser))
            sudo('useradd --base-dir {} --groups service --user-group '
                 '--create-home --system --shell /bin/bash '
                 '{}'.format(self.baseServicesDirectory, self.serviceUser))

        with settings(user=self.serviceUser):
            # Install twisted
            pip.install('twisted')

            # Create base directory setup
            run('mkdir -p {} {} {}'.format(
                self.runDir,
                self.logDir,
                self.binDir))

            # Create stop script
            stopFile = FilePath(__file__).sibling('stop')
            put(stopFile.path, '{}/stop'.format(self.binDir), mode=0755)

            readmeFile = FilePath(__file__).sibling('README')
            # FIXME: Clean this up
            # https://github.com/twisted-infra/braid/issues/7
            readmeContext = {}
            for key in ['configDir', 'runDir', 'logDir', 'binDir', 'serviceName']:
                readmeContext[key] = getattr(self, key)
            tasks = self.getTasks().itervalues()
            tasks = ((t.name, t.__doc__.strip().splitlines()[0]) for t in tasks)
            tasks = (' - {}: {}'.format(t) for t in tasks)
            readmeContext['tasks'] = '\n'.join(tasks)
            readme = readmeFile.getContent().format(**readmeContext)
            put(StringIO(readme), 'README')

    def task_start(self):
        """
        Stop the service
        """
        with settings(user=self.serviceUser):
            run('{}/start'.format(self.binDir), pty=False)

    def task_stop(self):
        """
        Stop the service.
        """
        with settings(user=self.serviceUser):
            run('{}/stop'.format(self.binDir))

    def task_restart(self):
        """
        Restart the service.
        """
        self.stop()
        self.start()

    def task_log(self):
        """
        Tail the log of the service.
        """
        with settings(user=self.serviceUser):
            run('tail -f {}/twistd.log'.format(self.logDir))

    def getTasks(self):
        """
        Get all tasks of this L{Service} object.

        Intended to be used like::

            globals.updated(Service('name').getTasks())

        at the module level of a fabfile.

        @returns: L{dict} of L{fabric.tasks.Task}
        """
        tasks = [(t, _stripPrefix(t))
                 for t in prefixedMethods(self, TASK_PREFIX)]
        return {name: task(name=name)(t) for t, name in tasks}
