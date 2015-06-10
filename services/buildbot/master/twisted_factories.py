"""
Build classes specific to the Twisted codebase
"""

from buildbot.process.properties import WithProperties
from buildbot.process.base import Build
from buildbot.process.factory import BuildFactory
from buildbot.steps import shell, transfer
from buildbot.steps.shell import ShellCommand
from buildbot.steps.source import Mercurial, Git
from txbuildbot.pypy import Translate

from twisted_steps import ProcessDocs, ReportPythonModuleVersions, \
    Trial, RemovePYCs, RemoveTrialTemp, LearnVersion, \
    SetBuildProperty

from txbuildbot.lint import (
        CheckDocumentation,
        CheckCodesByTwistedChecker,
        PyFlakes,
        )

TRIAL_FLAGS = ["--reporter=bwverbose"]
WARNING_FLAGS = ["--unclean-warnings"]
FORCEGC_FLAGS = ["--force-gc"]

class TwistedBuild(Build):
    workdir = "Twisted" # twisted's bin/trial expects to live in here

### WARNING (for buildbot-0.8.6)
### We use the build step factory repreentation deperecated in 0.8.6 here.
### Some of the steps in twisted_steps break otherwise, but will
### work fine with the factory support introduced in 0.8.7. Rather than
### change the steps, we will just ignore the warnings for now.

class TwistedTrial(Trial):
    tests = "twisted"
    # the Trial in Twisted >=2.1.0 has --recurse on by default, and -to
    # turned into --reporter=bwverbose .
    recurse = False
    trialMode = TRIAL_FLAGS
    testpath = None
    trial = "./bin/trial"

class TwistedBaseFactory(BuildFactory):
    """
    @ivar python: The path to the Python executable to use.  This is a
        list, to allow additional arguments to be passed.
    """
    buildClass = TwistedBuild
    # bin/trial expects its parent directory to be named "Twisted": it uses
    # this to add the local tree to PYTHONPATH during tests
    workdir = "Twisted"

    forceGarbageCollection = False

    def _fixPermissions(self, source):
        # Hack for Windows
        haveChmod = transfer.FileDownload(
            mastersrc="dependencies/chmod.bat",
            slavedest="chmod.bat",
            workdir=".")
        source.insert(0, haveChmod)
        # Fix any nasty permissions left over from last time that
        # might cause the cleanup to fail.
        fixPermissions = ShellCommand(
            workdir=".", command=["chmod", "u+rwX", "-f", "-R", "Twisted"])
        source.insert(0, fixPermissions)


    def __init__(self, python, source, uncleanWarnings, trialTests=None, trialMode=None):
        if not isinstance(source, list):
            source = [source]
        else:
            source = list(source)

        # If permissions get messed up on a slave, this can fix it.
        # But it breaks on old slaves so it's not enabled all the time
        # (and it can't fix old slaves, obviously).

        # self._fixPermissions(source)

        BuildFactory.__init__(self, source)

        if type(python) is str:
            python = [python]

        self.python = python
        self.uncleanWarnings = uncleanWarnings
        self.trialMode = trialMode
        if trialTests is None:
            trialTests = [WithProperties("%(test-case-name:~twisted)s")]
        self.trialTests = trialTests

        self.addStep(
            ReportPythonModuleVersions,
            python=self.python,
            moduleInfo=[
                ("Python", "sys", "sys.version"),
                ("OpenSSL", "OpenSSL", "OpenSSL.__version__"),
                ("PyCrypto", "Crypto", "Crypto.__version__"),
                ("gmpy", "gmpy", "gmpy.version()"),
                ("SOAPpy", "SOAPpy", "SOAPpy.__version__"),
                ("ctypes", "ctypes", "ctypes.__version__"),
                ("gtk", "gtk", "gtk.gtk_version"),
                ("pygtk", "gtk", "gtk.pygtk_version"),
                ("pywin32", "win32api",
                 "win32api.GetFileVersionInfo(win32api.__file__, chr(92))['FileVersionLS'] >> 16"),
                ("pyasn1", "pyasn1", "pyasn1.__version__"),
                ("cffi", "cffi", "cffi.__version__"),
                ],
            pkg_resources=[
                ("subunit", "subunit"),
                ("zope.interface", "zope.interface"),
                ])


    def addTrialStep(self, **kw):
        if self.trialMode is not None:
            trialMode = self.trialMode
        else:
            trialMode = TRIAL_FLAGS

        if self.uncleanWarnings:
            trialMode = trialMode + WARNING_FLAGS
        if self.forceGarbageCollection:
            trialMode = trialMode + FORCEGC_FLAGS
        if 'tests' not in kw:
            kw['tests'] = self.trialTests
        if 'python' not in kw:
            kw['python'] = self.python
        self.addStep(TwistedTrial, trialMode=trialMode, **kw)



