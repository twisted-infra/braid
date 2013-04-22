from fabric.api import run


def install(package, python='pypy'):
    if python == 'pypy':
        pip = '~pypy/bin/pip'
    else: #FIXME (see #4)
        pip = 'pip'
    run('{} install --user {}'.format(pip, package))
