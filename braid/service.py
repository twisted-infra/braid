from fabric.api import sudo, run


def _service(action, service, useSudo=True):
    cmd = sudo if useSudo else run
    cmd('/usr/bin/service {} {}'.format(service, action))


def start(service, useSudo=True):
    _service('start', service, useSudo)


def stop(service, useSudo=True):
    _service('stop', service, useSudo)


def restart(service, useSudo=True):
    _service('restart', service, useSudo)


def enable(service, useSudo=True):
    sudo('/usr/sbin/update-rc.d {} defaults'.format(service))
    _service('start', service, useSudo)


def disable(service, useSudo=True):
    _service('stop', service, useSudo)
    sudo('/usr/sbin/update-rc.d -f {} remove'.format(service))
