import mock
from twisted.trial.unittest import TestCase
from buildbot.test.util import sourcesteps
from buildbot.steps.source.git import Git
from buildbot.status.results import SUCCESS
from buildbot.test.fake.remotecommand import ExpectShell

from txbuildbot.git import (
        TwistedGit, MergeForward,
        mungeBranch, isTrunk, isRelease)

class TestTwistedGit(sourcesteps.SourceStepMixin, TestCase):
    """
    Tests for L{TwistedGit}.
    """

    def setUp(self):
        return self.setUpSourceStep()

    def tearDown(self):
        return self.tearDownSourceStep()

    def assertStartVCMunges(self, providedBranch, expectedBranch):
        def startVC_sideeffect(step, branch, revision, patch):
            self.assertEqual(branch, expectedBranch)
            step.finish(SUCCESS)
        git_startVC = mock.Mock(spec=Git.startVC, side_effect=startVC_sideeffect)
        self.patch(Git, 'startVC', git_startVC)
        self.setupStep(TwistedGit(repourl='git://twisted', branch='trunk'),
                       {'branch': providedBranch})
        self.expectOutcome(result=SUCCESS, status_text=['update'])
        return self.runStep()

    def test_startVC_mungeTrunk(self):
        return self.assertStartVCMunges('trunk', 'trunk')

    def test_startVC_mungesBranch(self):
        return self.assertStartVCMunges('/branches/test-branch-1234', 'test-branch-1234')

    def test_startVC_mungesBranch_withoutSlash(self):
        return self.assertStartVCMunges('branches/test-branch-1234', 'test-branch-1234')

    def test_startVCUsesGitRevision(self):
        """
        TwistedGit.startVC honors the "git_revision" property of the Change
        object to know which git revision to use when performing a post-commit
        build.
        """
        class FakeBuild(object):
            def getSourceStamp(self, id):
                return FakeSourceStamp()

        class FakeChange(object):
            properties = {"git_revision": "abcdef"}

        class FakeSourceStamp(object):
            changes = [FakeChange()]

        def startVC_replacement(step, branch, revision, patch):
            gitStartVC.append((step, branch, revision, patch))        

        self.patch(Git, 'startVC', startVC_replacement)
        tgit = TwistedGit(repourl='git://twisted', branch="")
        tgit.build = FakeBuild()
        gitStartVC = []
        tgit.startVC("", 195, "")

        self.assertEqual(gitStartVC[0][2], "abcdef")


