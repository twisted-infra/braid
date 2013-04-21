"""
Support for multiple environments based on python configuration files.
"""

from __future__ import print_function, absolute_import

import imp
import os

from twisted.python.filepath import FilePath

from fabric.api import env, task


CONFIG_DIRS = [
    '~/.braid',
    './braidrc.local',
]


def loadEnvironmentConfig(envName, directories=CONFIG_DIRS, extension='.py'):
    """
    Loads configuration directives for the specified environment into Fabric's
    C{env} variable.

    This function tries to load a python module from each specified directory
    and stores all of its public uppercase attributes as attributes of Fabric's
    environment (all attribute names will be lowercased).
    """
    for confDir in directories:
        path = FilePath(os.path.expanduser(confDir)).child(envName + extension)
        if path.exists():
            module = imp.load_source('braid.settings.' + envName, path.path)
            for k in dir(module):
                if k == k.upper():
                    setattr(env, k.lower(), getattr(module, k))


@task
def environment(env):
    """
    Load the passed environment configuration.
    This task can be invoked before executing the desired Fabric action.
    """
    loadEnvironmentConfig(env)


@task
def test():
    """
    Load the configuration for the testing environment.
    Shortcut for the C{environment:testing} task.
    """
    loadEnvironmentConfig('testing')


@task
def prod():
    """
    Load the configuration for the production environment.
    Shortcut for the C{environment:production} task.
    """
    loadEnvironmentConfig('production')
