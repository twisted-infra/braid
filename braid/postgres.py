from braid import package


def install():
    package.install('postgresql-9.1')
    package.install('postgresql-server-dev-9.1')


def createuser(name):
    pass


def createdb(name, owner):
    pass