class TwistedDocumentationBuildFactory(TwistedBaseFactory):
    treeStableTimer = 5 * 60

    def __init__(self, source, python="python"):
        TwistedBaseFactory.__init__(self, python, source, False)

        # Build our extensions, in case any API documentation wants to link to
        # them.
        self.addStep(
            shell.Compile,
            command=[python, "setup.py", "build_ext", "-i"])

        self.addStep(CheckDocumentation)
        self.addStep(ProcessDocs)
        self.addStep(
            shell.ShellCommand,
            name="bundle-docs",
            description=["bundling", "docs"],
            descriptionDone=["bundle", "docs"],
            command=['/bin/tar', 'cjf', 'doc.tar.bz2', 'doc'])
        self.addStep(
            shell.ShellCommand,
            name="bundle-apidocs",
            description=["bundling", "apidocs"],
            descriptionDone=["bundle", "apidocs"],
            command=['/bin/tar', 'cjf', 'apidocs.tar.bz2', 'apidocs'])
        self.addStep(
            transfer.FileUpload,
            name='upload-apidocs',
            workdir='.',
            slavesrc='./Twisted/apidocs.tar.bz2',
            masterdest=WithProperties(
                'build_products/apidocs/apidocs-%(got_revision)s.tar.bz2'),
            url=WithProperties(
                '/builds/apidocs/apidocs-%(got_revision)s.tar.bz2'))
        self.addStep(
            transfer.FileUpload,
            name='upload-docs',
            workdir='.',
            slavesrc='./Twisted/doc.tar.bz2',
            masterdest=WithProperties(
                'build_products/docs/doc-%(got_revision)s.tar.bz2'),
            url=WithProperties(
                '/builds/docs/doc-%(got_revision)s.tar.bz2'))



class FullTwistedBuildFactory(TwistedBaseFactory):
    treeStableTimer = 5*60

    def __init__(self, source, python="python",
                 runTestsRandomly=False,
                 compileOpts=[], compileOpts2=[],
                 uncleanWarnings=True, trialMode=None,
                 trialTests=None, buildExtensions=True):
        TwistedBaseFactory.__init__(self, python, source, uncleanWarnings, trialTests=trialTests, trialMode=trialMode)

        assert isinstance(compileOpts, list)
        assert isinstance(compileOpts2, list)

        if buildExtensions:
            cmd = (python + compileOpts + ["setup.py", "build_ext"]
                   + compileOpts2 + ["-i"])
            self.addStep(shell.Compile, command=cmd, flunkOnFailure=True)

        self.addStep(RemovePYCs)
        self.addTrialStep(randomly=runTestsRandomly)


class Win32RemovePYCs(ShellCommand):
    name = "remove-.pyc"
    command = 'del /s *.pyc'
    description = ["removing", ".pyc", "files"]
    descriptionDone = ["remove", ".pycs"]


class GoodTwistedBuildFactory(TwistedBaseFactory):
    treeStableTimer = 5 * 60

    def __init__(self, source, python="python",
                 processDocs=False, runTestsRandomly=False,
                 compileOpts=[], compileOpts2=[],
                 uncleanWarnings=True,
                 extraTrialArguments={},
                 forceGarbageCollection=False):
        TwistedBaseFactory.__init__(self, python, source, uncleanWarnings)
        self.forceGarbageCollection = forceGarbageCollection
        if processDocs:
            self.addStep(ProcessDocs)

        assert isinstance(compileOpts, list)
        assert isinstance(compileOpts2, list)
        cmd = (self.python + compileOpts + ["setup.py", "build_ext"]
               + compileOpts2 + ["-i"])

        self.addStep(shell.Compile, command=cmd, flunkOnFailure=True)
        self.addStep(RemovePYCs)
        self.addTrialStep(randomly=runTestsRandomly, **extraTrialArguments)


