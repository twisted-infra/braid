from fabric.api import sudo, hide, get, task, env, put, run, settings
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


def _grantSchemaAccess(database, user):
    # Double quotes tell postgres to consider names as case sensitive. If we
    # omit them and have uppercase chars in the names, the relevant object
    # (user or database) will not be found.
    _runQuery('grant connect on database "{}" to "{}";'.format(database, user))
    _runQuery('grant usage on schema public to "{}";'.format(user), database)


def grantRead(database, user):
    """
    Grant read permissions to C{user} to all tables in C{database}.
    """
    _grantSchemaAccess(database, user)
    # This only affects existing tables. It is possible to set the default
    # privileges on the schema for new objects but this rapidly complicates
    # everything. The simple solution is to just re-run this command
    _runQuery('grant select on all tables in schema public to "{}";'
              .format(user), database)


def grantReadWrite(database, user):
    """
    Grant read and write permissions to C{user} to all tables in C{database}.
    """
    _grantSchemaAccess(database, user)
    _runQuery('grant select, insert, update, delete on all tables in '
              'schema public to "{}";'.format(user), database)
    _runQuery('grant all privileges on all sequences in schema public to "{}";'
              .format(user), database)


def dropDb(name):
    return _runQuery('drop database if exists {};'.format(quote(name)))


@task
def dump(name, localpath):
    """
    Download a dump of the specified database to localpath.
    """
    temp = run('mktemp')
    cmd = [
        'pg_dump',
        '--blobs',
        '--no-owner',
        '--format', 'custom',
        '--file', temp,
        '--compress', '9',
        name,
    ]
    run(' '.join(cmd))
    get(temp, localpath)
    run('rm {}'.format(temp))


@task
def restore(dump, database, user=None, clean=False):
    """
    Upload a local dump and restore it to the named database.

    If no user is specified, set the owner to the current active SSH user.
    This function only works for postgres users which have a corresponding
    system user.

    If clean is specified, the database will be dropped and recreated. The
    database will always be created if it does not exits.
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
