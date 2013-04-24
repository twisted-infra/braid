from fabric.api import run, settings


def install(user, file):
    with settings(user=user):
        run('crontab {}'.format(file))
