from fabric.api import run, cd

from braid import package, fails


def install():
    package.install(['git'])


def branch(branch, location):
    if fails('/usr/bin/test -d {}/.git'.format(location)):
        run('/usr/bin/git clone {} {}'.format(branch, location))
    else:
        # FIXME: We currently don't check that this the correct branch
        # https://github.com/twisted-infra/braid/issues/5
        with cd(location):
            run('/usr/bin/git fetch origin')
            run('/usr/bin/git reset --hard origin')
