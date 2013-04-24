from fabric.api import run, cd

from braid import package, fails


def install():
    package.install(['git'])


def branch(branch, location):
    if fails('[ -d {}/.git ]'.format(location)):
        run('git clone {} {}'.format(branch, location))
    else:
        # FIXME: We currently don't check that this the correct branch
        # https://github.com/twisted-infra/braid/issues/5
        with cd(location):
            run('git fetch origin')
            run('git reset --hard origin')
