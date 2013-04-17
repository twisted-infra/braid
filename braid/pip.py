import os

from fabric.api import run, prefix


def install(package):
    run('pip install --user {}'.format(package))
