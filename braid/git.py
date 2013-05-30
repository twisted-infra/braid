from fabric.api import run, cd

from braid import package, fails


def install():
    package.install(['git'])


def branch(url, destination):
    if fails('/usr/bin/test -d {}/.git'.format(destination)):
        run('/usr/bin/git clone {} {}'.format(url, destination))
    else:
        # FIXME: We currently don't check that this the correct branch
        # https://github.com/twisted-infra/braid/issues/5
        with cd(destination):
            run('/usr/bin/git fetch origin')
            run('/usr/bin/git reset --hard origin')
