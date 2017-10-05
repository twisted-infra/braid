import os

from fabric.api import settings, run, env, cd, put, puts, abort

from braid import git, cron, archive, config, authbind
from braid.twisted import service
from braid.tasks import addTasks
from braid.utils import confirm

__all__ = ['config']

class Buildbot(service.Service):

    python = 'python'

    def task_install(self):
        """
        Install buildbot.
        """
        self.bootstrap()

        # Setup authbind to be used by HTTP to HTTPS redirection and by
        # the HTTPS proxy.
        authbind.allow(self.serviceUser, 80)
        authbind.allow(self.serviceUser, 443)

        with settings(user=self.serviceUser):
            self.update(_installDeps=True)
            run('/bin/ln -nsf {}/start {}/start'.format(self.configDir, self.binDir))
            run('/bin/mkdir -p ~/data')
            run('/bin/mkdir -p ~/data/build_products')
            run('/bin/ln -nsf ~/data/build_products {}/public_html/builds'.format(self.configDir))
            cron.install(self.serviceUser, '{}/crontab'.format(self.configDir))

    def task_installTestData(self):
        """
        Do test environment setup (with fake passwords, etc).
        """
        if env.get('environment') == 'production':
           abort("Don't use testInit in production.")

        self.task_install()

        targetPath = os.path.join(self.configDir)
        with settings(user=self.serviceUser), cd(targetPath):
            # Copy the new private data for testing.
            puts('Copying testing private.py to %s' % (targetPath,))
            put(
                os.path.dirname(__file__) + '/master/private.py.sample',
                self.configDir + '/private.py',
                mirror_local_mode=True)

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
            put(os.path.dirname(__file__) + '/../../../twisted-infra-secret/buildmaster/private.py',
                self.configDir + "/private.py")

    def task_upgradeMaster(self):
        """
        Only upgrade the master database.
        """
        targetPath = os.path.join(self.configDir)
        with settings(user=self.serviceUser), cd(targetPath):
            run('~/virtualenv/bin/buildbot upgrade-master')
            run('/bin/cp state.sqlite ~/data')

    def update(self, _installDeps=False):
        """
        Update the buildmaster environment.
        """
        with settings(user=self.serviceUser):
            run('mkdir -p ' + self.configDir)
            run('mkdir -p ~/data/certs')
            run('touch ~/data/certs/buildbot.twistedmatrix.com.pem')
            put(
                os.path.dirname(__file__) + '/crontab', self.configDir,
                mirror_local_mode=True)
            put(
                os.path.dirname(__file__) + '/start', self.configDir,
                mirror_local_mode=True)

            buildbotSource = os.path.join(self.configDir, 'buildbot-source')
            buildmasterSource = os.path.join(buildbotSource, 'master')
            # For now we are using a buildbot eight HEAD due to a bug in
            # 0.8.12
            # https://github.com/buildbot/buildbot/pull/1924
            # A forked branch is still used to control its version.
            # If changes are required to this branch it should use a name
            # other than `eight` to reduce confusion.
            buildbotBranch = 'eight'
            git.branch(
                url='https://github.com/twisted-infra/buildbot',
                destination=buildbotSource,
                branch=buildbotBranch,
                )

            self.venv.install_twisted()
            self.venv.install("virtualenv twisted==16.2 txacme==0.9.1 txgithub>=15.0.0")

            if _installDeps:
                # sqlalchemy-migrate only works with a specific version of
                # sqlalchemy.
                self.venv.install(
                    'sqlalchemy==0.7.10 sqlalchemy-migrate==0.7.2 '
                    '{}'.format(buildmasterSource))
            else:
                self.venv.install('--no-deps {}'.format(buildmasterSource))

            self.updatefast()


    def updatefast(self):
        """
        Update only some of the config.
        """
        with settings(user=self.serviceUser):
            put(
                os.path.dirname(__file__) + '/master/*.cfg', self.configDir,
                mirror_local_mode=True)
            put(
                os.path.dirname(__file__) + '/master/*.py', self.configDir,
                mirror_local_mode=True)
            put(
                os.path.dirname(__file__) + '/master/*/*.py', self.configDir,
                mirror_local_mode=True)

            if env.get('installPrivateData'):
                self.task_updatePrivateData()
                redirector_port = 80
            else:
                # Install test configuration.
                self.task_installTestData()
                redirector_port = 8000

            # Update the buildbot application configuration to not use
            # port 80 as it will conflict with the web service which run
            # on the same machine in testing.
            # This is also run in production to make sure that this command
            # is functional.
            run('sed -i s/80/%s/g ~/config/buildbot.tac' % (redirector_port,))


    def task_update(self):
        """
        Update the environment and restart.
        """
        self.update()
        self.task_restart()


    def task_reconfigure(self):
        """
        Update just the configuration and restart.
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



addTasks(globals(), Buildbot('bb-master').getTasks(role='buildbot'))
