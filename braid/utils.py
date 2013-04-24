from __future__ import print_function

import functools

from fabric.api import env, sudo, run, quiet


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


def cacheInEnvironment(f):
    """
    Decorator that caches the return value in fabric's environment.

    The name used is the name of the function.
    """
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        result = env.get(f.__name__)
        if result is None:
            result = f(*args, **kwargs)
            env[f.__name__] = result
        return result
    return wrapper
