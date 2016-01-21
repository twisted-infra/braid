# -*- test-case-name: buildbot.test.test_twisted -*-

from twisted.python import log

from buildbot.status import builder
from buildbot.status.builder import SUCCESS, FAILURE, WARNINGS, SKIPPED
from buildbot.process.buildstep import LogLineObserver, OutputProgressObserver
from buildbot.process.buildstep import RemoteShellCommand, BuildStep
from buildbot.steps.shell import ShellCommand, SetProperty

try:
    import cStringIO
    StringIO = cStringIO
except ImportError:
    import StringIO
import re

# BuildSteps that are specific to the Twisted source tree


def countFailedTests(output):
    # start scanning 50kb from the end, because there might be a few kb of
    # import exception tracebacks between the total/time line and the errors
    # line
    chunk = output[-50000:]
    lines = chunk.split("\n")
    lines.pop() # blank line at end
    # lines[-3] is "Ran NN tests in 0.242s"
    # lines[-2] is blank
    # lines[-1] is 'OK' or 'FAILED (failures=1, errors=12)'
    #  or 'FAILED (failures=1)'
    #  or "PASSED (skips=N, successes=N)"  (for Twisted-2.0)
    # there might be other lines dumped here. Scan all the lines.
    res = {'total': None,
           'failures': 0,
           'errors': 0,
           'skips': 0,
           'expectedFailures': 0,
           'unexpectedSuccesses': 0,
           }
    for l in lines:
        out = re.search(r'Ran (\d+) tests', l)
        if out:
            res['total'] = int(out.group(1))
        if (l.startswith("OK") or
            l.startswith("FAILED ") or
            l.startswith("PASSED")):
            # the extra space on FAILED_ is to distinguish the overall
            # status from an individual test which failed. The lack of a
            # space on the OK is because it may be printed without any
            # additional text (if there are no skips,etc)
            out = re.search(r'failures=(\d+)', l)
            if out: res['failures'] = int(out.group(1))
            out = re.search(r'errors=(\d+)', l)
            if out: res['errors'] = int(out.group(1))
            out = re.search(r'skips=(\d+)', l)
            if out: res['skips'] = int(out.group(1))
            out = re.search(r'expectedFailures=(\d+)', l)
            if out: res['expectedFailures'] = int(out.group(1))
            out = re.search(r'unexpectedSuccesses=(\d+)', l)
            if out: res['unexpectedSuccesses'] = int(out.group(1))
            # successes= is a Twisted-2.0 addition, and is not currently used
            out = re.search(r'successes=(\d+)', l)
            if out: res['successes'] = int(out.group(1))

    return res


class TrialTestCaseCounter(LogLineObserver):
    _line_re = re.compile(r'^([\w\.]+) \.\.\. \[([^\]]+)\]$')
    numTests = 0
    finished = False

    def outLineReceived(self, line):
        # different versions of Twisted emit different per-test lines with
        # the bwverbose reporter.
        #  2.0.0: testSlave (buildbot.test.test_runner.Create) ... [OK]
        #  2.1.0: buildbot.test.test_runner.Create.testSlave ... [OK]
        #  2.4.0: buildbot.test.test_runner.Create.testSlave ... [OK]
        # Let's just handle the most recent version, since it's the easiest.

        if self.finished:
            return
        if line.startswith("=" * 40):
            self.finished = True
            return

        m = self._line_re.search(line.strip())
        if m:
            testname, result = m.groups()
            self.numTests += 1
            self.step.setProgress('tests', self.numTests)


UNSPECIFIED=() # since None is a valid choice

class ProcessDocs(ShellCommand):
    """
    I build all docs. This requires some LaTeX packages to be
    installed. It will result in the full documentation book (dvi,
    pdf, etc).
    """

    name = "process-docs"
    warnOnWarnings = 1
    command = [
        "python",
        "bin/admin/build-docs", "."]
    description = ["processing", "docs"]
    descriptionDone = ["docs"]
    # TODO: track output and time

    def createSummary(self, log):
        output = log.getText()
        # hlint warnings are of the format: 'WARNING: file:line:col: stuff
        # latex warnings start with "WARNING: LaTeX Warning: stuff", but
        # sometimes wrap around to a second line.
        lines = output.split("\n")
        warningLines = []
        wantNext = False
        for line in lines:
            wantThis = wantNext
            wantNext = False
            if line.startswith("WARNING: "):
                wantThis = True
                wantNext = True
            if wantThis:
                warningLines.append(line)

        if warningLines:
            self.addCompleteLog("warnings", "\n".join(warningLines) + "\n")
        self.warnings = len(warningLines)

    def evaluateCommand(self, cmd):
        if cmd.rc != 0:
            return FAILURE
        if self.warnings:
            return WARNINGS
        return SUCCESS

    def getText(self, cmd, results):
        if results == SUCCESS:
            return ["docs", "successful"]
        if results == WARNINGS:
            return ["docs",
                    "%d warnin%s" % (self.warnings,
                                     self.warnings == 1 and 'g' or 'gs')]
        if results == FAILURE:
            return ["docs", "failed"]

    def getText2(self, cmd, results):
        if results == WARNINGS:
            return ["%d do%s" % (self.warnings,
                                 self.warnings == 1 and 'c' or 'cs')]
        return ["docs"]



