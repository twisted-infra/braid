from fabric.api import run


def install(package):
    run('pip install --user {}'.format(package))
