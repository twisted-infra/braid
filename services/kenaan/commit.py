
import os, re

from twisted.internet import reactor, protocol, defer
from twisted.python import log
from twisted.spread import pb

import config

SVNLOOK = '/usr/bin/svnlook'

ADDED = 'A'
DELETED = 'D'
MODIFIED = 'U'

class Change(pb.Copyable, pb.RemoteCopy):
    def __init__(self, path, changeType, propchange=False):
        self.path = path
        self.changeType = changeType
        self.propchange = propchange

    def __str__(self):
        mod = self.changeType
        if self.propchange:
            mod = '_' + mod
        return mod + ' ' + self.path

    def __repr__(self):
        return 'Change(%r, %r, propchange=%r)' % (
            self.path, self.changeType, self.propchange)

    def fromString(cls, status):
        parts = status.split(None, 1)
        propchange = '_' in parts[0]
        return cls(parts[1], parts[0][-1:], propchange)
    fromString = classmethod(fromString)
pb.setUnjellyableForClass(Change, Change)

class _Look(protocol.ProcessProtocol):
    def __init__(self, onDone):
        self.onDone = onDone

    def connectionMade(self):
        self.out = []
        self.err = []
        self.transport.closeStdin()

    def outReceived(self, bytes):
        self.out.append(bytes)

    def errReceived(self, bytes):
        self.err.append(bytes)

    def processEnded(self, reason):
        if self.err:
            log.msg("Error output received:")
            log.msg(repr(''.join(self.err)))
            log.msg("Standard output received:")
            log.msg(repr(''.join(self.out)))
            self.onDone.errback(Exception("Something went wrong",
                                          ''.join(self.err),
                                          ''.join(self.out)))
        else:
            self.onDone.callback(self.done(''.join(self.out)))

class LookInfo(_Look):
    def done(self, bytes):
        lines = bytes.strip().splitlines()
        author, date, logMsgSize = lines[:3]
        logMsg = lines[3:]
        return author, logMsg

class LookChanged(_Look):
    def done(self, bytes):
        return map(Change.fromString, bytes.splitlines())

class RepositoryChangeListener:
    """
    Mixin for a PB Referenceable which accepts repository change
    notifications.
    """
    def remote_change(self, repo, rev, author, msg, changes):
        log.msg("change(%r, %r, %r, %r, %r)" % (repo, rev, author, msg, changes))
        self.proto.change(repo, rev, author, msg, changes)

class RepositoryChange:
    def sendChangeTo(self, channel, repo, rev, author, msg, changes):
        self.join(channel)
        msg = msg[0]
        fmt = '\x0303%(author)s \x0310r%(rev)s\x0314%(prefix)s%(changes)s\x0f: %(msg)s'
        adds = []
        deletes = []
        modifies = []

        if len(changes) > 1:
            pfx = '/'.join(os.path.commonprefix([ch.path.split('/') for ch in changes]))
            if pfx:
                prefix = ' ' + pfx
                for ch in changes:
                    ch.path = ch.path[len(pfx):]
            else:
                prefix = ''
        else:
            prefix = ''

        for ch in changes:
            if len(changes) == 1 or ch.path.endswith('/'):
                p = ch.path
            else:
                p = os.path.basename(ch.path)
            if p:
                if ch.propchange:
                    p = p + '*'
                {ADDED: adds,
                 DELETED: deletes,
                 MODIFIED: modifies}[ch.changeType].append(p)

        # Not a rigorous max group length enforcement thingy, but a
        # reasonable heuristic.  Make it better later.
        M = 15
        if len(adds) + len(deletes) + len(modifies) > M:
            L = [adds, deletes, modifies]
            L.sort(key=len)
            del L[2][M - (len(L[0]) + len(L[1])):]
            L[2].append('...')

        changes = ((adds and ' \x0305A(' + ' '.join(adds) + ')' or '') +
                   (deletes and ' \x0306D(' + ' '.join(deletes) + ')' or '') +
                   (modifies and ' \x0307M(' + ' '.join(modifies) + ')' or ''))
        trailer = ' ...'
        ircmsg = fmt % locals()
        ircmsg = ircmsg[:240 - len(trailer)] + trailer

        # Freenode kind of sucks.
        self.msg(channel, ircmsg, config.LINE_LENGTH)

    def change(self, repo, rev, author, msg, changes):
        sentTo = []
        for (repoRule, pathRule, channels) in config.COMMIT_RULES:
            for channel in channels:
                if channel in sentTo:
                    continue
                if re.match(repoRule, repo):
                    for change in changes:
                        if re.match(pathRule, change.path):
                            self.sendChangeTo(
                                channel,
                                repo,
                                rev,
                                author,
                                msg,
                                # This is pretty lame, but it is the easiest
                                # way to not have to touch the logic in
                                # sendChangeTo, which mutates Change
                                # instances (because it is stupid).
                                [Change(ch.path, ch.changeType, ch.propchange)
                                 for ch
                                 in changes])
                            sentTo.append(channel)
                            break

def _collect(repo, rev):
    infoD = defer.Deferred()
    changedD = defer.Deferred()
    reactor.spawnProcess(LookInfo(infoD), SVNLOOK, args=('svnlook', 'info',
                                                         repo, '--revision',
                                                         str(rev)))
    reactor.spawnProcess(LookChanged(changedD), SVNLOOK, args=('svnlook',
                                                               'changed',
                                                               repo,
                                                               '--revision',
                                                               str(rev)))
    return defer.DeferredList([infoD, changedD])

def _report(((infoSuccess, infoResult), (changeSuccess, changeResult)),
            repo, rev):
    if not infoSuccess:
        return infoResult
    if not changeSuccess:
        return changeResult

    # Connect
    def cbRoot(rootObj):
        return rootObj.callRemote(
            'change',
            repo=repo, rev=rev,
            author=infoResult[0], msg=infoResult[1],
            changes=changeResult)
    cf = pb.PBClientFactory()
    reactor.connectTCP(config.BOT_HOST, config.BOT_PORT, cf)
    rootD = cf.getRootObject()
    rootD.addCallback(cbRoot)
    return rootD

def _collectAndReport(repo, rev):
    d = _collect(repo, rev)
    d.addCallback(_report, repo, rev)
    d.addErrback(log.err)
    d.addCallback(lambda ign: reactor.stop())



def _unblockAll():
    import ctypes

    SIG_SETMASK = 2

    libc = ctypes.CDLL('libc.so.6')
    sigprocmask = libc.sigprocmask
    sigprocmask.restype = ctypes.c_int
    sigprocmask.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_long)]
    new = ctypes.c_long(0)
    old = ctypes.c_long(0)
    print 'sigprocmask result:', sigprocmask(SIG_SETMASK, ctypes.pointer(new), ctypes.pointer(old))
    print 'old signal mask was:', old



def main(repo, rev):

    # In case invoked from mod_dav_svn, fix the signal mask.  As far as I
    # can tell, Apache blocks a crapload of stuff - most importantly SIGCHLD
    # - and we inherit that, breaking us.
    _unblockAll()

    reactor.callWhenRunning(_collectAndReport, repo, rev)
    reactor.run()
