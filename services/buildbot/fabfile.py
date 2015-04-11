import os

from fabric.api import settings, run, env, cd, puts, abort
from fabric.contrib import files

from braid import git, cron, pip, archive
from braid.twisted import service
from braid.tasks import addTasks
from braid.utils import confirm
from braid import config

__all__ = ['config']

class Buildbot(service.Service):
    def task_install(self):
        """
        Install buildbot.
        """
        self.bootstrap()

        with settings(user=self.serviceUser):
            pip.install('sqlalchemy==0.7.10')
            self.update(_installDeps=True)
            run('/bin/ln -nsf {}/start {}/start'.format(self.configDir, self.binDir))
            run('/bin/mkdir -p ~/data')
            run('/bin/mkdir -p ~/data/build_products')
            run('/bin/ln -nsf ~/data/build_products {}/master/public_html/builds'.format(self.configDir))

            # TODO: install dependencies
            if env.get('installTestData'):
                self.task_installTestData()

            cron.install(self.serviceUser, '{}/crontab'.format(self.configDir))

    def task_installTestData(self, force=None):
        """
        Do test environment setup (with fake passwords, etc).
        """
        if env.get('environment') == 'production':
           abort("Don't use testInit in production.")

        with settings(user=self.serviceUser), cd(os.path.join(self.configDir, 'master')):
            if force or not files.exists('private.py'):
                puts('Using sample private.py')
                run('/bin/cp private.py.sample private.py')

            if force or not files.exists('state.sqlite'):
                run('~/.local/bin/buildbot upgrade-master')

    def task_updatePrivateData(self):
        """
        Update private config.
        """
        with settings(user=self.serviceUser):
            git.branch('tomprince@svn.twistedmatrix.com:infra/buildbot-private.git', '~/private')

    def update(self, _installDeps=False):
        """
        Update
        """
        with settings(user=self.serviceUser):
            git.branch('https://github.com/twisted-infra/twisted-buildbot-configuration', self.configDir)
            buildbotSource = os.path.join(self.configDir, 'buildbot-source')
            git.branch('https://github.com/twisted-infra/buildbot', buildbotSource)
            if _installDeps:
                pip.install('{}'.format(os.path.join(buildbotSource, 'master')),
                        python='python')
            else:
                pip.install('--no-deps --upgrade {}'.format(os.path.join(buildbotSource, 'master')),
                        python='python')

            if env.get('installPrivateData'):
                self.task_updatePrivateData()

    def task_update(self):
        """
        Update config and restart.
        """
        self.update()
        self.task_restart()


    def task_dump(self, localfile):
        """
        Create a tarball containing all information not currently stored in
        version control and download it to the given C{localfile}.
        """
        with settings(user=self.serviceUser):
            archive.dump({
                'data': 'data',
            }, localfile, exclude=[
                'http.log*',
            ])


    def task_restore(self, localfile):
        """
        Restore all information not stored in version control from a tarball
        on the invoking users machine.
        """
        msg = 'The whole data directory will be replaced with the backup.'

        if confirm(msg):
            with settings(user=self.serviceUser):
                archive.restore({
                    'data': 'data',
                }, localfile)



addTasks(globals(), Buildbot('bb-master').getTasks())
