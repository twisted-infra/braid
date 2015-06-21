"""
Support for amptrac.
"""

from fabric.api import run, settings

from braid import cron, git, pip, postgres
from braid.twisted import service
from braid.tasks import addTasks

from braid import config
__all__ = [ 'config' ]


class AmpTrac(service.Service):
    def task_install(self):
        """
        Install amptrac.
        """
        # Bootstrap a new service environment
        self.bootstrap()

        postgres.createUser('amptrac')
        postgres.grantRead('trac', 'amptrac')

        with settings(user=self.serviceUser):
            run('/bin/ln -nsf {}/start {}/start'.format(self.configDir, self.binDir))
            self.update(_installDeps=True)
            cron.install(self.serviceUser, '{}/crontab'.format(self.configDir))

    def update(self, _installDeps=False):
        """
        Update config.
        """
        with settings(user=self.serviceUser):
            git.branch('https://github.com/twisted-infra/amptrac-config', self.configDir)
            amptracSource = 'git+https://github.com/twisted-infra/amptrac-server'
            if _installDeps:
                pip.install('{}'.format(amptracSource))
            else:
                pip.install('--no-deps --upgrade {}'.format(amptracSource))


    def task_update(self):
        """
        Update config and restart.
        """
        self.update()
        self.task_restart()


addTasks(globals(), AmpTrac('amptrac').getTasks())
