from fabric.api import run, cd, settings, sudo
from fabric.contrib import files

from os import path

pipURL = 'https://bootstrap.pypa.io/get-pip.py'

getPipDirectory = "/opt/pip"
getPipLocation = path.join(getPipDirectory, "get-pip.py")


def ensureGetPip(target=getPipDirectory, update=False):
    """
    Ensure we have C{get-pip.py} available in our expected location.
    """
    if update or not files.exists(getPipLocation):
        sudo("mkdir -p {}".format(getPipDirectory))
        with cd(getPipDirectory):
            sudo('/usr/bin/wget -O {}'.format(getPipLocation, pipURL))
        sudo('chmod a+r {}'.format(getPipLocation))


def bootstrap(user, python, updateDependencies=False):
    """
    Bootstrap pip and virtualenv.
    """
    ensureGetPip(update=updateDependencies)

    with settings(user=user):
        run("{python} {getPipLocation} --user".format(
            python=python,
            getPipLocation=getPipLocation))

        # See https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning
        run("{} -m pip install --user -U ndg-httpsclient".format(python))

        # Ensure we have the latest pip, virtualenv, setuptools, and wheel.
        run("{} -m pip install --user -U"
            " pip virtualenv setuptools wheel".format(python))
