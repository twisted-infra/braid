import os

from fabric.api import run, sudo

from fablib import package, fails


def install():
    package.install('bzr')


def branch(branch, location):
    # TODO: Change sudo to run and provide a context manager to override the
    # user when calling run
    if fails('[ -d {}/.bzr ]'.format(location)):
        sudo('mkdir -p {}'.format(os.path.dirname(location)))
        sudo('bzr branch {} {}'.format(branch, location))
    else:
        # FIXME: We currently don't check that this the correct branch
        sudo('bzr update {}'.format(location))
