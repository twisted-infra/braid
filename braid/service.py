from fabric.api import sudo, run


def _service(action, service, use_sudo=True):
    cmd = sudo if use_sudo else run
    cmd('service {} {}'.format(service, action))


def start(service, use_sudo=True):
    _service('start', service, use_sudo)


def stop(service, use_sudo=True):
    _service('stop', service, use_sudo)


def restart(service, use_sudo=True):
    _service('restart', service, use_sudo)


def enable(service, use_sudo=True):
    sudo('update-rc.d {} defaults'.format(service))
    _service('start', service, use_sudo)


def disable(service, use_sudo=True):
    _service('stop', service, use_sudo)
    sudo('update-rc.d -f {} remove'.format(service))
