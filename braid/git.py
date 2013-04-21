from fabric.api import run, cd

from braid import package, fails


def install():
    package.install('git')


def branch(branch, location):
    # TODO: Change sudo to run and provide a context manager to override the
    # user when calling run
    if fails('[ -d {}/.git ]'.format(location)):
        run('git clone {} {}'.format(branch, location))
    else:
        # FIXME: We currently don't check that this the correct branch
        with cd(location):
            run('git fetch origin')
            run('git reset --hard origin')