class TwistedReactorsBuildFactory(TwistedBaseFactory):
    treeStableTimer = 5*60

    def __init__(self, source, RemovePYCs=RemovePYCs,
                 python="python", compileOpts=[], compileOpts2=[],
                 reactors=["select"], uncleanWarnings=True):
        TwistedBaseFactory.__init__(self, python, source, uncleanWarnings)

        assert isinstance(compileOpts, list)
        assert isinstance(compileOpts2, list)
        cmd = (self.python + compileOpts + ["setup.py", "build_ext"]
               + compileOpts2 + ["-i"])

        self.addStep(shell.Compile, command=cmd, warnOnFailure=True)

        for reactor in reactors:
            self.addStep(RemovePYCs)
            self.addStep(RemoveTrialTemp, python=self.python)
            self.addTrialStep(
                name=reactor, reactor=reactor, flunkOnFailure=True,
                warnOnFailure=False)



class TwistedBdistMsiFactory(TwistedBaseFactory):
    treeStableTimer = 5*60

    uploadBase = 'build_products/'
    def __init__(self, source, uncleanWarnings, arch, pyVersion):
        python = self.python(pyVersion)
        TwistedBaseFactory.__init__(self, python, source, uncleanWarnings)
        self.addStep(
            LearnVersion, python=python, package='twisted', workdir='Twisted')

        def transformVersion(build):
            return build.getProperty("version").split("+")[0].split("pre")[0]
        self.addStep(SetBuildProperty,
            property_name='versionMsi', value=transformVersion)
        self.addStep(shell.ShellCommand,
                name='write-copyright-file',
                description=['Update', 'twisted/copyright.py'],
                descriptionDone=['Updated', 'twisted/copyright.py'],
                command=[python, "-c", WithProperties(
                     'version = \'%(versionMsi)s\'; '
                     'f = file(\'twisted\copyright.py\', \'at\'); '
                     'f.write(\'version = \' + repr(version)); '
                     'f.close()')],
                     haltOnFailure=True)

        self.addStep(shell.ShellCommand,
                     name='build-msi',
                     description=['Build', 'msi'],
                     descriptionDone=['Built', 'msi'],
                     command=[python, "setup.py", "bdist_msi"],
                     haltOnFailure=True)
        self.addStep(
            transfer.FileUpload,
            name='upload-msi',
            slavesrc=WithProperties('dist/Twisted-%(versionMsi)s.' + arch + '-py' + pyVersion + '.msi'),
            masterdest=WithProperties(
                self.uploadBase + 'twisted-packages/Twisted-%%(version)s.%s-py%s.msi' % (arch, pyVersion)),
            url=WithProperties(
                '/build/twisted-packages/Twisted-%%(version)s.%s-py%s.msi' % (arch, pyVersion)))

        self.addStep(shell.ShellCommand,
                name='build-exe',
                description=['Build', 'exe'],
                descriptionDone=['Built', 'exe'],
                command=[python, "setup.py", "bdist_wininst"],
                haltOnFailure=True)
        self.addStep(
            transfer.FileUpload,
            name='upload-exe',
            slavesrc=WithProperties('dist/Twisted-%(versionMsi)s.' + arch + '-py' + pyVersion + '.exe'),
            masterdest=WithProperties(
                self.uploadBase + 'twisted-packages/Twisted-%%(version)s.%s-py%s.exe' % (arch, pyVersion)),
            url=WithProperties(
                '/build/twisted-packages/Twisted-%%(version)s.%s-py%s.exe' % (arch, pyVersion)))

        wheelPythonVersion = 'cp' + pyVersion.replace('.','') + '-none-' + arch.replace('-','_')
        self.addStep(shell.ShellCommand,
                name='build-whl',
                description=['Build', 'wheel'],
                descriptionDone=['Built', 'wheel'],
                command=[python, "setup.py", "--command-package", "wheel", "bdist_wheel"],
                haltOnFailure=True)
        self.addStep(
            transfer.FileUpload,
            name='upload-whl',
            slavesrc=WithProperties('dist/Twisted-%(versionMsi)s-' + wheelPythonVersion + '.whl'),
            masterdest=WithProperties(
                self.uploadBase + 'twisted-packages/Twisted-%(version)s-'
                + wheelPythonVersion + '.whl'),
            url=WithProperties(
                '/build/twisted-packages/Twisted-%(version)s-'
                + wheelPythonVersion + '.whl'),
            )

    def python(self, pyVersion):
        return (
            "c:\\python%s\\python.exe" % (
                pyVersion.replace('.', ''),))


