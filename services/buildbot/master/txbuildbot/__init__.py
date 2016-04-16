# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

from __future__ import absolute_import, division

from StringIO import StringIO

def filterTox(logText, commandNumber=0):
    """
    Filter out the tox output for lint tox envs -- where there's only one
    command.
    """
    toxStatus = 'NOT_STARTED'

    for line in StringIO(logText):

        if " runtests: commands[" + str(commandNumber) + "] | " in line:
            # Tox has started, further lines should be read
            toxStatus = 'STARTED'

        elif " runtests: commands[" + str(commandNumber + 1) + "] | " in line:
            # The next command is running
            toxStatus = 'FINISHED'

        elif "ERROR: InvocationError:" in line:
            # Tox is finished
            toxStatus = 'FINISHED'

        elif '___ summary ___' in line:
            toxStatus = 'FINISHED'

        elif toxStatus == 'STARTED':
            yield line.strip("\n")
