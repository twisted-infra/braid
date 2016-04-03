
from twisted.trial.unittest import TestCase

from txbuildbot import filterTox


class FilterToxTests(TestCase):
    """
    Tests for L{filterTox}.
    """

    def test_nonZeroStep(self):
        text = """GLOB sdist-make: /Users/red/code/twgit/setup.py
py27-coverage create: /Users/red/code/twgit/build/py27-coverage
py27-coverage installdeps: zope.interface, constantly, pyopenssl, service_identity, idna, pyserial, python-subunit, pycrypto, appdirs, soappy, coverage
py27-coverage inst: /Users/red/code/twgit/build/dist/Twisted-16.0.0.zip
py27-coverage installed: -f file:///Users/red/.cache/pip/wheelhouse,appdirs==1.4.0,attrs==15.2.0,cffi==1.5.2,constantly==15.1.0,coverage==4.0.3,cryptography==1.3.1,defusedxml==0.4.1,docutils==0.12,enum34==1.1.2,extras==0.0.3,fixtures==1.4.0,idna==2.1,ipaddress==1.0.16,linecache2==1.0.0,pbr==1.8.1,pyasn1==0.1.9,pyasn1-modules==0.0.8,pycparser==2.14,pycrypto==2.6.1,pyOpenSSL==16.0.0,pyrsistent==0.11.12,pyserial==3.0.1,python-mimeparse==1.5.1,python-subunit==1.2.0,service-identity==16.0.0,six==1.10.0,SOAPpy==0.12.22,testtools==2.0.0,traceback2==1.4.0,Twisted==16.0.0,unittest2==1.1.0,wstools==0.4.3,zope.interface==4.1.3
py27-coverage runtests: PYTHONHASHSEED='4251224165'
py27-coverage runtests: commands[0] | coverage erase
py27-coverage runtests: commands[1] | coverage run --rcfile=/Users/red/code/twgit/.coveragerc /Users/red/code/twgit/build/py27-coverage/bin/trial --reporter=bwverbose twisted.test.test_stdio
twisted.test.test_stdio.StandardInputOutputTests.test_consumer ... [OK]
twisted.test.test_stdio.StandardInputOutputTests.test_hostAndPeer ... [OK]
twisted.test.test_stdio.StandardInputOutputTests.test_lastWriteReceived ... [OK]
twisted.test.test_stdio.StandardInputOutputTests.test_loseConnection ... [OK]
twisted.test.test_stdio.StandardInputOutputTests.test_normalFileStandardOut ... [OK]
twisted.test.test_stdio.StandardInputOutputTests.test_producer ... [OK]
twisted.test.test_stdio.StandardInputOutputTests.test_readConnectionLost ... [OK]
twisted.test.test_stdio.StandardInputOutputTests.test_write ... [OK]
twisted.test.test_stdio.StandardInputOutputTests.test_writeSequence ... [OK]

-------------------------------------------------------------------------------
Ran 9 tests in 4.051s

PASSED (successes=9)
py27-coverage runtests: commands[2] | coverage report --rcfile=/Users/red/code/twgit/.coveragerc
Name                                                                                                                 Stmts   Miss Branch BrPart     Cover
---------------------------------------------------------------------------------------------------------------------------------------------------------
/Users/red/code/twgit/build/py27-coverage/lib/python2.7/site-packages/twisted/__init__.py                               33     10     10      4    67.44%
/Users/red/code/twgit/build/py27-coverage/lib/python2.7/site-packages/twisted/words/__init__.py                          6      0      0      0   100.00%
/Users/red/code/twgit/build/py27-coverage/lib/python2.7/site-packages/twisted/words/iwords.py                           40      0     44     22    73.81%
---------------------------------------------------------------------------------------------------------------------------------------------------------
TOTAL                                                                                                                17435   9938   5493    686    38.24%
__________________________________________________________________________________________________ summary __________________________________________________________________________________________________
  py27-coverage: commands succeeded
  congratulations :)"""

        filtered = "\n".join(filterTox(text, commandNumber=1))

        self.assertEqual(filtered, """twisted.test.test_stdio.StandardInputOutputTests.test_consumer ... [OK]
twisted.test.test_stdio.StandardInputOutputTests.test_hostAndPeer ... [OK]
twisted.test.test_stdio.StandardInputOutputTests.test_lastWriteReceived ... [OK]
twisted.test.test_stdio.StandardInputOutputTests.test_loseConnection ... [OK]
twisted.test.test_stdio.StandardInputOutputTests.test_normalFileStandardOut ... [OK]
twisted.test.test_stdio.StandardInputOutputTests.test_producer ... [OK]
twisted.test.test_stdio.StandardInputOutputTests.test_readConnectionLost ... [OK]
twisted.test.test_stdio.StandardInputOutputTests.test_write ... [OK]
twisted.test.test_stdio.StandardInputOutputTests.test_writeSequence ... [OK]

-------------------------------------------------------------------------------
Ran 9 tests in 4.051s

PASSED (successes=9)""")

    def test_isolateStep(self):
        text = """GLOB sdist-make: /Users/red/code/twgit/setup.py
pyflakes create: /Users/red/code/twgit/build/pyflakes
pyflakes installdeps: zope.interface, constantly, pyflakes
pyflakes inst: /Users/red/code/twgit/build/dist/Twisted-16.0.0.zip
pyflakes installed: -f file:///Users/red/.cache/pip/wheelhouse,constantly==15.1.0,pyflakes==1.1.0,Twisted==16.0.0,zope.interface==4.1.3
pyflakes runtests: PYTHONHASHSEED='2754180371'
pyflakes runtests: commands[0] | pyflakes twisted
twisted/runner/inetdtap.py:22: 'portmap' imported but unused
twisted/runner/inetdtap.py:55: redefinition of unused 'portmap' from line 22
twisted/runner/inetdtap.py:58: undefined name 'rpcVersions'
twisted/runner/inetdtap.py:59: undefined name 'name'
twisted/runner/inetdtap.py:62: undefined name 'p'
twisted/runner/inetdtap.py:152: undefined name 'proto'
twisted/scripts/tap2deb.py:77: local variable 'maintainer' is assigned to but never used
twisted/scripts/tap2deb.py:78: local variable 'description' is assigned to but never used
twisted/scripts/tap2deb.py:80: local variable 'longDescription' is assigned to but never used
twisted/scripts/tap2deb.py:82: local variable 'twistdOption' is assigned to but never used
twisted/scripts/tap2deb.py:83: local variable 'date' is assigned to but never used
twisted/scripts/tap2deb.py:85: local variable 'pythonVersion' is assigned to but never used
twisted/words/xish/xpathparser.py:326: redefinition of unused 'sys' from line 36
twisted/words/xish/xpathparser.py:326: redefinition of unused 're' from line 36
twisted/words/xish/xpathparser.py:366: local variable 'END' is assigned to but never used
twisted/words/xish/xpathparser.py:383: local variable 'WILDCARD' is assigned to but never used
twisted/words/xish/xpathparser.py:417: local variable '_context' is assigned to but never used
twisted/words/xish/xpathparser.py:475: local variable '_context' is assigned to but never used
twisted/words/xish/xpathparser.py:485: local variable '_context' is assigned to but never used
ERROR: InvocationError: '/Users/red/code/twgit/build/pyflakes/bin/pyflakes twisted'
___________________________________ summary ____________________________________
ERROR:   pyflakes: commands failed"""

        filtered = "\n".join(filterTox(text, commandNumber=0))

        self.assertEqual(filtered, """twisted/runner/inetdtap.py:22: 'portmap' imported but unused
twisted/runner/inetdtap.py:55: redefinition of unused 'portmap' from line 22
twisted/runner/inetdtap.py:58: undefined name 'rpcVersions'
twisted/runner/inetdtap.py:59: undefined name 'name'
twisted/runner/inetdtap.py:62: undefined name 'p'
twisted/runner/inetdtap.py:152: undefined name 'proto'
twisted/scripts/tap2deb.py:77: local variable 'maintainer' is assigned to but never used
twisted/scripts/tap2deb.py:78: local variable 'description' is assigned to but never used
twisted/scripts/tap2deb.py:80: local variable 'longDescription' is assigned to but never used
twisted/scripts/tap2deb.py:82: local variable 'twistdOption' is assigned to but never used
twisted/scripts/tap2deb.py:83: local variable 'date' is assigned to but never used
twisted/scripts/tap2deb.py:85: local variable 'pythonVersion' is assigned to but never used
twisted/words/xish/xpathparser.py:326: redefinition of unused 'sys' from line 36
twisted/words/xish/xpathparser.py:326: redefinition of unused 're' from line 36
twisted/words/xish/xpathparser.py:366: local variable 'END' is assigned to but never used
twisted/words/xish/xpathparser.py:383: local variable 'WILDCARD' is assigned to but never used
twisted/words/xish/xpathparser.py:417: local variable '_context' is assigned to but never used
twisted/words/xish/xpathparser.py:475: local variable '_context' is assigned to but never used
twisted/words/xish/xpathparser.py:485: local variable '_context' is assigned to but never used""")