class InterpreterBuilderMixin:

    # Prefix in which to install modules
    modulePrefix = '../install'

    def buildModule(self, python, basename):
        self.addStep(
            ShellCommand,
            name="extract-"+basename,
            description=["extracting", basename],
            descriptionDone=["extract", basename],
            # Can't make workdir build, .. won't resolve properly
            # because build is a symlink.
            workdir=".",
            command=["/bin/tar", "Cxzf", "build", basename + ".tar.gz"])
        self.addStep(
            ShellCommand,
            name="install-"+basename,
            description=["installing", basename],
            descriptionDone=["install", basename],
            workdir="build/" + basename,
            command=[python, "setup.py", "clean", "install", "--prefix", self.modulePrefix])


    def buildModules(self, python, projects):
        python = "../" + python

        for basename in projects:
            # Send the tarball down
            self.addStep(
                transfer.FileDownload,
                name="download-" + basename,
                mastersrc="dependencies/" + basename + ".tar.gz",
                slavedest=basename + ".tar.gz",
                workdir=".")

            if "subunit" in basename:
                # Always trying to be special.
                self.buildSubunit(python, basename)
            else:
                self.buildModule(python, basename)

    def buildSubunit(self, python, dirname):
        basename = dirname + '.tar.gz'
        self.addStep(
            ShellCommand,
            name="extract-"+dirname,
            description=["extracting", dirname],
            descriptionDone=["extract", dirname],
            workdir=".",
            command=["/bin/tar", "Cxzf", "build", basename])
        self.addStep(
            ShellCommand,
            name="configure-"+dirname,
            description=["configuring", dirname],
            descriptionDone=["configure", dirname],
            workdir="build/" + dirname,
            env={"PYTHON": python},
            command="./configure --prefix=${PWD}/" + self.modulePrefix)
        self.addStep(
            ShellCommand,
            name="install-"+basename,
            description=["installing", basename],
            descriptionDone=["install", basename],
            workdir="build/" + dirname,
            command=["make", "install"])



class CPythonBuildFactory(BuildFactory, InterpreterBuilderMixin):
    def __init__(self, branch, python, projects, *a, **kw):
        BuildFactory.__init__(self, *a, **kw)
        self.addStep(
            Mercurial,
            repourl="http://hg.python.org/cpython",
            defaultBranch=branch,
            branchType='inrepo',
            mode="copy")
        self.addStep(
            ShellCommand,
            name="configure-python",
            description=["configuring", "python"],
            descriptionDone=["configure", "python"],
            command="./configure --prefix=$PWD/install")
        self.addStep(
            ShellCommand,
            name="install-python",
            description=["installing", "python"],
            descriptionDone=["install", "python"],
            command=["make", "install"])
        pythonc = "install/bin/" + python
        self.addStep(
            ShellCommand,
            name="link-binary",
            description=["linking", "binary"],
            descriptionDone=["link", "binary"],
            command=["ln", "-nsf", "build/" + pythonc, "python"],
            workdir=".")
        self.buildModules(pythonc, projects)



class PyPyTranslationFactory(BuildFactory, InterpreterBuilderMixin):
    modulePrefix = '../'
    def __init__(self, translationArguments, targetArguments, projects, *a, **kw):
        BuildFactory.__init__(self, *a, **kw)
        self.addStep(
            Mercurial,
            repourl="https://bitbucket.org/pypy/pypy")
        self.addStep(
            Translate,
            translationArgs=translationArguments,
            targetArgs=targetArguments)
        self.addStep(
            ShellCommand,
            name="link-binary",
            description=["linking", "binary"],
            descriptionDone=["link", "binary"],
            command=["ln", "-nsf", "build/pypy/goal/pypy-c", "."],
            workdir=".")

        # Don't try building these yet.  PyPy doesn't quite work well
        # enough.
        pypyc = "pypy/goal/pypy-c"
        self.buildModules(pypyc, projects)



