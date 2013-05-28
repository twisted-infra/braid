from fabric.api import run, quiet
from braid import succeeds, cacheInEnvironment

@cacheInEnvironment
def distroName():
    """
    Get the name of the distro.
    """
    with quiet():
        lsb = run('/usr/bin/lsb_release --id --short', warn_only=True)
        if lsb.succeeded:
            return lsb.lower()

        distros = [
                ('centos', '/etc/centos-release'),
                ('fedora', '/etc/fedora-release'),
                ]
        for distro, sentinel in distros:
            if succeeds('/usr/bin/test -f {}'.format(sentinel)):
                return distro



def distroFamily():
    """
    Get the family of the distro.

    @returns: C{'debian'} or C{'fedora'}
    """
    families = {
            'debian': ['debian', 'ubuntu'],
            'fedora': ['fedora', 'centos', 'rhel'],
            }
    distro = distroName()
    for family, members in families.iteritems():
        if distro in members:
            return family
    return 'other'


@cacheInEnvironment
def arch():
    """
    Get the architechture of the machine.
    """
    return run('/bin/uname --machine')



@cacheInEnvironment
def isRoot():
    """
    Check if the current user is root.
    """
    return run('id -u') == '0'



__all__ = ['distroName', 'distroFamily', 'arch']
