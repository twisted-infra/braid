from fabric.api import sudo, task, put

from twisted.python.filepath import FilePath

from braid import pypy

@task
def bootstrap():
    """
    Prepare the machine to be able to correctly install, configure and execute
    twisted services.
    """

    # Each service specific system user shall be added to the 'service' group
    sudo('groupadd -f --system service')

    pypy.install()
