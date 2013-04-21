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
    for dir in directories:
        path = FilePath(os.path.expanduser(dir)).child(envName + extension)
        if path.exists():
            module = imp.load_source('braid.settings.' + envName, path.path)
            for k in dir(module):
                if k == k.upper():
                    setattr(env, k.lower(), getattr(module, k))


@task
def environment(env):
    """
    Loads the passed environment configuration. This task can be invoked before
    executing the desired Fabric action.
    """
    loadEnvironmentConfig(env)


@task
def test():
    """
    Shortcut for the C{environment:testing} task.
    """
    loadEnvironmentConfig('testing')


@task
def prod():
    """
    Shortcut for the C{environment:production} task.
    """
    loadEnvironmentConfig('production')
