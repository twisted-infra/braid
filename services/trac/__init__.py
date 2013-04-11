from fabric.api import task, settings

from fablib import postgres, requires_root, bazaar, pip
from fablib.twisted import service


@task
@requires_root
def install():
    # Bootstrap a new service environment
    service.bootstrap('trac', python='python2.7')

    # Install and setup postgres
    postgres.install()

    # Get the modified source tree
    bazaar.install()
    with settings(sudo_user='trac'):
        # TODO: Repackage this in order to be able to run setup.py
        bazaar.branch('lp:~exarkun/+junk/trac', '/srv/trac/src/Trac-0.11.6-py2.7.egg')

    pip.install('/srv/trac/venv', 'genshi')
    pip.install('/srv/trac/venv', 'psycopg2')
