import os

from fabric.api import run

from braid import package, fails


def install():
    package.install(['bzr'])


def branch(branch, location):
    if fails('[ -d {}/.bzr ]'.format(location)):
        run('mkdir -p {}'.format(os.path.dirname(location)))
        run('bzr branch {} {}'.format(branch, location))
    else:
        run('bzr pull --overwrite -d {} {}'.format(location, branch))
