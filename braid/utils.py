from __future__ import print_function

import importlib
import sys
from functools import WRAPPER_ASSIGNMENTS

from fabric.api import env, sudo, run, quiet


def load_config(path):
    module = importlib.import_module(path)
    for k in dir(module):
        if k == k.upper():
            setattr(env, k.lower(), getattr(module, k))


def succeeds(cmd, useSudo=False):
    func = sudo if useSudo else run
    with quiet():
        return func(cmd).succeeded


def fails(cmd, useSudo=False):
    return not succeeds(cmd, useSudo)


class requiresRoot(object):
    canRoot = None

    def __init__(self, func):
        self._func = func
        for attr in WRAPPER_ASSIGNMENTS:
            setattr(self, attr, getattr(func, attr))

    def hasSudoCapabilities(self):
        if requiresRoot.canRoot is None:
            with quiet():
                requiresRoot.canRoot = run('sudo -n whoami').succeeded
        return requiresRoot.canRoot

    def __repr__(self):
        return repr(self._func)

    def __call__(self, *args, **kwargs):
        if self.hasSudoCapabilities():
            return self._func(*args, **kwargs)
        else:
            name = self._func.__name__
            if self.func.__module__:
                name = self.func.__module__ + '.' + name
            print('The execution of the function {} requires root '
                  'privileges.'.format(name))
            sys.exit(1)
