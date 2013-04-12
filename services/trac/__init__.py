import os

from fabric.api import task, sudo, put, prefix

from fablib import postgres, requires_root, bazaar, pip, authbind, fails
from fablib.twisted import service


@task
@requires_root
def install():
    # Bootstrap a new service environment (we can't use pypy here because
    # psycopg2 does not build on it)
    service.bootstrap('trac', python='python2.7')

    # Install and setup postgres
    postgres.install()

    # Install the modified source tree
    bazaar.install()
    pip.install('/srv/trac/venv', 'bzr+lp:~jonathan-9/+junk/trac')

    # Initialize a trac environment
    # NOTE: This may be replaced with a second checkout if needed
    # TODO: Replace the arguments with actual values
    with prefix('source /srv/trac/venv/bin/activate'):
        if fails('[ -d /srv/trac/trac-env ]'):
            sudo('trac-admin /srv/trac/trac-env initenv "{}" {} svn {}'.format(
                'Twisted',
                'sqlite:db/trac.db',
                '/srv/trac/repo'
            ), user='trac')

        # Create the deployment script
        if fails('[ -f /srv/trac/trac-env/deploy/trac_wsgi.py ]'):
            sudo('trac-admin /srv/trac/trac-env deploy '
                 '/srv/trac/trac-env/deploy', user='trac')
            sudo('mv /srv/trac/trac-env/deploy/cgi-bin/trac.wsgi '
                 '/srv/trac/trac-env/deploy/trac_wsgi.py', user='trac')
            sudo('rm -rf /srv/trac/trac-env/deploy/cgi-bin', user='trac')
    # TODO: Remove or move the rest of the deploy directory

    # Setup authbind
    # TODO: Multiple services will be deployed on :80, trac will be only a
    # single component. This will be moved elsewhere.
    authbind.install()
    authbind.allow('trac', 80)

    # Install initscript
    initscript = os.path.join(os.path.dirname(__file__), 'initscript.sh')
    put(initscript, '/srv/trac/etc/init.d/trac', use_sudo=True, mode=0755)
    sudo('chown trac:trac /srv/trac/etc/init.d/trac')
    sudo('ln -fs /srv/trac/etc/init.d/trac /etc/init.d/trac')
    sudo('update-rc.d trac defaults')


@task
def update():
    # TODO
    pass


@task
def start():
    service.start('trac')


@task
def stop():
    service.stop('trac')


@task
def restart():
    service.restart('trac')
