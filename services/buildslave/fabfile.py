import os

from fabric.api import settings, execute, put

from braid.twisted import service
from braid.tasks import addTasks
from braid import config

__all__ = ['config']

class Buildslave(service.Service):

    python = 'python'

    serviceLocalDir = os.path.dirname(__file__)

    def task_install(self):
        """
        Install the buildslave process for testing.

        General system configuration should be done via Ansible.
        """
        self.bootstrap()

        with settings(user=self.serviceUser):
            self.venv.install('buildbot-slave')
            put(
                os.path.join(self.serviceLocalDir, 'start'),
                self.binDir,
                mirror_local_mode=True)
            execute(self.update)

    def update(self, _installDeps=False):
        """
        Update configuration.
        """
        with settings(user=self.serviceUser):
            put(
                os.path.join(self.serviceLocalDir, 'buildbot.tac'),
                self.configDir)
            put(os.path.join(self.serviceLocalDir, 'info'), self.configDir)

    def task_update(self):
        """
        Update config and restart.
        """
        self.update()
        self.task_restart()


addTasks(globals(), Buildslave('bb-slave').getTasks())
