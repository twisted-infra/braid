from __future__ import absolute_import

import functools
import contextlib
import imp

from twisted.python.filepath import FilePath

from fabric.api import env, sudo, run, quiet, get, put, hide


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
            env.canRoot[env.host_string] = run('/usr/bin/sudo -n '
                                               '/usr/bin/whoami').succeeded
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



@contextlib.contextmanager
def tempfile(uploadFrom=None, saveTo=None, suffix=''):
    """
    Context manager to create and remove a temporary file during the execution
    of its context.

    If the C{uploadFrom} argumment is provided, the content of the temporary
    file will be set to the contents of the local file prior execution.

    If the C{saveTo} argument is provided, the content of the temporary file
    will be downloaded locally upon successful execution.
    """
    with hide('output'):
        temp = run('/bin/mktemp -t braid-tmp-XXXXXXXX --suffix={}'.format(suffix))
    try:
        if uploadFrom:
            put(uploadFrom, temp, mode=0600)
        yield temp
    except:
        raise
    else:
        if saveTo:
            get(temp, saveTo)
    finally:
        run('/bin/rm -f {}'.format(temp))



@contextlib.contextmanager
def tempdir():
    with hide('output'):
        temp = run('/bin/mktemp -d -t braid-tmp-XXXXXXXX')
    try:
        yield temp
    except:
        raise
    finally:
        run('/bin/rm -rf {}'.format(temp))


def loadServices(base):
    from braid import config

    services = {}
    servicesDir = FilePath(base).sibling('services')
    for serviceDir in servicesDir.children():
        serviceName = serviceDir.basename()
        fabfile = serviceDir.child('fabfile.py')
        if fabfile.exists():
            module = imp.load_source(serviceName, fabfile.path, fabfile.open())
            if module.config == config:
                del module.config
            services[serviceName] = module
    return services
