"""
Support for kenaan service installation and management.
"""
import os
from fabric.api import execute, run, settings, env, cd, abort, puts, put
from fabric.contrib import files

from twisted.python.filepath import FilePath
from twisted.python.util import sibpath

from braid import git, cron, pip
from braid.twisted import service

# TODO: Move these somewhere else and make them easily extendable
from braid import config
_hush_pyflakes = [ config ]


class Kenaan(service.Service):
    def task_install(self):
        """
        Install kenaan, an irc bot.
        """
        # Bootstrap a new service environment
        self.bootstrap()

        with settings(user=self.serviceUser):
            run('/bin/ln -nsf {}/start {}/start'.format(self.configDir, self.binDir))
            for bin in ['alert', 'commit', 'message', 'ticket']:
                run('/bin/ln -nsf {1}/{0} {2}/{0}'.format(bin, self.configDir, self.binDir))
            execute(self.update)
            cron.install(self.serviceUser, '{}/crontab'.format(self.configDir))


    def task_installTestData(self, force=None):
        """
        Do test environment setup (with fake passwords, etc).
        """
        if env.get('environment') == 'production':
           abort("Don't use testInit in production.")

        with settings(user=self.serviceUser), cd(self.configDir):
            if force or not files.exists('private.py'):
                puts('Using sample private.py and config.py')
                put(sibpath(__file__, 'private.py.sample'),
                    os.path.join(self.configDir, "private.py"), mode=0600)
                put(sibpath(__file__, 'config.py.sample'),
                    os.path.join(self.configDir, "config.py"))


    def task_installPrivateData(self, private=sibpath(__file__, 'private.py')):
        """
        Install private config.
        """
        with settings(user=self.serviceUser):
            put(sibpath(__file__, 'config.py'),
                os.path.join(self.configDir, "config.py"))

            if FilePath(private).exists():
                put(sibpath(__file__, 'private.py'),
                    os.path.join(self.configDir, "private.py"), mode=0600)
            else:
                abort('Missing private config.')


    def update(self):
        """
        Update config.
        """
        with settings(user=self.serviceUser):
            filesToCopy = [
                "_http.py", "alert", "alert.py", "commit", "commit.py",
                "commit_bot.py", "commit_bot.tac", "crontab", "message",
                "message.py", "start", "ticket", "ticket.py"
            ]
            run('mkdir -p ' + self.configDir)

            self.venv.install("amptrac")

            for f in filesToCopy:
                put(os.path.join(os.path.dirname(__file__), f), self.configDir,
                    mirror_local_mode=True)

            if env.get('installPrivateData'):
                execute(self.task_installPrivateData)
            else:
                execute(self.task_installTestData)


    def task_update(self):
        """
        Update config and restart.
        """
        self.update()
        self.task_restart()


globals().update(Kenaan('kenaan').getTasks())
