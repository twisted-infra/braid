from __future__ import print_function, absolute_import
from fabric.api import task, sudo
from fabric.contrib import files

from twisted.python.filepath import FilePath


@task
def create(username, homeBase='/home'):
    """
    Creates a new user for everyday use.
    """
    return sudo('useradd --base-dir {} --user-group --create-home '
                '--shell /bin/bash {}'.format(homeBase, username))


@task
def uploadKeys(user, keyfile):
    """
    Add keys from an authorized_keys file to a given user.
    """
    # FIXME: Detect whether we are already connecting as the user who's
    # keys we are modifying, and don't use sudo then.
    keys = FilePath(keyfile).getContent().splitlines()
    sudo('mkdir -p ~{}/.ssh'.format(user))
    files.append('~{}/.ssh/authorized_keys'.format(user), keys, use_sudo=True)


