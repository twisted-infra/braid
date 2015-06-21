"""
Tools to administer mailman.
"""
from fabric.api import settings, put, sudo
from twisted.python.util import sibpath
from braid import tasks, service, package, archive
from braid.debian import debconf
from braid.utils import confirm

from braid import config
__all__ = [ 'config' ]


class Service(tasks.Service):

    serviceUser = 'list'

    def task_dump(self, dump):
        """
        Dump mailman data.
        """
        with settings(user=self.serviceUser):
            archive.dump({
                'lists': 'lists',
                'data': 'data',
                'archives': 'archives'
            }, dump)

    def task_restore(self, dump):
        """
        Restore mailman data.
        """
        msg = 'All mailman state and archives will be replaced with the backup.'
        if confirm(msg):
            with settings(user=self.serviceUser):
                archive.restore({
                    'lists': 'lists',
                    'data': 'data',
                    'archives': 'archives'
                }, dump)

    def task_install(self):
        """
        Install mailman.
        """
        debconf.setDebconfValue('mailman', 'mailman/site_languages', 'multiselect', 'en')
        debconf.setDebconfValue('mailman', 'mailman/create_site_list', 'note', '')
        package.install(['mailman'])
        put(sibpath(__file__, 'mm_cfg.py'), '/etc/mailman/mm_cfg.py', use_sudo=True)
        sudo('/usr/sbin/usermod -a -G service --home /var/lib/mailman {}'.format(self.serviceUser))

    def task_start(self):
        """
        Start mailman.
        """
        service.start('mailman')

    def task_stop(self):
        """
        Stop mailman.
        """
        service.stop('mailman')

    def task_restart(self):
        """
        Restart mailman.
        """
        service.restart('mailman')




tasks.addTasks(globals(), Service().getTasks())

