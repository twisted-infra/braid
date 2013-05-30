from __future__ import print_function, absolute_import

try:
    import requests
except ImportError:
    requests = None

from braid.api import task, sudo
from braid.utils import fails
from fabric.contrib import files

from twisted.python.filepath import FilePath


@task
def create(username, homeBase='/home'):
    """
    Creates a new user for everyday use.
    """
    return sudo('/usr/sbin/useradd --base-dir {} --user-group --create-home '
                '--shell /bin/bash {}'.format(homeBase, username))



def createService(username, base='/srv'):
    """
    Create a service user.
    """
    if fails('/usr/bin/id {}'.format(username)):
        sudo('/usr/sbin/useradd --base-dir {} --groups service --user-group '
             '--create-home --system --shell /bin/bash '
             '{}'.format(base, username))



def uploadKeys(user, keys):
    """
    Uplaod a list of keys to a user's autorized_keys file.
    """
    sudo('/bin/mkdir -p ~{}/.ssh'.format(user))
    files.append('~{}/.ssh/authorized_keys'.format(user), keys, use_sudo=True)


@task
def uploadKeyFile(user, keyfile):
    """
    Add keys from an authorized_keys file to a given user.
    """
    # FIXME: Detect whether we are already connecting as the user who's
    # keys we are modifying, and don't use sudo then.
    keys = FilePath(keyfile).getContent().splitlines()
    uploadKeys(user, keys)


@task
def uploadLaunchpadKeys(user, launchpadUser=None):
    if launchpadUser is None:
        launchpadUser = user
    r = requests.get('https://launchpad.net/~{}/+sshkeys'.format(launchpadUser))
    keys = r.text.splitlines()
    uploadKeys(user, keys)

if requests is None:
    del uploadLaunchpadKeys