class TwistedIronPythonBuildFactory(FullTwistedBuildFactory):
    def __init__(self, source, *a, **kw):
        FullTwistedBuildFactory.__init__(
            self, source, ["ipy"], buildExtensions=False, *a, **kw)



class TwistedCoveragePyFactory(TwistedBaseFactory):
    OMIT_PATHS = [
        '/usr/*',
        '_trial_temp/*',
        ]

    REPORT_COMMAND = [
        'coverage', 'html', '-d', 'twisted-coverage',
        '--omit', ','.join(OMIT_PATHS), '-i']

    def __init__(self, python, source):
        TwistedBaseFactory.__init__(self, python, source, False)
        self.addStep(
            shell.Compile,
            command=python + ["setup.py", "build_ext", "-i"],
            flunkOnFailure=True)
        self.addTrialStep(python=[
                "coverage", "run",
                "--omit", ','.join(self.OMIT_PATHS),
                "--branch"])
        self.addStep(
            shell.ShellCommand,
            command=self.REPORT_COMMAND)
        self.addStep(
            transfer.DirectoryUpload,
            workdir='Twisted',
            slavesrc='twisted-coverage',
            masterdest=WithProperties('build_products/twisted-coverage.py/twisted-coverage.py-r%(got_revision)s'),
            url=WithProperties('/builds/twisted-coverage.py/twisted-coverage.py-r%(got_revision)s/'),
            blocksize=2 ** 16,
            compress='gz')


class TwistedPython3CoveragePyFactory(TwistedBaseFactory):
    OMIT_PATHS = [
        '/usr/*',
        '*/tw-py3-*/*',
        ]

    def __init__(self, python, source):
        TwistedBaseFactory.__init__(self, python, source, False)
        self.addStep(
            shell.ShellCommand,
            command = self.python + [
                "-m", "coverage", "run", "--omit", ','.join(self.OMIT_PATHS),
                "--branch", "admin/run-python3-tests"])
        self.addStep(
            shell.ShellCommand,
            command=self.python + [
                "-m", "coverage", 'html', '-d', 'twisted-coverage', '--omit',
                ','.join(self.OMIT_PATHS), '-i'])
        self.addStep(
            transfer.DirectoryUpload,
            workdir='Twisted',
            slavesrc='twisted-coverage',
            masterdest=WithProperties('build_products/twisted-coverage.py/twisted-py3-coverage.py-r%(got_revision)s'),
            url=WithProperties('/builds/twisted-coverage.py/twisted-py3-coverage.py-r%(got_revision)s/'),
            blocksize=2 ** 16,
            compress='gz')


class TwistedBenchmarksFactory(TwistedBaseFactory):
    def __init__(self, python, source):
        TwistedBaseFactory.__init__(self, python, source, False)

        self.addStep(
            shell.ShellCommand,
            env={'PYTHONPATH': '.'},
            command=self.python + [
                "../../../twisted-benchmarks/speedcenter.py",
                "--duration", "1", "--iterations", "60",
                "--url", "http://speed.twistedmatrix.com/result/add/"])

class TwistedPython3Tests(TwistedBaseFactory):
    def __init__(self, python, source):
        TwistedBaseFactory.__init__(self, python, source, False)
        self.addStep(RemovePYCs)
        self.addStep(
            shell.ShellCommand,
            command=self.python + ["admin/run-python3-tests"])

class TwistedCheckerBuildFactory(TwistedBaseFactory):
    def __init__(self, source, python="python"):
        # Add twistedchecker Git step first, so got_revision is twisted's
        source = [
            Git(
                repourl="https://github.com/twisted/twistedchecker",
                branch="master",
                alwaysUseLatest=True,
                mode="update",
                workdir="twistedchecker",
            )
        ] + source
        TwistedBaseFactory.__init__(self, python, source, False)

        self.addStep(CheckCodesByTwistedChecker,
                     want_stderr=False,
                     env={"PATH": ["../twistedchecker/bin","${PATH}"],
                          "PYTHONPATH": ["../twistedchecker","${PYTHONPATH}"]})

class PyFlakesBuildFactory(TwistedBaseFactory):
    """
    A build factory which just runs PyFlakes over the specified source.
    """

    def __init__(self, source, python="python"):
        TwistedBaseFactory.__init__(self, python, source, False)

        self.addStep(PyFlakes)