class ReportPythonModuleVersions(ShellCommand):
    """
    Load a number of Python modules and report their version information.

    @ivar _moduleInfo: A list of three-tuples.  The first element of
        each tuple is a human-readable label.  The second element of
        each tuple is a string giving the FQPN of a module to import
        to load version information from.  The third element of each
        tuple is a string giving a Python expression which, when
        evaluated, produces the desired version information.
        Importing the second element must be all that is necessary to
        make the third element accessible.

    @ivar _pkg_resources: A list of two-tuples.  The first element of
        each tuple is a human-readable label.  The second element is
        the name of a distribution which pkg_resources may be able to
        find and report the version of.
    """

    name = "report-module-versions"
    description = ["check", "module", "versions"]
    descriptionDone = ["module", "versions"]

    def __init__(self, python, moduleInfo, pkg_resources, **kwargs):
        ShellCommand.__init__(self, **kwargs)
        self._python = python
        self._moduleInfo = moduleInfo
        self._pkg_resources = pkg_resources


    def _formatSource(self, moduleInfo, pkg_resources):
        checks = "from __future__ import print_function\n"

        normalTemplate = (
            'try: import %(module)s\n'
            'except Exception as e: print( "Failed %(label)s: missing %(module)s", str(e))\n'
            'else:\n'
            '  try: version = %(version)s\n'
            '  except Exception as e: print("Failed %(label)s:", str(e))\n'
            '  else: print("found %(label)s, %(version)s =", version)\n')
        checks += '\n'.join([
            normalTemplate % dict(label=label, module=module, version=version)
            for (label, module, version)
            in moduleInfo]) + '\n'

        pkgresourcesTemplate = (
            'try: import pkg_resources, %(module)s\n'
            'except Exception as e: print("Failed %(label)s: missing %(module)s", str(e))\n'
            'else:\n'
            '\ttry: version = pkg_resources.get_distribution(%(module)r).version\n'
            '\texcept Exception as e: print("Failed %(label)s:", str(e))\n'
            '\telse: print("found %(label)s, distribution version =", version)\n')
        checks += '\n'.join([
            pkgresourcesTemplate % dict(label=label, module=module)
            for (label, module)
            in pkg_resources]) + '\n'

        # Cannot have newlines in this code, or it isn't compatible on
        # both POSIX and Windows.  Also, quotes make things really
        # confusing, so don't have any literal quotes.
        return 'from binascii import unhexlify; exec(unhexlify(b"%s"))' % (checks.encode('hex'),)


    def start(self):
        command = self._python + [
            "-c", self._formatSource(self._moduleInfo, self._pkg_resources)]
        self.setCommand(command)
        ShellCommand.start(self)


    def commandComplete(self, cmd):
        self.addCompleteLog("versions", cmd.logs['stdio'].getText())


    def evaluateCommand(self, cmd):
        if cmd.rc != 0:
            return FAILURE
        return SUCCESS


class RemovePYCs(ShellCommand):
    name = "remove-.pyc"
    command = 'find . -name "*.pyc" -or -name "*$py.class" | xargs rm -f'
    description = ["removing", "bytecode", "files"]
    descriptionDone = ["remove", "bytecode"]


class RemoveTrialTemp(ShellCommand):
    name = "remove-_trial_temp"
    description = ["removing", "_trial_temp"]
    descriptionDone = ["remove", "_trial_temp"]

    source = (
        "from __future__ import print_function\n"
        "import os, sys, time, shutil\n"
        "target = os.path.abspath(sys.argv[1])\n"
        "for i in range(10):\n"
        "    if os.path.exists(target):\n"
        "        print('Attempting to delete', target)\n"
        "        try:\n"
        "            shutil.rmtree(target, False)\n"
        "        except Exception as e:\n"
        "            print('Failed to delete:', e)\n"
        "            time.sleep(6)\n"
        "        else:\n"
        "            print('Succeeded')\n"
        "            break\n")

    def __init__(self, python):
        ShellCommand.__init__(self)
        self.command = python + [
            "-c",
            'import codecs; exec(codecs.decode("%s", "hex"))' % (self.source.encode('hex'),),
            "_trial_temp"]


class LearnVersion(SetProperty):
    """
    Import a package and set a version property based on its version.
    """
    src = (
        # Do not use multiple lines.  Windows cannot deal with it.
        'from %(package)s import __version__; '
        'print __version__; ')

    def _extractVersion(self, rc, stdout, stderr):
        # FIXME: SetProperty doesn't support using just stdout, so we write our
        # own extraction function.
        return {'version': stdout.strip()}

    def __init__(self, python, package, **kw):
        SetProperty.__init__(
            self,
            name="check-%s-version" % package,
            description="checking %s version" % package,
            command=[python, '-c', self.src % dict(package=package)],
            extract_fn=self._extractVersion, **kw)

        self.package = package

    def getText(self, cmd, results):
        if 'version' in self.property_changes:
            return [ "%s version %s" % (self.package, self.property_changes['version']) ]
        else:
            SetProperty.getText(self, cmd, results)


class SetBuildProperty(BuildStep):

    name = "set build property"

    def __init__(self, property_name, value, **kwargs):
        self.property_name = property_name
        self.value = value
        BuildStep.__init__(self, **kwargs)
        self.addFactoryArguments(property_name=property_name, value=value)

    def start(self):
        if callable(self.value):
            value = self.value(self.build)
        else:
            value = self.value
        self.setProperty(self.property_name, value)
        self.step_status.setText(['set props:', self.property_name])
        self.addCompleteLog("property changes", "%s: %s" % (self.property_name, value))
        return self.finished(SUCCESS)
