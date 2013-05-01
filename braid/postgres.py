from fabric.api import sudo
from braid import package


def install():
    package.install(['postgresql-9.1', 'postgresql-server-dev-9.1'])


def createUser(name):
    sudo('createuser -D -R -S {}'.format(name), user='postgres')


def createDb(name, owner):
    sudo('createdb -O {} {}'.format(owner, name), user='postgres')
