from braid.api import sudo, abort

from braid.info import distroFamily

def install(packages):
    """
    Install a list of packages.
    """
    if distroFamily() == 'debian':
        sudo('/usr/bin/apt-get --yes --quiet install {}'.format(" ".join(packages)))
    elif distroFamily() == 'fedora':
        sudo('/usr/bin/yum install -y {}'.format(" ".join(packages)))
    else:
        abort('Unknown distro.')
