# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

from __future__ import absolute_import, division

from StringIO import StringIO

def filterTox(logText, commandNumber=0):
    """
    Filter out the tox output for lint tox envs -- where there's only one
    command.
    """
    toxStatus = 'STARTED'

    for line in StringIO(logText):

        if "ERROR: InvocationError:" in line:
            # Tox is finished
            toxStatus = 'FINISHED'

        elif '___ summary ___' in line:
            toxStatus = 'FINISHED'

        elif toxStatus == 'STARTED':
            yield line.strip("\n")
