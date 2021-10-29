from fabric.api import sudo, run


def _service(action, service, useSudo=True):
    cmd = sudo if useSudo else run
    cmd('/usr/bin/systemctl {} {}'.format(action, service))


def start(service, useSudo=True):
    _service('start', service, useSudo)


def stop(service, useSudo=True):
    _service('stop', service, useSudo)


def restart(service, useSudo=True):
    _service('restart', service, useSudo)


def enable(service, useSudo=True):
    _service('enable', service, useSudo)
    _service('start', service, useSudo)


def disable(service, useSudo=True):
    _service('disable', service, useSudo)
    _service('stop', service, useSudo)
