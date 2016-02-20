from cStringIO import StringIO

from fabric.api import settings, run, put

from braid import pip, tasks, users, venv

from twisted.python.filepath import FilePath


TASK_PREFIX = 'task_'


def _stripPrefix(f):
    """
    Get the unprefixed name of C{f}.
    """
    return f.__name__[len(TASK_PREFIX):]


class Service(tasks.Service):

    python = "pypy"
    runDir = '~/run'
    logDir = '~/log'
    configDir = '~/config'
    binDir = '~/bin'

    def __init__(self, serviceName):
        self.serviceName = serviceName
        self.serviceUser = serviceName

        self.venv = venv.VirtualEnvironment(user=self.serviceUser,
                                            python=self.python)


    def _generateReadme(self):
        """
        Generate a generic readme from the tasks available.
        """
        # FIXME: Clean this up
        # https://github.com/twisted-infra/braid/issues/7
        readmeFile = FilePath(__file__).sibling('README')
        readmeContext = {}
        for key in ['configDir', 'runDir', 'logDir', 'binDir', 'serviceName']:
            readmeContext[key] = getattr(self, key)
        tasks = self.getTasks().itervalues()
        tasks = [(t.name, t.__doc__.strip().splitlines()[0]) for t in tasks]
        tasks = [' - {}: {}'.format(*t) for t in tasks]
        readmeContext['tasks'] = '\n'.join(tasks)
        return readmeFile.getContent().format(**readmeContext)

    def bootstrap(self, venv_site_packages=False):
        # Create the user only if it does not already exist
        users.createService(self.serviceUser)

        with settings(user=self.serviceUser):

            # Create a virtualenv in the service user's folder
            # It'll be a PyPy venv by default, unless self.python is changed
            self.venv.create(site_packages=venv_site_packages)

            # Create base directory setup
            run('/bin/mkdir -p {} {} {} {}'.format(
                self.runDir,
                self.logDir,
                self.binDir,
                self.configDir,
                ))

            # Create stop script
            stopFile = FilePath(__file__).sibling('stop')
            put(stopFile.path, '{}/stop'.format(self.binDir), mode=0755)

            readme = self._generateReadme()
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
        with settings(warn_only=True):
            self.task_stop()
        self.task_start()

    def task_log(self, n=20):
        """
        Tail the log of the service.
        """
        with settings(user=self.serviceUser):
            run('/usr/bin/tail -f -n {} {}/twistd.log'.format(n, self.logDir))
