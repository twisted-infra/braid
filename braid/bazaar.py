import os

from fabric.api import run

from braid import package, fails


def install():
    package.install(['bzr'])


def branch(branch, location):
    if fails('/usr/bin/test -d {}/.bzr'.format(location)):
        run('/bin/mkdir -p {}'.format(os.path.dirname(location)))
        run('/usr/bin/bzr branch {} {}'.format(branch, location))
    else:
        run('/usr/bin/bzr pull --verbose --overwrite -d {} {}'.format(location, branch), pty=False)
