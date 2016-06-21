"""
Support for amptrac.
"""
import os
from fabric.api import put, run, settings

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
            self.update()
            cron.install(self.serviceUser, '{}/crontab'.format(self.configDir))

    def update(self):
        """
        Update config.
        """
        with settings(user=self.serviceUser):
            run('mkdir -p ' + self.configDir)
            put(
                os.path.dirname(__file__) + '/*', self.configDir,
                mirror_local_mode=True)

            self.venv.install_twisted()
            self.venv.install('git+https://github.com/twisted-infra/amptrac.git')
            self.venv.install('git+https://github.com/twisted-infra/amptrac-server')

    def task_update(self):
        """
        Update config and restart.
        """
        self.update()
        self.task_restart()


addTasks(globals(), AmpTrac('amptrac').getTasks())
