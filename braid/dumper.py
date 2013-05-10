import os

from fabric.api import run, get

from braid import utils
from pipes import quote


def dump(spec, localfile):
    """
    C{spec} is a dictionary of filenames/dirnames in the tarball to locations
    on the disk from where the contents have to be retrieved.

    Home relative (~/...) file names are not supported by the transformation
    rules as they are converted by the shell before being passed to tar.
    """

    _, ext = os.path.splitext(localfile)

    with utils.tempfile(suffix=ext) as temp:
        cmd = [
            'tar',
            '--create',
            '--file={}'.format(temp),
            '--auto-compress',
            '-h',  # Follow symbolic links
            '--verbose',
            '--show-transformed-names',
        ]

        for destination, source in spec.iteritems():
            cmd.extend([
                '\\\n',
                '   {:30s}'.format(source),
                '--transform',
                quote('s!^{}!{}!'.format(source.lstrip('/'), destination)),
            ])

        run(' '.join(cmd))
        get(temp, localfile)
