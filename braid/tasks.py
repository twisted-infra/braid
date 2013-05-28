from __future__ import absolute_import

from fabric.api import task, roles
from twisted.python.reflect import prefixedMethods


TASK_PREFIX = 'task_'


def _stripPrefix(f):
    """
    Get the unprefixed name of C{f}.
    """
    return f.__name__[len(TASK_PREFIX):]


class Service(object):

    def getTasks(self, role=None):
        """
        Get all tasks of this L{Service} object.

        Intended to be used like::

            globals().update(Service('name').getTasks())

        at the module level of a fabfile.

        @returns: L{dict} of L{fabric.tasks.Task}
        """
        tasks = prefixedMethods(self, TASK_PREFIX)
        tasks = ((_stripPrefix(t), t) for t in tasks)
        tasks = ((name, task(name=name)(t)) for name, t in tasks)

        if role:
            tasks = ((name, roles(role)(t)) for name, t in tasks)

        return dict(tasks)


def addTasks(globals, tasks):
    globals.update(tasks)
    globals['__all__'].extend(tasks.keys())
