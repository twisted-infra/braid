from __future__ import print_function

import importlib
import functools

from fabric.api import env, sudo, run, quiet, abort


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


def hasSudoCapabilities():
    env.setdefault('canRoot', {})
    if env.canRoot.get(env.host_string) is None:
        with quiet():
            env.canRoot[env.host_string] = run('sudo -n whoami').succeeded
    return env.canRoot[env.host_string]

def requiresRoot(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if hasSudoCapabilities():
            return f(*args, **kwargs)
        else:
            name = f.__name__
            if f.__module__:
                name = f.__module__ + '.' + name
            abort('The execution of the function {} requires root '
                  'privileges.'.format(name))
    return wrapper
