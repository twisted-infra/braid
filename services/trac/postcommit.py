import os

from twisted.python import log
from twisted.spread import pb
from twisted.internet import utils
from twisted.application import internet

class TracPostCommitPbServerRoot(pb.Root):
    def __init__(self, allowedIP, tracEnvPath, tracURL, postCommitHook):
        self.allowedIP = allowedIP
        self.tracEnvPath = tracEnvPath
        self.tracURL = tracURL
        self.postCommitHook = postCommitHook

    def remote_postCommit(self, revision, author, msg):
        log.msg("postCommit(revision=%(revision)r)", revision=revision)
        result = utils.getProcessOutput(
            self.postCommitHook, ['-p', self.tracEnvPath,
                                  '-r', str(revision),
                                  '-u', author,
                                  '-m', msg,
                                  '-s', self.tracURL],
            errortoo=True, env=os.environ)
        def hooked(result):
            log.msg("hook completed: %(result)r", result=result)
            return result
        def failed(reason):
            log.err(reason, "hook failed")
            return reason
        result.addCallbacks(hooked, failed)
        return result


class TracPostCommitPbServerRootFactory(pb.PBServerFactory):
    def buildProtocol(self, addr):
        if addr.host != self.root.allowedIP:
            raise Exception("DISALLOWED")
        return pb.PBServerFactory.buildProtocol(self, addr)


def service(vcsServer, postCommitHook, tracEnvPath, tracURL, tracCommitServerPort):
    root = TracPostCommitPbServerRoot(
                allowedIP=vcsServer,
                tracEnvPath=tracEnvPath,
                tracURL=tracURL,
                postCommitHook=postCommitHook)
    return internet.TCPServer(
        tracCommitServerPort,
        TracPostCommitPbServerRootFactory(root))
