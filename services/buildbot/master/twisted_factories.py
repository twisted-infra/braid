"""
Build classes specific to the Twisted codebase
"""

import posixpath, ntpath

from buildbot.process.properties import WithProperties
from buildbot.process.base import Build
from buildbot.process.factory import BuildFactory
from buildbot.steps import shell, transfer
from buildbot.steps.shell import ShellCommand

from twisted_steps import ProcessDocs, ReportPythonModuleVersions, \
    Trial, RemovePYCs, RemoveTrialTemp, LearnVersion, \
    SetBuildProperty, TrialTox

from txbuildbot.lint import CheckDocumentation

import private
reload(private)

TRIAL_FLAGS = ["--reporter=bwverbose"]
WARNING_FLAGS = ["--unclean-warnings"]
FORCEGC_FLAGS = ["--force-gc"]

# Dependencies that work on both CPython 2.7 + 3.3 + 3.4
BASE_DEPENDENCIES = [
    'tox',
    'pyopenssl',
    'service_identity',
    'zope.interface',
    'idna',
    'pyasn1',
    'pyserial',
    'python-subunit',
    'constantly',
    'appdirs',
    'h2',
    'priority',
]

# Dependencies that don't work on PyPy
CEXT_DEPENDENCIES = [
    'pycrypto',
]

# Dependencies that don't work on CPython 3.3+
EXTRA_DEPENDENCIES = [
    'soappy',
]

# Dependencies that don't work on Windows or Python 3.3+
PY2_NONWIN_DEPENDENCIES = [
    'pysqlite',
]

# Dependencies for running on Windows
WINDOWS_DEPENDENCIES = [
    "cffi",
    "pypiwin32",
]

