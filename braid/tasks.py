from __future__ import absolute_import

from fabric.api import task
from twisted.python.reflect import prefixedMethods


TASK_PREFIX = 'task_'


def _stripPrefix(f):
    """
    Get the unprefixed name of C{f}.
    """
    return f.__name__[len(TASK_PREFIX):]

class Service(object):

    def getTasks(self):
        """
        Get all tasks of this L{Service} object.

        Intended to be used like::

            globals().update(Service('name').getTasks())

        at the module level of a fabfile.

        @returns: L{dict} of L{fabric.tasks.Task}
        """
        tasks = [(t, _stripPrefix(t))
                 for t in prefixedMethods(self, TASK_PREFIX)]
        return {name: task(name=name)(t) for t, name in tasks}

def addTasks(globals, tasks):
    globals.update(tasks)
    globals['__all__'].extend(tasks.keys())
