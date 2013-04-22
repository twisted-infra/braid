from fabric.api import run


def install(package, python='pypy'):
    if python == 'pypy':
        pip = '~pypy/bin/pip'
    else: #FIXME https://github.com/twisted-infra/braid/issue/5
        pip = 'pip'
    run('{} install --user {}'.format(pip, package))
