"""
Support for www service installation and management.
"""

from fabric.api import run, settings, env, put, sudo

from os import path
from twisted.python.util import sibpath

from braid import authbind, git, cron, archive, pip
from braid.twisted import service
from braid.debian import equivs
from braid.tasks import addTasks
from braid.utils import confirm

from braid import config
__all__ = ['config']


class TwistedWeb(service.Service):
    def task_install(self):
        """
        Install t-web, a Twisted Web based server.
        """
        # Bootstrap a new service environment
        self.bootstrap()

        # Add to www-data group. Mailman depends on this.
        sudo('/usr/sbin/usermod -a -g www-data -G t-web {}'.format(self.serviceUser))

        # Setup authbind
        authbind.allow(self.serviceUser, 80)
        authbind.allow(self.serviceUser, 443)

        # Install httpd equiv, so apt doesn't try to install apache ever
        equivs.installEquiv(self.serviceName, 'httpd')

        with settings(user=self.serviceUser):
            pip.install('txsni', python='pypy')
            run('/bin/ln -nsf {}/start {}/start'.format(self.configDir, self.binDir))
            run('/bin/ln -nsf {}/start-maintenance {}/start-maintenance'.format(self.configDir, self.binDir))
            self.update()
            cron.install(self.serviceUser, '{}/crontab'.format(self.configDir))

            run('/bin/mkdir -p ~/data')
            if env.get('installPrivateData'):
                self.task_installSSLKeys()
                run('/usr/bin/touch {}/production'.format(self.configDir))
            else:
                run('/bin/rm -f {}/production'.format(self.configDir))


    def task_installSSLKeys(self):
        """
        Install SSL keys.
        """
        cert = sibpath(__file__, 'twistedmatrix.com.crt')

        with settings(user=self.serviceUser):
            run('mkdir -p ~/ssl')
            for cert in ['www.twistedmatrix.com.pem',
                         'buildbot.twistedmatrix.com.pem']:
                fullpath = sibpath(__file__, cert)
                if path.exists(fullpath):
                    put(fullpath, '~/ssl/' + cert, mode=0600)
            run('ln -s ~/ssl/www.twistedmatrix.com.pem '
                '~/ssl/twistedmatrix.com.pem')
            run('ln -s ~/ssl/www.twistedmatrix.com.pem ~/ssl/DEFAULT.pem')

    def update(self):
        """
        Update config.
        """
        with settings(user=self.serviceUser):
            git.branch('https://github.com/twisted-infra/t-web', self.configDir)


    def task_update(self):
        """
        Update config and restart.
        """
        self.update()
        self.task_restart()


    def task_dump(self, dump):
        """
        Dump non-versioned resources.
        """
        with settings(user=self.serviceUser):
            archive.dump({
                'data': 'data',
                }, dump)


    def task_restore(self, dump):
        """
        Resotre non-versioned resources.
        """
        msg = 'All non-versioned web resources will be replaced with the backup.'
        if confirm(msg):
            with settings(user=self.serviceUser):
                archive.restore({
                    'data': 'data',
                    }, dump)

    def task_startMaintenanceSite(self):
        """
        Start maintenance site.
        """
        with settings(user=self.serviceUser):
            run('{}/start-maintenance'.format(self.binDir))


    def task_uploadRelease(self, release, releasesTarball):
        """
        Upload a relase.

        It expects a tarball containing the following files:
        - Twisted<Subproject>-<release>.tar.bz2
        - Twisted-<release>.<ext> for all source/windows installers
        - twisted-<release>-<hash>.txt for md5 and sha512
        - doc - for narative documentation
        - api - for api documents

        @param release: Release version.
        @param releasesTarball: Tarball with release tarballs and documentation
        """
        apiVersion = '.'.join(release.split('.')[:2])
        distPaths = {}
        for ext in ['.tar.bz2',
                 '-cp27-none-win32.whl', '.win32-py2.7.exe', '.win32-py2.7.msi',
                 '.win-amd64-py2.7.msi', '.win-amd64-py2.7.exe', '-cp27-none-win_amd64.whl']:
            tarball = 'Twisted-{}{}'.format(release, ext)
            distPaths[tarball] = 'data/releases/Twisted/{}/{}'.format(apiVersion, tarball)
        for subproject in ['Core', 'Conch', 'Lore', 'Mail', 'Names', 'News', 'Pair', 'Runner', 'Web', 'Words']:
            tarball = 'Twisted{}-{}.tar.bz2'.format(subproject, release)
            distPaths[tarball] = 'data/releases/{}/{}/{}'.format(subproject, apiVersion, tarball)

        distPaths['doc'] = 'data/documentation/{}'.format(release)
        distPaths['api'] = 'data/documentation/{}/api'.format(release)
        for hash in ['md5sums', 'shasums']:
            hashFile = 'twisted-{}-{}.txt'.format(release,hash)
            distPaths[hashFile] = 'data/releases/{}'.format(hashFile)

        directories = [path.dirname(file) for file in distPaths.values()]

        with settings(user=self.serviceUser):
            run('/bin/mkdir -p {}'.format(' '.join(set(directories))))
            archive.restore(distPaths, releasesTarball)


    def task_updateCurrentDocumentation(self, release):
        """
        Update the current link for documentation
        """
        with settings(user=self.serviceUser):
            run('/bin/ln -nsf {} data/documentation/current'.format(release))



addTasks(globals(), TwistedWeb('t-web').getTasks())
