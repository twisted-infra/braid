# -*- makefile -*-

# everything Buildbot related goes under ~/BuildBot
# buildbot code from CVS will be stuffed in ~/BuildBot/Buildbot
#  e.g. ~/BuildBot/Buildbot/buildbot/master.py

# other python modules may be needed (Twisted, CVSToys). If the versions in
# /usr/lib are not sufficient, newer versions should be extracted under
# ~/BuildBot and symlinks installed from ~/BuildBot/support-master to their
# top-level modules. Both ~/BuildBot/Buildbot and ~/BuildBot/support-master
# will be added to PYTHONPATH for the buildmaster. ~/BuildBot/support-slave
# will be provided for the slave, and may contain different symlinks.

# buildmaster-private data (e.g. private.py) also lives in support-master/

BBBASE := ~/BuildBot/Buildbot
MPP = PYTHONPATH=$(PYTHONPATH):~/BuildBot/support-master
SPP = PYTHONPATH=$(PYTHONPATH):~/BuildBot/support-slave
MDIR = ~/BuildBot/master
SDIR = ~/BuildBot/slave
S2DIR = ~/BuildBot/slave-xvfb

.PHONY: master slave

master:
	buildbot master $(MDIR)

start-master:
	buildbot start $(MDIR)
restart-master:
	buildbot stop $(MDIR)
	buildbot start $(MDIR)
reconfig:
	buildbot sighup $(MDIR)
stop-master:
	buildbot stop $(MDIR)

diff-config:
	-diff $(BBBASE)/docs/examples/twisted_master.cfg $(MDIR)/master.cfg
install-config:
	cp $(BBBASE)/docs/examples/twisted_master.cfg $(MDIR)/master.cfg


clean-master-all:
	cd $(MDIR) && rm -rf OS-X debuild freebsd full-2.2 full-2.3 quick reactors twistd.log*
clean-master:
	cd $(MDIR) && find . -mindepth 2 -type f -mtime +14 -exec rm {} \;
	cd $(MDIR) && find twistd.log* -mtime +30 -exec rm {} \;
clean-slave:
	cd $(SDIR) && find twistd.log* -mtime +30 -exec rm {} \;
	cd $(S2DIR) && find twistd.log* -mtime +30 -exec rm {} \;

stable-slave:
	buildbot slave $(SDIR) pyramid.twistedmatrix.com:9987 bot1 sekrit

unstable-slave:
	buildbot slave $(S2DIR) pyramid.twistedmatrix.com:9987 bot2 sekrit
# slave2 wants to run inside an xvfb so the gtk reactors can be tested. This
# is handled by the Makefile.buildbot in the unstable slave's basedir.

start-slave:
	nice buildbot start $(SDIR)
stop-slave:
	buildbot stop $(SDIR)
start-slave2:
	nice buildbot start $(S2DIR)
stop-slave2:
	buildbot stop $(S2DIR)

