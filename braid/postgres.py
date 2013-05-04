from fabric.api import sudo, hide
from braid import package
from pipes import quote


def install():
    package.install(['postgresql-9.1', 'postgresql-server-dev-9.1'])


def _runQuery(query, database=None):
    with hide('running', 'output'):
        database = '--dbname={}'.format(database) if database else ''
        return sudo('psql --no-align --no-readline --no-password --quiet '
                    '--tuples-only {} -c {}'.format(database, quote(query)),
                    user='postgres', pty=False, combine_stderr=False)


def _dbExists(name):
    res = _runQuery("select count(*) from pg_database "
                    "where datname = '{}';".format(name))
    return res == '1'


def _userExists(name):
    res = _runQuery("select count(*) from pg_user "
                    "where usename = '{}';".format(name))
    return res == '1'


def createUser(name):
    if not _userExists(name):
        sudo('createuser -D -R -S {}'.format(name), user='postgres', pty=False)


def createDb(name, owner):
    if not _dbExists(name):
        sudo('createdb -O {} {}'.format(owner, name), user='postgres',
             pty=False)


def grantRead(user, database):
    """
    Grant read permissions to C{user} to all tables in C{database}.
    """


def grantReadWrite(user, database):
    """
    Grant read and write permissions to C{user} to all tables in C{database}.
    """
