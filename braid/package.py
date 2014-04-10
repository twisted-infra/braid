from braid.api import sudo, abort

from braid.info import distroFamily

def update():
    """
    Update package list.
    """
    if distroFamily() == 'debian':
        sudo('/usr/bin/apt-get update')
    elif distroFamily() == 'fedora':
        # Automatic
        pass
    elif distroFamily() == 'freebsd':
        sudo('/usr/sbin/pkg update')
    else:
        abort('Unknown distro.')


def install(packages):
    """
    Install a list of packages.
    """
    if distroFamily() == 'debian':
        sudo('/usr/bin/apt-get --yes --quiet install {}'.format(" ".join(packages)))
    elif distroFamily() == 'fedora':
        sudo('/usr/bin/yum install -y {}'.format(" ".join(packages)))
    elif distroFamily() == 'freebsd':
        sudo('/usr/sbin/pkg install -y {}'.format(" ".join(packages)))
    else:
        abort('Unknown distro.')
