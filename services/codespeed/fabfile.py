"""
Support for benchmark reporting.
"""
from StringIO import StringIO
import random

from fabric.api import run, settings, env, put

from braid import git, cron, pip, archive, utils, package
from braid.twisted import service
from braid.tasks import addTasks

from braid import config


__all__ = [ 'config' ]


class Codespeed(service.Service):

    def task_install(self):
        """
        Install codespeed, a benchmark reporting tool
        """
        # Bootstrap a new service environment
        self.bootstrap(python='system')

        package.install(['python-svn'])

        with settings(user=self.serviceUser):
            run('/bin/ln -nsf {}/start {}/start'.format(self.configDir, self.binDir))
            run('mkdir -p ~/data')
            pip.install('Django==1.2.7', python='system')
            self.update()
            cron.install(self.serviceUser, '{}/crontab'.format(self.configDir))
            if env.get('installTestData'):
                self.task_installTestData()
            self.task_generateSecretKey()

    def task_generateSecretKey(self):
        """
        Generate a new C{SECRET_KEY} and save it in the settings file.
        """
        with settings(user=self.serviceUser):
            if utils.succeeds('ls {}/secret_key.py'.format(self.configDir)):
                execute = utils.confirm('This will replace the current secret '
                                        'key with a newly generated one.')
            else:
                execute = True

            if execute:
                chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
                secret = ''.join([random.choice(chars) for i in range(50)])
                setting = StringIO("SECRET_KEY = '{}'\n".format(secret))
                put(setting, '{}/secret_key.py'.format(self.configDir),
                    mode=0600)

    def update(self):
        """
        Update config.
        """
        with settings(user=self.serviceUser):
            git.branch('https://github.com/twisted-infra/codespeed', self.configDir)
            git.branch('https://github.com/twisted-infra/codespeed-source', '~/codespeed')

    def djangoAdmin(self, args):
        """
        Run django-admin with proper settings.
        """
        with settings(user=self.serviceUser):
            path = '~/config:~/codespeed:~/codespeed/speedcenter'
            run('PYTHONPATH={}:$PYTHONPATH ~/.local/bin/django-admin.py {} '
                '--settings=local_settings'.format(path, ' '.join(args)))

    def task_installTestData(self):
        """
        Create test db.
        """
        self.djangoAdmin(['syncdb', '--noinput'])

    def task_update(self):
        """
        Update config and restart.
        """
        self.update()
        self.task_restart()

    def task_dump(self, localfile):
        """
        Dump codespeed database and download it to the given C{localfile}.
        """
        with settings(user=self.serviceUser):
            with utils.tempfile() as temp:
                run('/usr/bin/sqlite3 ~/data/codespeed.db .dump >{}'.format(temp))
                archive.dump({
                    'db.dump': temp,
                }, localfile)

    def task_restore(self, localfile):
        """
        Restore codespeed database from the given C{localfile}.
        """
        msg = 'The whole database will be replaced with the backup.'

        if utils.confirm(msg):
            with settings(user=self.serviceUser):
                with utils.tempfile() as temp:
                    archive.restore({
                        'db.dump': temp,
                    }, localfile)
                    run('/bin/rm -f ~/data/codespeed.db')
                    run('/usr/bin/sqlite3 ~/data/codespeed.db ".read {}"'.format(temp))

addTasks(globals(), Codespeed('codespeed').getTasks())
