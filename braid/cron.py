from __future__ import absolute_import

from braid.api import run, settings, task, put
from twisted.python.util import sibpath


def install(user, file):
    with settings(user=user):
        run('/usr/bin/crontab {}'.format(file))


@task
def installCronic():
    configFile = sibpath(__file__, 'cronic')
    put(configFile, '/usr/local/bin/cronic', use_sudo=True)
