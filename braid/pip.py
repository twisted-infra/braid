from fabric.api import run, cd, sudo

from os import path

from braid import info

pipURL = 'https://bootstrap.pypa.io/get-pip.py'


def install(python):

    with cd('/tmp'):
        sudo('/usr/bin/wget -nc {}'.format(pipURL))

    sudo("{python} {pipURL}".format(
        python=python,
        pipURL=path.join('/tmp/', path.basename(pipURL))))

    # Ensure we have the latest pip, virtualenv, setuptools, and wheel.
    sudo("{} -m pip install -U pip virtualenv setuptools wheel".format(python))
