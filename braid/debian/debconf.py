from cStringIO import StringIO
from fabric.api import sudo
from braid.utils import tempfile

def setDebconfValue(package, question, type, value):
    selections = StringIO(' '.join([package, question, type, value]))
    with tempfile(selections) as controlFile:
        sudo('/usr/bin/debconf-set-selections {}'.format(controlFile))
