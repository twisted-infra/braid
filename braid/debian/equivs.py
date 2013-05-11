from cStringIO import StringIO
from twisted.python.filepath import FilePath
from fabric.api import cd, sudo
from braid.utils import tempfile

def _generateControlFile(package, provides, description=None):
    """
    Generate a control file for C{package}.

    @returns: the control file
    @rtype: L{file}-like
    """
    if description is None:
        description = 'Dummy provider of %s.' % provides

    template = FilePath(__file__).sibling('equivs.control').getContent()
    body = template.format(package=package, provides=provides, description=description)
    return StringIO(body)

def installEquiv(package, provides, description=None):
    control = _generateControlFile(package, provides, description)
    with tempfile(control) as controlFile, cd('/root'):
        sudo('/usr/bin/equivs-build {}'.format(controlFile))
        sudo('/usr/bin/dpkg -i {}_1.0_all.deb'.format(package))
