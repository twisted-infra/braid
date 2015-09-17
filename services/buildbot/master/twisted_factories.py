"""
Build classes specific to the Twisted codebase
"""

import os

from buildbot.process.properties import WithProperties
from buildbot.process.base import Build
from buildbot.process.factory import BuildFactory
from buildbot.steps import shell, transfer
from buildbot.steps.shell import ShellCommand

from twisted_steps import ProcessDocs, ReportPythonModuleVersions, \
    Trial, RemovePYCs, RemoveTrialTemp, LearnVersion, \
    SetBuildProperty

from txbuildbot.lint import (
    CheckDocumentation,
    CheckCodesByTwistedChecker,
    PyFlakes,
)

import private
reload(private)

TRIAL_FLAGS = ["--reporter=bwverbose"]
WARNING_FLAGS = ["--unclean-warnings"]
FORCEGC_FLAGS = ["--force-gc"]

# Dependencies that work on both CPython 2.7 + 3.3 + 3.4
BASE_DEPENDENCIES = [
    'cryptography<=0.9',
    'pyopenssl',
    'service_identity',
    'zope.interface',
    'idna',
    'pyasn1',
    'python-subunit',
]

# Dependencies that don't work on PyPy
CEXT_DEPENDENCIES = [
    'pycrypto',
]

# Dependencies that don't work on CPython 3.3+
EXTRA_DEPENDENCIES = [
    'soappy',
    'pyserial',
]

# Dependencies used for coverage testing
COVERAGE_DEPENDENCIES = [
    'coverage',
]

