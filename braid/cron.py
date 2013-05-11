from fabric.api import run, settings


def install(user, file):
    with settings(user=user):
        run('/usr/bin/crontab {}'.format(file))
