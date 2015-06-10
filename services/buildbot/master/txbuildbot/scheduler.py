from buildbot.schedulers.basic import SingleBranchScheduler

class TwistedScheduler(SingleBranchScheduler):
    @staticmethod
    def fileIsImportant(change):
        for filename in change.files:
            if not filename.startswith("doc/fun/"):
                return 1
        return 0
