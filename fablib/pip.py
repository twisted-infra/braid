import os

from fabric.api import sudo, prefix, run


def install(venv, package):
    # TODO: pip as an -E option for virtualenv
    venv = os.path.join(venv, 'bin', 'activate')

    user = run('stat -c \'%U\' {}'.format(venv))

    with prefix('source {}'.format(venv)):
        sudo('pip install {}'.format(package), user=user)
