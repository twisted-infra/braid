"""
Support for multiple environments based on python configuration files.
"""

from __future__ import print_function, absolute_import

import os

from twisted.python.filepath import FilePath

from fabric.api import env, task

from braid.settings import ENVIRONMENTS


CONFIG_DIRS = [
    '~/.config/braid',
]

def loadEnvironmentConfig(envFile):
    """
    Loads configuration directives for the specified environment into Fabric's
    C{env} variable.

    This function tries to load a python module from each specified directory
    and stores all of its public uppercase attributes as attributes of Fabric's
    environment (all attribute names will be lowercased).
    """
    envName = os.path.splitext(envFile.basename())[0]
    ENVIRONMENTS.setdefault(envName, {})
    glob = { '__file__': envFile.path }
    exec envFile.getContent() in glob
    ENVIRONMENTS[envName].update(glob['ENVIRONMENT'])


def loadEnvironments(directories=CONFIG_DIRS):
    for directory in directories:
        confDir = FilePath(os.path.expanduser(directory))
        for envFile in confDir.globChildren('*.env'):
            loadEnvironmentConfig(envFile)


loadEnvironments()

def environment(envName):
    """
    Load the passed environment configuration.
    This task can be invoked before executing the desired Fabric action.
    """
    env.update(ENVIRONMENTS[envName])


for envName in ENVIRONMENTS:
    globals()[envName] = task(name=envName)(lambda: environment(envName))