class TestMergeForward(sourcesteps.SourceStepMixin, TestCase):
    """
    Tests for L{MergeForward}.
    """

    env = {
        'GIT_AUTHOR_EMAIL': 'buildbot@twistedmatrix.com',
        'GIT_AUTHOR_NAME': 'Twisted Buildbot',
        'GIT_COMMITTER_EMAIL': 'buildbot@twistedmatrix.com',
        'GIT_COMMITTER_NAME': 'Twisted Buildbot',
    }


    def setUp(self):
        return self.setUpSourceStep()

    def tearDown(self):
        return self.tearDownSourceStep()


    def buildStep(self, branch):
        self.setupStep(MergeForward(repourl='git://twisted'),
                       {'branch': branch})

    def test_trunk(self):
        self.buildStep('trunk')
        self.expectCommands(
                ExpectShell(workdir='wkdir',
                            command=['git', 'rev-parse', 'HEAD~1'],
                            env=self.env)
                + ExpectShell.log('stdio', stdout="deadbeef00000000000000000000000000000000\n")
                + 0
        )
        self.expectOutcome(result=SUCCESS, status_text=['merge', 'forward'])
        self.expectProperty('lint_revision', 'deadbeef00000000000000000000000000000000')
        return self.runStep()


    def test_branch(self):
        self.buildStep('destroy-the-sun-5000')
        self.expectCommands(
                ExpectShell(workdir='wkdir',
                            command=['git', 'fetch',
                                'git://twisted', 'trunk'],
                            env=self.env)
                + 0,
                ExpectShell(workdir='wkdir',
                            command=['git', 'merge',
                                '--no-ff', '--no-stat',
                                'FETCH_HEAD'],
                            env=self.env)
                + 0,
                ExpectShell(workdir='wkdir',
                            command=['git', 'merge-base', 'HEAD', 'FETCH_HEAD'],
                            env=self.env)
                + ExpectShell.log('stdio', stdout="deadbeef00000000000000000000000000000000\n")
                + 0
        )
        self.expectOutcome(result=SUCCESS, status_text=['merge', 'forward'])
        self.expectProperty('lint_revision', 'deadbeef00000000000000000000000000000000')
        return self.runStep()


    def test_releaseBranch(self):
        self.buildStep('releases/release-23.2-12345')
        self.expectCommands(
                ExpectShell(workdir='wkdir',
                            command=['git', 'fetch',
                                'git://twisted', 'trunk'],
                            env=self.env)
                + 0,
                ExpectShell(workdir='wkdir',
                            command=['git', 'merge-base', 'HEAD', 'FETCH_HEAD'],
                            env=self.env)
                + ExpectShell.log('stdio', stdout="deadbeef00000000000000000000000000000000\n")
                + 0
        )
        self.expectOutcome(result=SUCCESS, status_text=['merge', 'forward'])
        self.expectProperty('lint_revision', 'deadbeef00000000000000000000000000000000')
        return self.runStep()


class UtilsTestCase(TestCase):
    """
    Tests for branch-name inspecting functions.
    """

    def test_mungeBranch(self):
        self.assertEqual(mungeBranch('trunk'),
                         'trunk')
        self.assertEqual(mungeBranch('/trunk'),
                         'trunk')
        self.assertEqual(mungeBranch(''),
                         'trunk')
        self.assertEqual(mungeBranch('/branches/destroy-the-sun-5000'),
                         'destroy-the-sun-5000')
        self.assertEqual(mungeBranch('branches/destroy-the-sun-5000'),
                         'destroy-the-sun-5000')
        self.assertEqual(mungeBranch('destroy-the-sun-5000'),
                         'destroy-the-sun-5000')
        self.assertEqual(mungeBranch('/branches/releases/release-23.2-12345'),
                         'releases/release-23.2-12345')
        self.assertEqual(mungeBranch('branches/releases/release-23.2-12345'),
                         'releases/release-23.2-12345')
        self.assertEqual(mungeBranch('releases/release-23.2-12345'),
                         'releases/release-23.2-12345')


    def test_isTrunk(self):
        self.assertTrue(isTrunk('trunk'))
        self.assertTrue(isTrunk('/trunk'))
        self.assertTrue(isTrunk(''))
        self.assertFalse(isTrunk('/branches/destroy-the-sun-5000'))
        self.assertFalse(isTrunk('branches/destroy-the-sun-5000'))
        self.assertFalse(isTrunk('destroy-the-sun-5000'))
        self.assertFalse(isTrunk('/branches/releases/release-23.2-12345'))
        self.assertFalse(isTrunk('branches/releases/release-23.2-12345'))
        self.assertFalse(isTrunk('releases/release-23.2-12345'))

    def test_isRelease(self):
        self.assertFalse(isRelease('trunk'))
        self.assertFalse(isRelease('/trunk'))
        self.assertFalse(isRelease(''))
        self.assertFalse(isRelease('/branches/destroy-the-sun-5000'))
        self.assertFalse(isRelease('branches/destroy-the-sun-5000'))
        self.assertFalse(isRelease('destroy-the-sun-5000'))
        self.assertTrue(isRelease('/branches/releases/release-23.2-12345'))
        self.assertTrue(isRelease('branches/releases/release-23.2-12345'))
        self.assertTrue(isRelease('releases/release-23.2-12345'))