# Dependencies for building the documentation
DOC_DEPENDENCIES = [
    'sphinx',
    'pydoctor',
]



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


    def _reportVersions(self, python=None, virtualenv=False):
        # Report the module versions
        if python == None:
            python = self.python

        if virtualenv:
            stepAdder = self.addVirtualEnvStep
        else:
            stepAdder = self.addStep

        stepAdder(
            ReportPythonModuleVersions,
            python=python,
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


    def __init__(self, python, source, uncleanWarnings, trialTests=None,
                 trialMode=None, virtualenv=False,
                 forceGarbageCollection=False):
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
        self.forceGarbageCollection = forceGarbageCollection
        self.trialMode = trialMode
        if trialTests is None:
            trialTests = [WithProperties("%(test-case-name:~twisted)s")]
        self.trialTests = trialTests

        if virtualenv:
            # Each time we create a new virtualenv as latest pip can build
            # wheels on the fly and install them from user's cache.
            self.addStep(
                shell.ShellCommand,
                command = self.python + ["-m",
                    'virtualenv', '--clear',
                    self._virtualEnvPath,
                    ],
                )

        else:
            # Report the versions, since we're using the system ones. If it's a
            # virtualenv, it's up to the venv factory to report the versions
            # itself.
            self._reportVersions()


    def addTrialStep(self, virtualenv=False, **kw):
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
        if virtualenv:
            self.addVirtualEnvStep(TwistedTrial, trialMode=trialMode, **kw)
        else:
            self.addStep(TwistedTrial, trialMode=trialMode, **kw)


    @property
    def _virtualEnvBin(self):
        """
        Path to the virtualenv bin folder.
        """
        return os.path.join('..', 'venv', 'bin')


    @property
    def _virtualEnvPath(self):
        """
        Path to the root virtualenv folder.
        """
        return os.path.join('..', 'venv')


    def addVirtualEnvStep(self, step, **kwargs):
        """
        Add a step which is executed with virtualenv path.
        """
        # Update PATH environment so that the virtualenv is listed first.
        env = kwargs.get('env', {})
        path = env.get('PATH', '')
        env['PATH'] = os.pathsep.join([self._virtualEnvBin, path, '${PATH}'])
        kwargs['env'] = env
        self.addStep(step, **kwargs)



class TwistedDocumentationBuildFactory(TwistedBaseFactory):
    treeStableTimer = 5 * 60

    def __init__(self, source, python="python",
                 reactors=["select"], uncleanWarnings=True,
                 dependencies=BASE_DEPENDENCIES + CEXT_DEPENDENCIES + EXTRA_DEPENDENCIES + DOC_DEPENDENCIES):

        TwistedBaseFactory.__init__(
            self,
            source=source,
            python=python,
            uncleanWarnings=False,
            virtualenv=True,
        )

        self.addVirtualEnvStep(
            shell.ShellCommand,
            description = "installing dependencies".split(" "),
            command=['pip', 'install'] + dependencies
        )

        self.addVirtualEnvStep(CheckDocumentation)
        self.addVirtualEnvStep(ProcessDocs)
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



class Win32RemovePYCs(ShellCommand):
    name = "remove-.pyc"
    command = 'del /s *.pyc'
    description = ["removing", ".pyc", "files"]
    descriptionDone = ["remove", ".pycs"]



class TwistedReactorsBuildFactory(TwistedBaseFactory):
    treeStableTimer = 5*60

    def __init__(self, source, RemovePYCs=RemovePYCs,
                 python="python", reactors=["select"], uncleanWarnings=True):
        TwistedBaseFactory.__init__(self, python, source, uncleanWarnings)

        self.addVirtualEnvStep(shell.ShellCommand,
                               description="installing CExts".split(" "),
                               command=['pip', 'install', 'cexts/'],
                               warnOnFailure=True)

        for reactor in reactors:
            self.addStep(RemovePYCs)
            self.addStep(RemoveTrialTemp, python=self.python)
            self.addTrialStep(
                name=reactor, reactor=reactor, flunkOnFailure=True,
                warnOnFailure=False)



class TwistedVirtualenvReactorsBuildFactory(TwistedBaseFactory):
    treeStableTimer = 5*60

    def __init__(self, source, RemovePYCs=RemovePYCs, python="python",
                 trial="./bin/trial",
                 reactors=["select"], uncleanWarnings=False,
                 dependencies=BASE_DEPENDENCIES + CEXT_DEPENDENCIES + EXTRA_DEPENDENCIES,
                 forceGarbageCollection=False, tests=None):

        TwistedBaseFactory.__init__(
            self,
            source=source,
            python=python,
            uncleanWarnings=uncleanWarnings,
            virtualenv=True,
            forceGarbageCollection=forceGarbageCollection,
            trialTests=tests,
        )

        self.addVirtualEnvStep(
            shell.ShellCommand,
            description = "installing dependencies".split(" "),
            command=['pip', 'install'] + dependencies
        )

        self._reportVersions(virtualenv=True)

        self.addVirtualEnvStep(shell.ShellCommand,
                               description="installing CExts".split(" "),
                               command=['pip', 'install', 'cexts/'],
                               warnOnFailure=True)

        for reactor in reactors:
            self.addStep(RemovePYCs)
            self.addStep(RemoveTrialTemp, python=self.python)
            self.addTrialStep(
                name=reactor, reactor=reactor, flunkOnFailure=True,
                warnOnFailure=False, virtualenv=True, trial=trial)



class TwistedJythonReactorsBuildFactory(TwistedBaseFactory):
    treeStableTimer = 5*60

    def __init__(self, source, RemovePYCs=RemovePYCs, python="jython",
                 reactors=["select"], uncleanWarnings=True):

        TwistedBaseFactory.__init__(
            self,
            source=source,
            python=python,
            uncleanWarnings=False,
            virtualenv=False,
        )

        # Download and build Jython
        self.addStep(
            shell.ShellCommand,
            command=["rm", "-f", "master.tar.gz"]
        )
        self.addStep(
            shell.ShellCommand,
            command=["rm", "-rf", "jython-master"]
        )

        self.addStep(
            shell.ShellCommand,
            command=["wget", "https://github.com/jythontools/jython/archive/master.tar.gz"],
        )

        self.addStep(
            shell.ShellCommand,
            command=["tar", "-xvf", "master.tar.gz"]
        )

        self.addStep(
            shell.ShellCommand,
            warnOnFailure=True,
            command=["ant", "-file", "jython-master/build.xml"]
        )

        # Run it again... because
        self.addStep(
            shell.ShellCommand,
            warnOnFailure=True,
            command=["ant", "-file", "jython-master/build.xml"]
        )

        python = "jython-master/dist/bin/jython"

        self.addStep(
            shell.ShellCommand,
            command=["python", "-m", "virtualenv", "-p", python, self._virtualEnvPath]
        )


        self.addStep(
            shell.ShellCommand,
            description="Fixing permissions".split(" "),
            command=["chmod", "+x", "../venv/bin/pip"]
        )

        self.addVirtualEnvStep(
            shell.ShellCommand,
            description = "installing dependencies".split(" "),
            command=['pip', 'install', 'zope.interface']
        )

        venvPython = [os.path.join(self._virtualEnvBin, self.python[0])]

        self._reportVersions(python=venvPython)

        for reactor in reactors:
            self.addStep(RemovePYCs)
            self.addStep(RemoveTrialTemp, python=self.python)
            self.addTrialStep(
                name=reactor, reactor=reactor, flunkOnFailure=True,
                warnOnFailure=False, virtualenv=True)



class TwistedCextsWheelBuildFactory(TwistedBaseFactory):
    """
    Build the _twistedextensions package.
    """
    treeStableTimer = 5*60

    uploadBase = 'build_products/'
    def __init__(self, python, source, uncleanWarnings, arch, pyVersion):
        TwistedBaseFactory.__init__(self, python, source, uncleanWarnings)

        self.addStep(
            LearnVersion, python=python, package='twisted', workdir='Twisted')

        def transformVersion(build):
            return build.getProperty("version").split("+")[0].split("pre")[0]

        self.addStep(SetBuildProperty,
                     property_name="versionWhl",
                     value=transformVersion)

        wheelPythonVersion = 'cp' + pyVersion.replace('.','') + '-none-' + arch.replace('-','_')

        self.addStep(
            shell.ShellCommand,
            workdir="cexts",
            name='build-whl',
            description=['Build', 'wheel'],
            descriptionDone=['Built', 'wheel'],
            command=[python, "setup.py", "bdist_wheel"],
            haltOnFailure=True
        )

        self.addStep(
            transfer.FileUpload,
            name='upload-whl',
            slavesrc=WithProperties(
                'cexts/dist/_twistedextensions-%(versionWhl)s-' + wheelPythonVersion + '.whl'),
            masterdest=WithProperties(
                self.uploadBase + 'twisted-packages/_twistedextensions-%(version)s-'
                + wheelPythonVersion + '.whl'),
            url=WithProperties(
                '/build/twisted-packages/_twistedextensions-%(version)s-'
                + wheelPythonVersion + '.whl'),
        )



class TwistedCoveragePyFactory(TwistedBaseFactory):
    OMIT_PATHS = [
        '/usr/*',
        '_trial_temp/*',
        ]

    def __init__(self, python, source, buildID=None, trial="./bin/trial",
                 tests=None, dependencies=BASE_DEPENDENCIES + CEXT_DEPENDENCIES + EXTRA_DEPENDENCIES):
        OMIT = self.OMIT_PATHS[:]
        OMIT.append(self._virtualEnvPath + "/*")

        TwistedBaseFactory.__init__(
            self,
            source=source,
            python=python,
            uncleanWarnings=False,
            virtualenv=True,
            trialTests=tests,
        )
        self.addVirtualEnvStep(
            shell.ShellCommand,
            description="installing dependencies".split(" "),
            command=['pip', 'install'] + dependencies + COVERAGE_DEPENDENCIES
        )

        self._reportVersions(virtualenv=True)

        self.addVirtualEnvStep(shell.ShellCommand,
                               description="installing CExts".split(" "),
                               command=['pip', 'install', 'cexts/'],
                               warnOnFailure=True)

        self.addTrialStep(
            flunkOnFailure=True,
            python=[
                "coverage", "run",
                "--omit", ','.join(self.OMIT_PATHS),
                "--branch"],
            warnOnFailure=False, virtualenv=True, trial=trial)

        self.addVirtualEnvStep(
            shell.ShellCommand,
            description = "run coverage html".split(" "),
            command=["coverage", 'html', '-d', 'twisted-coverage',
                     '--omit', ','.join(OMIT), '-i']
        )

        self.addStep(
            transfer.DirectoryUpload,
            workdir='Twisted',
            slavesrc='twisted-coverage',
            masterdest=WithProperties('build_products/twisted-coverage.py/twisted-' + buildID + '-coverage.py-r%(got_revision)s'),
            url=WithProperties('/builds/twisted-coverage.py/twisted-' + buildID + '-coverage.py-r%(got_revision)s/'),
            blocksize=2 ** 16,
            compress='gz')



class TwistedBenchmarksFactory(TwistedBaseFactory):
    def __init__(self, python, source):
        TwistedBaseFactory.__init__(
            self,
            source=source,
            python=python,
            uncleanWarnings=False,
            virtualenv=True,
        )

        self.addStep(shell.ShellCommand,
                     command=["wget", "https://github.com/twisted-infra/twisted-benchmarks/archive/master.tar.gz",
                              "-O", "twisted-benchmarks.tar.gz"])
        self.addStep(shell.ShellCommand,
                     command=["rm", "-rf", "twisted-benchmarks/"])
        self.addStep(shell.ShellCommand,
                     command=["mkdir", "-p", "twisted-benchmarks/"])
        self.addStep(shell.ShellCommand,
                     command=["tar", "xvf", "twisted-benchmarks.tar.gz",
                              "--strip-components=1", "--directory=twisted-benchmarks/"])

        self.addVirtualEnvStep(
            shell.ShellCommand,
            description = "installing dependencies".split(" "),
            command=['pip', 'install'] + BASE_DEPENDENCIES + ["requests"])

        self._reportVersions(virtualenv=True)

        self.addVirtualEnvStep(
            shell.ShellCommand,
            env={'PYTHONPATH': '.'},
            command=self.python + [
                "twisted-benchmarks/speedcenter.py",
                "--duration", "1", "--iterations", "30", "--warmup", "5",
                "--url", "http://speed.twistedmatrix.com/result/add/json/"])



class TwistedCheckerBuildFactory(TwistedBaseFactory):
    """
    Run twistedchecker check from an virtualenv.
    """

    def __init__(self, source, python="python2.7"):
        TwistedBaseFactory.__init__(
            self,
            source=source,
            python=python,
            uncleanWarnings=False,
            virtualenv=True,
        )
        self.addVirtualEnvStep(
            shell.ShellCommand,
            command=['pip', 'install', 'twistedchecker==0.4.0'])
        self.addVirtualEnvStep(CheckCodesByTwistedChecker, want_stderr=False)



class PyFlakesBuildFactory(TwistedBaseFactory):
    """
    A build factory which just runs PyFlakes over the specified source.
    """

    def __init__(self, source, python="python"):
        TwistedBaseFactory.__init__(
            self,
            source=source,
            python=python,
            uncleanWarnings=False,
            virtualenv=True,
        )
        self.addVirtualEnvStep(
            shell.ShellCommand,
            command=['pip', 'install', 'pyflakes'])
        self.addVirtualEnvStep(PyFlakes)
