from __future__ import print_function


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
