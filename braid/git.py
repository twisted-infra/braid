from fabric.api import run, cd, local, lcd, env

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


def push(source, destination):
    """
    Push the given local source directory to the given remote directory,
    detaching the remote directory first so it will accept patches to master.
    """
    with lcd(source):
        with cd(destination):
            run('/usr/bin/git checkout --detach')
            local(
                "git push ssh://{user}@{host}:{port}/{destination} HEAD:master"
                .format(user=env.user, host=env.host, port=env.port,
                        destination=destination)
            )
            run('/usr/bin/git reset --hard master')
