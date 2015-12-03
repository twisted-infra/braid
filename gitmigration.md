# GITHUB MIGRATION PLAN #

## Objectives ##

-  https://github.com/twisted/twisted will be the "repository of truth" for Twisted.
     - Twisted releases will be done from GitHub
     - the Twisted developers who are now "core committers" for SVN, will be given access to be "core committers" to https://github.com/twisted/twisted . Committers to Twisted must have 2FA enabled, existing Twisted org members will get given access during the migration, but those that are not part of the Twisted org can be emailed with a mention that 2FA is required, and we can invite once that is set up.

- Trac will still be used for filing tickets.  Filing issues in GitHub will be disabled.

## Task Items ##

- Task items for this effort will be tracked here: https://github.com/twisted-infra/braid/milestones/Migrate-to-Git

## Plan ##
### Staging Environment ###
- [ ] Copy ``twisted/twisted`` to ``twisted/twisted-staging``
- [ ] Investigate to see if we can trim out older branches on the existing git mirror, and only leaving tags and trunk/master.
- [ ] Investigate ``.mailmap`` and similar to alter/amend history to update existing contributor metadata to be their current GitHub email
- [ ] Make the base branch "master" instead of trunk
- [ ] Push this 'staging' repo to GitHub, NOT under ``twisted/twisted``
- [ ] Create a staging Trac server
- [ ] In 'staging' Trac, install https://github.com/trac-hacks/trac-GitHub
- [ ] In 'staging' GitHub repo add the webhook to poke the 'staging' Trac
- [ ] Commit some things to the staging GitHub repo, make sure the staging trac picks them up, and it's propagated to Kenaan and such.
- [ ] Make sure that existing Trac changeset links go to the SVN repo viewer, and new Git changesets redirect from Trac to GitHub. https://github.com/twisted-infra/braid/issues/138

### Accounts ###
- [ ] Make sure that all users who have SVN commit access have a GitHub account which can commit to the Twisted repository on GitHub, https://github.com/twisted-infra/braid/issues/158

### Infrastructure ###
- [ ] Migrate SVN commit hooks to GitHub, https://github.com/twisted-infra/braid/issues/141, https://github.com/twisted-infra/braid/issues/147
- [ ] Update all buildbots to get code from GitHub, https://github.com/twisted-infra/braid/issues/73, https://github.com/twisted-infra/braid/issues/141
- [ ] Change Kenaan IRC bot to monitor GitHub, https://github.com/twisted-infra/braid/issues/137

### Documentation ###
- [ ] Update all wiki documentation to change all references to getting code from Subversion, to getting code from GitHub. https://github.com/twisted-infra/braid/issues/159
- [ ] Update Release Engineering documentation for doing a release from GitHub, https://github.com/twisted-infra/braid/issues/156

### Migration schedule ###
- [ ] Pick a weekend where Amber isn't doing anything, send out warnings, queue up a ticket for testing
- [ ] Send e-mail one week before scheduled maintenance.
- [ ] Before the maintenance begins, send another HEADSUP e-mail.
- [ ] Disable commits to Subversion: http://stackoverflow.com/questions/2411122/how-to-freeze-entire-svn-repository-to-make-it-read-only
- [ ] Install trac-GitHub as on the staging on the production trac, and set up ``twisted/twisted`` to connect to the production webhook.
- [ ] Merge the ticket queued up for testing, make sure production Trac knows about it.
- [ ] Send HEADSUP e-mail saying that GitHub migration is done, #68
- [ ] Delete the ``twisted/twisted-staging`` repo.
