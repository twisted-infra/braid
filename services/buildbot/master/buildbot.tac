from twisted.application import service
from buildbot.master import BuildMaster

from os.path import expanduser
from twisted.python.util import sibpath

basedir = expanduser('~/data')
configfile = sibpath(__file__, 'master.cfg')

application = service.Application('buildmaster')

BuildMaster(basedir, configfile).setServiceParent(application)
