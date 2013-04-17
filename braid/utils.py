from __future__ import print_function
import importlib
import sys

from fabric.api import env, sudo, run, quiet


def load_config(path):
    module = importlib.import_module(path)
    for k in dir(module):
        if k == k.upper():
            setattr(env, k.lower(), getattr(module, k))


def succeeds(cmd, use_sudo=False):
    func = sudo if use_sudo else run
    with quiet():
        return func(cmd).succeeded


def fails(cmd, use_sudo=False):
    return not succeeds(cmd, use_sudo)


class requires_root(object):
    can_root = None

    def __init__(self, func):
        self.func = func

    def has_sudo_capabilities(self):
        if requires_root.can_root is None:
            with quiet():
                requires_root.can_root = run('sudo -n whoami').succeeded
        return requires_root.can_root

    def __call__(self, *args, **kwargs):
        if self.has_sudo_capabilities():
            return self.func(*args, **kwargs)
        else:
            name = self.func.__name__
            if self.func.__module__:
                name = self.func.__module__ + '.' + name
            print('The execution of the function {} requires root '
                  'privileges.'.format(name))
            sys.exit(1)
