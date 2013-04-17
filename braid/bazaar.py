import os

from fabric.api import run

from braid import package, fails


def install():
    package.install('bzr')


def branch(branch, location):
    # TODO: Change sudo to run and provide a context manager to override the
    # user when calling run
    if fails('[ -d {}/.bzr ]'.format(location)):
        run('mkdir -p {}'.format(os.path.dirname(location)))
        run('bzr branch {} {}'.format(branch, location))
    else:
        # FIXME: We currently don't check that this the correct branch
        run('bzr update {}'.format(location))
