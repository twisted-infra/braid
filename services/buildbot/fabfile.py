import os

from fabric.api import settings, run, env, execute, cd, put, puts, abort
from fabric.contrib import files

from braid import git, cron, pip, archive, config
from braid.twisted import service
from braid.tasks import addTasks
from braid.utils import confirm

__all__ = ['config']

class Buildbot(service.Service):

    python = "python"

    def task_install(self):
        """
        Install buildbot.
        """
        self.bootstrap()

        with settings(user=self.serviceUser):
            execute(self.update)
            run('/bin/ln -nsf {}/start {}/start'.format(self.configDir, self.binDir))
            run('/bin/mkdir -p ~/data')
            run('/bin/mkdir -p ~/data/build_products')
            run('/bin/ln -nsf ~/data/build_products {}/master/public_html/builds'.format(self.configDir))
            cron.install(self.serviceUser, '{}/crontab'.format(self.configDir))

    def task_installTestData(self):
        """
        Do test environment setup (with fake passwords, etc).
        """
        if env.get('environment') == 'production':
           abort("Don't use testInit in production.")

        targetPath = os.path.join(self.configDir, 'master')
        with settings(user=self.serviceUser), cd(targetPath):
            puts('Copying testing private.py to %s' % (targetPath,))
            run('/bin/cp private.py.sample private.py')
            puts('Migrating SQLite db.')
            run('~/virtualenv/bin/buildbot upgrade-master')
            puts('Copying migrated state.sqlite db to ~/data')
            run('/bin/mkdir -p ~/data')
            run('/bin/cp state.sqlite ~/data')

    def task_updatePrivateData(self):
        """
        Update private config.
        """
        with settings(user=self.serviceUser):
            git.branch(
                'buildbot@wolfwood.twistedmatrix.com:/git/buildbot-secrets',
                '~/private')

    def update(self):
        """
        Update
        """
        with settings(user=self.serviceUser):
            run('mkdir -p ' + self.configDir)
            put(
                os.path.dirname(__file__) + '/master/*', self.configDir + "/master/",
                mirror_local_mode=True)
            run('mkdir -p ' + self.configDir + "/twisted_view")
            run('mkdir -p ' + self.configDir + "/twisted_view/buildbot_twisted_view")
            put(
                os.path.dirname(__file__) + '/twisted_view/*.py', self.configDir + "/twisted_view/",
                mirror_local_mode=True)
            put(
                os.path.dirname(__file__) + '/twisted_view/buildbot_twisted_view/*', self.configDir + "/twisted_view/buildbot_twisted_view/",
                mirror_local_mode=True)
            buildbotSource = os.path.join(self.configDir, 'buildbot-source')
            git.branch('https://github.com/buildbot/buildbot', buildbotSource)

            with cd(buildbotSource):
                run('npm install gulp')

            self.venv.install("mock")

            with cd(buildbotSource + "/pkg/"):
                self.venv.run("setup.py install")

            with cd(buildbotSource + "/master/"):
                self.venv.run("setup.py install")

            with cd(buildbotSource + "/www/base/"):
                self.venv.run("setup.py install")

            with cd(buildbotSource + "/www/waterfall_view/"):
                self.venv.run("setup.py install")

            with cd(buildbotSource + "/www/console_view/"):
                self.venv.run("setup.py install")

            with cd(self.configDir + '/twisted_view'):
                self.venv.run('setup.py install')

            if env.get('installPrivateData'):
                self.task_updatePrivateData()
            else:
                execute(self.task_installTestData)

    def updatefast(self):
        """
        Update only some of the config.
        """
        with settings(user=self.serviceUser):
            put(
                os.path.dirname(__file__) + '/master/twisted_*',
                self.configDir + "/master/",
                mirror_local_mode=True)
            put(
                os.path.dirname(__file__) + '/master/master.cfg',
                self.configDir + "/master/",
                mirror_local_mode=True)

            put(
                os.path.dirname(__file__) + '/twisted_view/setup.py', self.configDir + "/twisted_view/setup.py",
                mirror_local_mode=True)
            put(
                os.path.dirname(__file__) + '/twisted_view/buildbot_twisted_view/*', self.configDir + "/twisted_view/buildbot_twisted_view/",
                mirror_local_mode=True)

            with cd(self.configDir + '/twisted_view'):
                self.venv.run('setup.py install')

            if env.get('installPrivateData'):
                self.task_updatePrivateData()

    def task_update(self):
        """
        Update config and restart.
        """
        self.update()
        self.task_restart()


    def task_updatefast(self):
        """
        Update config and restart.
        """
        self.updatefast()
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
