"""
Reimport of fabric.api.

Provides some useful wrappers of stuff.
"""
from fabric.api import *
from fabric import api as _api

from braid import info as _info

def sudo(*args, **kwargs):
    """
    Only calls sudo if not already root.

    FIXME: Should handle the case where the desired user isn't root.
    """
    func = _api.run if _info.isRoot() else _api.sudo
    func(*args, **kwargs)
