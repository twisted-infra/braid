"""
Steps for translating PyPy.
"""

from buildbot.steps.shell import ShellCommand

class Translate(ShellCommand):
    name = "translate"
    description = ["Translating"]
    descriptionDone = ["Translation"]

    command = ["../../../pypy", "../../rpython/bin/rpython", "--batch"]
    translationTarget = "targetpypystandalone"
    haltOnFailure = False

    def __init__(self, translationArgs, targetArgs,
                 workdir="build/pypy/goal",
                 *a, **kw):
        self.command = self.command + translationArgs + [self.translationTarget] + targetArgs
        ShellCommand.__init__(self, workdir, *a, **kw)
