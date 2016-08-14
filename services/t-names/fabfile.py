"""
Support for DNS service installation and management.
"""
import os

from fabric.api import execute, put, run, settings

from braid import authbind, cron
from braid.twisted import service

from braid import config
_hush_pyflakes = [ config ]


class TwistedNames(service.Service):

    def task_install(self):
        """
        Install t-names, a Twisted Names based DNS server.
        """
        # Bootstrap a new service environment
        self.bootstrap()

        # Setup authbind
        authbind.allow(self.serviceUser, 53)

        with settings(user=self.serviceUser):
            run('/bin/ln -nsf {}/start {}/start'.format(self.configDir, self.binDir))
            execute(self.update)
            cron.install(self.serviceUser, '{}/crontab'.format(self.configDir))


    def update(self):
        """
        Update config.
        """
        with settings(user=self.serviceUser):
            self.venv.install_twisted()
            run('mkdir -p ' + self.configDir)
            put(
                os.path.dirname(__file__) + '/*', self.configDir,
                mirror_local_mode=True)

    def task_update(self):
        """
        Update config and restart.
        """
        self.update()
        self.task_restart()



globals().update(TwistedNames('t-names').getTasks(role='nameserver'))
