import os

from fabric.api import sudo, prefix


def install(venv, package):
    # TODO: pip as an -E option for virtualenv
    venv = os.path.join(venv, 'bin', 'activate')

    with prefix('source {}'.format(venv)):
        sudo('pip install {}'.format(package))
