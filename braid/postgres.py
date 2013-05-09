from fabric.api import sudo, quiet, get, task, env, put, run, settings
from braid import package
from pipes import quote


def install():
    package.install(['postgresql-9.1', 'postgresql-server-dev-9.1'])

def _runQuery(query):
    with quiet():
        return sudo('psql --no-align --no-readline --no-password --quiet '
                    '--tuples-only -c {}'.format(quote(query)),
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
        sudo('createdb -O {} {}'.format(owner, name), user='postgres', pty=False)


def dropDb(name):
    return _runQuery('drop database if exists {};'.format(quote(name)))


@task
def dump(name, localpath):
    temp = sudo('mktemp', user='postgres')
    cmd = [
        'pg_dump',
        '--blobs',
        '--no-owner',
        '--format', 'custom',
        '--file', temp,
        '--compress', '9',
        name,
    ]
    sudo(' '.join(cmd), user='postgres')
    sudo('chown {}:{} {}'.format(env.user, env.user, temp))
    get(temp, localpath)
    sudo('rm {}'.format(temp))


@task
def restore(dump, database, user=None, clean=False):
    """
    If the user is not specified, set the owner to the current active SSH user.
    This function only works for postgres users which have a corresponding
    system user.
    """
    if user is None:
        user = env.user

    if clean:
        dropDb(database)

    createDb(database, user)

    with settings(user=user):
        temp = run('mktemp')
        put(dump, temp, mode=0600)
        cmd = [
            'pg_restore',
            '--dbname', database,
            '--schema', 'public',
            '--clean' if clean else '',
            temp,
        ]
        run(' '.join(cmd))
        run('rm {}'.format(temp))
