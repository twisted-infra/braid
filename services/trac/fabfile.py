import shutil
import os
import tempfile

from fabric.api import abort, env, run, settings, put

from braid import pip, postgres, cron, git, archive, utils
from braid.twisted import service
from braid.utils import confirm

from braid import config
from braid.tasks import addTasks
__all__ = ['config']


class Trac(service.Service):
    def task_install(self):
        """
        Install trac.
        """
        self.bootstrap(python='system')

        with settings(user=self.serviceUser):
            pip.install('psycopg2', python='system')
            self.update(_installDeps=True)

            run('/bin/mkdir -p ~/svn')
            run('/bin/ln -nsf ~/svn {}/trac-env/svn-repo'.format(self.configDir))

            run('/bin/mkdir -p ~/attachments')
            run('/bin/ln -nsf ~/attachments {}/trac-env/files/attachments'.format(
                self.configDir))

            run('/bin/ln -nsf ~/website/trac-files {}/trac-env/htdocs'.format(
                self.configDir))

            run('/bin/ln -nsf {} {}/trac-env/log'.format(self.logDir, self.configDir))

            run('/bin/ln -nsf {}/start {}/start'.format(self.configDir, self.binDir))

            cron.install(self.serviceUser, '{}/crontab'.format(self.configDir))

            # Create an empty password file if not present.
            run('/usr/bin/touch config/htpasswd')

        # FIXME: Make these idempotent.
        postgres.createUser('trac')
        postgres.createDb('trac', 'trac')


    def update(self, _installDeps=False):
        """
        Update trac config.
        """
        with settings(user=self.serviceUser):
            run('mkdir -p ' + self.configDir)
            put(os.path.dirname(__file__) + '/*', self.configDir,
                mirror_local_mode=True)

            run('mkdir -p ~/website/')
            put(os.path.dirname(__file__) + '/../t-web/*', "~/website/",
                mirror_local_mode=True)

            pip.install('trac==1.0.6post2', python='system')
            pip.install('pygments==1.6', python='system')

            if _installDeps:
                pip.install('git+https://github.com/twisted-infra/twisted-trac-plugins.git', python='system')
            else:
                pip.install('--no-deps --upgrade git+https://github.com/twisted-infra/twisted-trac-plugins.git', python='system')
            pip.install('spambayes==1.1b1', python='system')

            pip.install('TracAccountManager==0.4.4', python='system')
            pip.install('svn+https://trac-hacks.org/svn/defaultccplugin/tags/0.2/', python='system')
            pip.install('svn+https://svn.edgewall.org/repos/trac/plugins/1.0/spam-filter@14116', python='system')


    def task_update(self):
        """
        Update config and restart.
        """
        self.update()
        self.task_restart()


    def task_upgrade(self):
        """
        Run a Trac upgrade.
        """
        with settings(user=self.serviceUser):
            self.update()
            run(".local/bin/trac-admin {}/trac-env upgrade".format(self.configDir))
            run(".local/bin/trac-admin {}/trac-env wiki upgrade".format(self.configDir))

        self.task_restart()


    def task_dump(self, localfile):
        """
        Create a tarball containing all information not currently stored in
        version control and download it to the given C{localfile}.
        """
        with settings(user=self.serviceUser):
            with utils.tempfile() as temp:
                postgres.dumpToPath('trac', temp)

                archive.dump({
                    'htpasswd': 'config/htpasswd',
                    'attachments': 'attachments',
                    'db.dump': temp,
                }, localfile)


    def task_restore(self, localfile, restoreDb=True):
        """
        Restore all information not stored in version control from a tarball
        on the invoking users machine.
        """
        restoreDb = str(restoreDb).lower() in ('true', '1', 'yes', 'ok', 'y')

        if restoreDb:
            msg = (
                'All existing files present in the backup will be overwritten and\n'
                'the database dropped and recreated.'
            )
        else:
            msg = (
                'All existing files present in the backup will be overwritten\n'
                '(the database will not be touched).'
            )

        print ''
        if confirm(msg):
            # TODO: Ask for confirmation here
            if restoreDb:
                postgres.dropDb('trac')
                postgres.createDb('trac', 'trac')

            with settings(user=self.serviceUser):
                with utils.tempfile() as temp:
                    archive.restore({
                        'htpasswd': 'config/htpasswd',
                        'attachments': 'attachments',
                        'db.dump': temp,
                    }, localfile)
                    if restoreDb:
                        postgres.restoreFromPath('trac', temp)


    def task_upgrade10(self):
        """
        The on-disk attachment storage location and storage format changed
        between trac 0.11dev+twisted-patches and 1.0.1.
        """

        with settings(user=self.serviceUser):
            self.update()

            # Move the old attachments directory out of the way, but keep it
            # around.
            run("/bin/mv ~/attachments ~/attachments.old")
            # Update the symlink within the git repository that was previously
            # pointing at ~/attachments to point at ~/attachments.old.  Dump
            # and restore work on ~/attachments.
            run("/bin/ln -nsf ~/attachments.old {}/trac-env/attachments".format(self.configDir))

            # Create a new directory at the old attachment location, and point
            # trac 1.0.1's new attachment storage directory at it.
            run("/bin/mkdir ~/attachments")
            run("/bin/mkdir {}/trac-env/files".format(self.configDir))
            # Trac 1.0 moved attachments from trac-env/attachments to
            # trac-env/files/attachments.
            run("/bin/ln -nsf ~/attachments {}/trac-env/files/attachments".format(
                self.configDir))

            # The file format for attachments also changed to be hashed and
            # sharded, so trac-env upgrade is going to look in
            # ~/trac-env/attachments (attachments.old).
            run(".local/bin/trac-admin {}/trac-env upgrade".format(self.configDir))
            # Wiki pages have attachments too, so upgrade any metadata
            # associated with those.
            run(".local/bin/trac-admin {}/trac-env wiki upgrade".format(self.configDir))


    def task_installTestData(self):
        """
        Create an empty trac database for testing.
        """
        if env.get('environment') == 'production':
           abort("Don't use installTestData in production.")

        if postgres.tableExists('trac', 'system'):
           abort("Existing Trac tables found.")

        with settings(user=self.serviceUser):
            # Run trac initenv to create the postgresql database tables, but use
            # a throwaway trac-env directory because that comes from
            # https://github.com/twisted-infra/trac-config/tree/master/trac-env
            try:
                run('~/.local/bin/trac-admin '
                    '/tmp/trac-init initenv TempTrac postgres://@/trac svn ""')
            finally:
                run("rm -rf /tmp/trac-init")

            # Run an upgrade to add plugin specific database tables and columns.
            run('~/.local/bin/trac-admin config/trac-env upgrade --no-backup')



addTasks(globals(), Trac('trac').getTasks())
