"""
Support for benchmark reporting.
"""
from StringIO import StringIO
import os
import random

from fabric.api import execute, run, settings, env, put, cd

from braid import git, cron, archive, utils
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
        self.bootstrap()

        self.update()

        with settings(user=self.serviceUser):
            run('/bin/ln -nsf {}/start {}/start'.format(self.configDir, self.binDir))
            run('mkdir -p ~/data')
            execute(self.update)
            cron.install(self.serviceUser, '{}/crontab'.format(self.configDir))
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
                    mode=0o600)

    def update(self):
        """
        Update config.
        """
        with settings(user=self.serviceUser):
            run('mkdir -p ' + self.configDir)
            put(
                os.path.dirname(__file__) + '/*', self.configDir,
                mirror_local_mode=True)

            self.task_recreateVirtualEnvironment()

            if env.get('installTestData'):
                execute(self.task_installTestData)


    def task_recreateVirtualEnvironment(self):
        """
        Recreate the virtual environment.
        """
        self.venv.remove()
        self.venv.create()
        git.branch('https://github.com/tobami/codespeed.git', '~/codespeed')
        with cd("~/codespeed"):
            run("git checkout 9893b87de02bdc1ea6256207de5cc010b095b3a5")
            run("git reset --hard")
        self.venv.install_twisted()
        self.venv.install('-r ~/codespeed/requirements.txt')


    def djangoAdmin(self, args):
        """
        Run django-admin with proper settings.
        """
        with settings(user=self.serviceUser):
            path = '~/config:~/codespeed/'
            run('PYTHONPATH={} '
                'DJANGO_SETTINGS_MODULE=twistedcodespeed.local_settings '
                '~/virtualenv/bin/django-admin.py {}'.format(path, ' '.join(args)))

    def task_installTestData(self):
        """
        Create test db.
        """
        self.djangoAdmin(['syncdb', '--noinput'])
        self.djangoAdmin(['migrate'])

    def task_createSuperuser(self):
        """
        Reset the admin password.
        """
        self.djangoAdmin(['createsuperuser'])

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