# Dependencies used for coverage testing
COVERAGE_DEPENDENCIES = [
    'coverage==4.0.0', # FIXME: 4.0.1 causes a test failure
    'codecov',
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
    trial = "-m twisted.trial"



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
            python = ['python']

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
                ("pygobject", "gi", "gi.version_info"),
                ("pywin32", "win32api",
                 "win32api.GetFileVersionInfo(win32api.__file__, chr(92))['FileVersionLS'] >> 16"),
                ("pyasn1", "pyasn1", "pyasn1.__version__"),
                ("cffi", "cffi", "cffi.__version__"),
                ("constantly", "constantly", "constantly.__version__"),
                ("cryptography", "cryptography", "cryptography.__version__"),
            ],
            pkg_resources=[
                ("subunit", "subunit"),
                ("zope.interface", "zope.interface"),
            ])


    def __init__(self, python, source, uncleanWarnings, trialTests=None,
                 trialMode=None, virtualenv=False,
                 virtualenv_module='virtualenv',
                 platform='unix',
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
            python = [python, "-Wall"]

        assert platform in ["unix", "windows"]

        self._platform = platform
        if platform == "unix":
            self._path = posixpath
        elif platform == "windows":
            self._path = ntpath

        self.python = python
        self.virtualenv = virtualenv
        self.uncleanWarnings = uncleanWarnings
        self.forceGarbageCollection = forceGarbageCollection
        self.trialMode = trialMode
        if trialTests is None:
            trialTests = [WithProperties("%(test-case-name:~twisted)s")]
        self.trialTests = trialTests

        if virtualenv:
            # Hopefully temporary workaround for --clear not working:
            # https://github.com/pypa/virtualenv/issues/929
            self.addStep(
                shell.ShellCommand,
                command = self.python + [
                    "-c", "import shutil, sys;"
                    "shutil.rmtree(sys.argv[1], ignore_errors=True)",
                    self._virtualEnvPath,
                ]
            )
            self.addStep(
                shell.ShellCommand,
                command = self.python + [
                    "-m", virtualenv_module, self._virtualEnvPath,
                ]
            )

        else:
            # Report the versions, since we're using the system ones. If it's a
            # virtualenv, it's up to the venv factory to report the versions
            # itself.
            self._reportVersions(python=self.python)


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
            if self.virtualenv:
                kw['python'] = "python"
            else:
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
        if self._platform == "windows":
            return self._path.join('..', 'venv', 'Scripts')
        else:
            return self._path.join('..', 'venv', 'bin')


    @property
    def _virtualEnvPath(self):
        """
        Path to the root virtualenv folder.
        """
        return self._path.join('..', 'venv')


    def addVirtualEnvStep(self, step, **kwargs):
        """
        Add a step which is executed with virtualenv path.
        """
        # Update PATH environment so that the virtualenv is listed first.
        env = kwargs.get('env', {})
        path = env.get('PATH', '')

        if self._path is ntpath:
            pathsep = ";"
        else:
            pathsep = ":"

        env['PATH'] = pathsep.join([self._virtualEnvBin, path, '${PATH}'])
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

        # Build our extensions, in case any API documentation wants to link to
        # them.
        self.addVirtualEnvStep(
            shell.Compile,
            command=[python, "setup.py", "build_ext", "-i"])

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



class TwistedToxBuildFactory(BuildFactory):
    """
    A build factor for running the tests in a virtual environment which is set
    up using tox.
    """

    workdir = "Twisted"

    def __init__(self, source, toxEnv, reactors=["default"],
                 allowSystemPackages=False, platform="unix", python="python"):

        BuildFactory.__init__(self, source)

        tests = [WithProperties("%(test-case-name:~)s")]
        tests = []

        assert platform in ["unix", "windows"]

        self._platform = platform
        if platform == "unix":
            self._path = posixpath
        elif platform == "windows":
            self._path = ntpath

        self.addStep(
            shell.ShellCommand,
            description="clearing virtualenv".split(" "),
            command = [python, "-c", "import shutil; shutil.rmtree('" + self._virtualEnvPath + "', True)"],
        )

        self.addStep(
            shell.ShellCommand,
            description="making virtualenv".split(" "),
            command = [python, "-m", "virtualenv", self._virtualEnvPath]
        )

        self.addVirtualEnvStep(
            shell.ShellCommand,
            description="installing tox".split(" "),
            command=["python", "-m", "pip", "install", "tox", "virtualenv"]
        )

        for reactor in reactors:
            self.addVirtualEnvStep(TrialTox,
                                   tests=tests,
                                   allowSystemPackages=allowSystemPackages,
                                   reactor=reactor,
                                   toxEnv=toxEnv)


    @property
    def _virtualEnvBin(self):
        """
        Path to the virtualenv bin folder.
        """
        if self._platform == "windows":
            return self._path.join('..', 'venv', 'Scripts')
        else:
            return self._path.join('..', 'venv', 'bin')


    @property
    def _virtualEnvPath(self):
        """
        Path to the root virtualenv folder.
        """
        return self._path.join('..', 'venv')


    def addVirtualEnvStep(self, step, **kwargs):
        """
        Add a step which is executed with virtualenv path.
        """
        # Update PATH environment so that the virtualenv is listed first.
        env = kwargs.get('env', {})
        path = env.get('PATH', '')

        if self._path is ntpath:
            pathsep = ";"
        else:
            pathsep = ":"

        env['PATH'] = pathsep.join([self._virtualEnvBin, path, '${PATH}'])
        kwargs['env'] = env
        self.addStep(step, **kwargs)



class TwistedToxCoverageBuildFactory(TwistedToxBuildFactory):

    def __init__(self, source, toxEnv, buildID, reactors=["default"],
                 allowSystemPackages=False, platform="unix", python="python",
                 env={}):

        tests = [WithProperties("%(test-case-name:~)s")]
        tests = []

        BuildFactory.__init__(self, source)

        assert platform in ["unix", "windows"]

        self._platform = platform
        if platform == "unix":
            self._path = posixpath
        elif platform == "windows":
            self._path = ntpath

        self.addStep(
            shell.ShellCommand,
            description="clearing virtualenv".split(" "),
            command = [python, "-c", "import shutil; shutil.rmtree('" + self._virtualEnvPath + "', True)"],
        )

        self.addStep(
            shell.ShellCommand,
            description="making virtualenv".split(" "),
            command = [python, "-m", "virtualenv", self._virtualEnvPath]
        )

        self.addVirtualEnvStep(
            shell.ShellCommand,
            description="installing tox".split(" "),
            command=["python", "-m", "pip", "install", "tox", "virtualenv",
                     "coverage", "codecov"]
        )

        self.addVirtualEnvStep(
            shell.ShellCommand,
            description="clearing coverage".split(" "),
            command=["coverage", "erase"]
        )

        for reactor in reactors:
            self.addVirtualEnvStep(TrialTox,
                                   allowSystemPackages=allowSystemPackages,
                                   reactor=reactor,
                                   tests=tests,
                                   toxEnv=toxEnv,
                                   commandNumber=2,
                                   _env=env,
            )

        self.addVirtualEnvStep(
            shell.ShellCommand,
            description = "run coverage combine".split(" "),
            command=["python", "-m", "coverage", 'combine']
        )

        self.addVirtualEnvStep(
            shell.ShellCommand,
            description = "run coverage xml".split(" "),
            command=["python", "-m", "coverage", 'xml', '-o', 'coverage.xml',
                     '-i'])

        self.addVirtualEnvStep(
            shell.ShellCommand,
            warnOnFailure=True,
            description="upload to codecov".split(" "),
            command=["codecov",
                     "--token={}".format(private.codecov_twisted_token),
                     "--build={}".format(buildID),
                     "--file=coverage.xml",
                     WithProperties("--commit=%(got_revision)s")
            ],
        )


class TwistedVirtualenvReactorsBuildFactory(TwistedBaseFactory):
    treeStableTimer = 5*60

    def __init__(self, source, RemovePYCs=RemovePYCs, python="python",
                 trial="-m twisted.trial", virtualenv_module="virtualenv",
                 reactors=["select"], uncleanWarnings=False, platform="unix",
                 dependencies=BASE_DEPENDENCIES + CEXT_DEPENDENCIES + PY2_NONWIN_DEPENDENCIES + EXTRA_DEPENDENCIES,
                 forceGarbageCollection=False, tests=None, symlinkGIFrom=None):

        TwistedBaseFactory.__init__(
            self,
            source=source,
            python=python,
            uncleanWarnings=uncleanWarnings,
            platform=platform,
            virtualenv=True,
            virtualenv_module=virtualenv_module,
            forceGarbageCollection=forceGarbageCollection,
            trialTests=tests,
        )

        self.addVirtualEnvStep(
            shell.ShellCommand,
            description = "installing dependencies".split(" "),
            command=['python', '-m', 'pip', 'install'] + dependencies
        )

        if symlinkGIFrom:
            pythonVer = list(filter(lambda _: 'python' in _,
                                    symlinkGIFrom.split('/')))[0]

            self.addStep(
                shell.ShellCommand,
                description="symlinking gi".split(" "),
                command=[
                    "ln", "-s", '/'.join([symlinkGIFrom, "gi"]),
                    '/'.join([self._virtualEnvPath, "lib", pythonVer, "site-packages"])])
            self.addStep(
                shell.ShellCommand,
                description="symlinking pygtkcompat".split(" "),
                command=[
                    "ln", "-s", '/'.join([symlinkGIFrom, "pygtkcompat"]),
                    '/'.join([self._virtualEnvPath, "lib", pythonVer, "site-packages"])])

        self._reportVersions(virtualenv=True)

        cmd = ["python", "setup.py", "build_ext", "-i"]
        self.addVirtualEnvStep(shell.Compile, command=cmd, warnOnFailure=True)

        for reactor in reactors:
            self.addStep(RemovePYCs)
            self.addStep(RemoveTrialTemp, python=self.python)
            self.addTrialStep(
                name=reactor, reactor=reactor, flunkOnFailure=True,
                warnOnFailure=False, virtualenv=True, trial=trial)



class TwistedBdistFactory(TwistedBaseFactory):
    treeStableTimer = 5*60

    uploadBase = 'build_products/'
    def __init__(self, source, uncleanWarnings, arch, pyVersion):
        python = self.python(pyVersion)
        TwistedBaseFactory.__init__(self, python, source, uncleanWarnings)
        learnVersion = LearnVersion(
            python=python,
            package='twisted',
            workdir='Twisted',
            )
        self.addStep(learnVersion)

        def transformVersion(build):
            return build.getProperty("version").split("+")[0].split("pre")[0]
        self.addStep(SetBuildProperty,
            property_name='versionMsi', value=transformVersion)

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



class TwistedCoveragePyFactory(TwistedBaseFactory):
    OMIT_PATHS = [
        '/usr/*',
        '_trial_temp/*',
        ]

    def __init__(self, python, source, buildID=None, trial="-m twisted.trial",
                 tests=None, dependencies=BASE_DEPENDENCIES + CEXT_DEPENDENCIES + PY2_NONWIN_DEPENDENCIES + EXTRA_DEPENDENCIES,
                 platform='unix', RemovePYCs=RemovePYCs, uncleanWarnings=False):

        TwistedBaseFactory.__init__(
            self,
            source=source,
            python=python,
            uncleanWarnings=uncleanWarnings,
            virtualenv=True,
            platform=platform,
            trialTests=tests,
        )

        OMIT = self.OMIT_PATHS[:]
        OMIT.append(self._virtualEnvPath + "/*")

        self.addVirtualEnvStep(
            shell.ShellCommand,
            description = "installing dependencies".split(" "),
            command=["python", '-m', 'pip', 'install'] + dependencies + COVERAGE_DEPENDENCIES
        )

        self._reportVersions(virtualenv=True)

        cmd = ["python", "setup.py", "build_ext", "-i"]
        self.addVirtualEnvStep(shell.Compile, command=cmd, warnOnFailure=True)

        self.addStep(RemovePYCs)

        self.addTrialStep(
            flunkOnFailure=True,
            python=["python",
                    "-m", "coverage", "run",
                    "--omit", ','.join(self.OMIT_PATHS),
                    "--branch"],
            warnOnFailure=False, virtualenv=True, trial=trial)

        self.addVirtualEnvStep(
            shell.ShellCommand,
            description = "run coverage combine".split(" "),
            command=["python", "-m", "coverage", "combine"])

        self.addVirtualEnvStep(
            shell.ShellCommand,
            description = "run coverage xml".split(" "),
            command=["python", "-m", "coverage", 'xml', '-o', 'coverage.xml',
                     '--omit', ','.join(OMIT), '-i'])

        self.addVirtualEnvStep(
            shell.ShellCommand,
            warnOnFailure=True,
            description="upload to codecov".split(" "),
            command=["codecov",
                     "--token={}".format(private.codecov_twisted_token),
                     "--build={}".format(buildID),
                     "--file=coverage.xml",
                     WithProperties("--commit=%(got_revision)s")
            ],
        )



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
