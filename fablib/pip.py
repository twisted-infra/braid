import os

from fabric.api import run, prefix


def install(venv, package):
    # TODO: pip as an -E option for virtualenv
    venv = os.path.join(venv, 'bin', 'activate')

    with prefix('source {}'.format(venv)):
        run('pip install {}'.format(package))
