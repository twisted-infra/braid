from fabric.api import run

from braid import info


def install(package, python='pypy'):
    pip = '/usr/bin/pip'
    if python == 'pypy':
        pip = '~pypy/bin/pip'
    elif python == 'system':
        #FIXME https://github.com/twisted-infra/braid/issue/5
        if info.distroFamily() == 'fedora':
            pip = '/usr/bin/pip-python'
        else:
            pip = '/usr/bin/pip'
    run('{} install --user {}'.format(pip, package))
