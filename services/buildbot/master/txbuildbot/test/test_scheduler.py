from twisted.trial import unittest

from txbuildbot.scheduler import TwistedScheduler
from buildbot.test.util.scheduler import SchedulerMixin

class TestTwistedScheduler(unittest.TestCase, SchedulerMixin):

    OBJECTID = 99

    def makeScheduler(self, name='testsched', builderNames=['test_builder']):
        return self.attachScheduler(TwistedScheduler(name=name, builderNames=builderNames, branch='trunk'), self.OBJECTID)

    def test_fileIsImportant(self):
        sched = self.makeScheduler()
        self.failIf(sched.fileIsImportant(self.makeFakeChange(files=['doc/fun/Twisted.Quotes'])))
        self.failIf(sched.fileIsImportant(self.makeFakeChange(files=['doc/fun/lightbulb'])))
        self.failUnless(sched.fileIsImportant(self.makeFakeChange(files=['doc/fun/Twisted.Quotes', 'setup.py'])))
        self.failUnless(sched.fileIsImportant(self.makeFakeChange(files=['twisted/__init__.py', 'setup.py'])))
