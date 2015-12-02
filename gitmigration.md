# GITHUB MIGRATION PLAN #

## Objectives ##

-  https://github.com/twisted/twisted will be the "repository of truth" for Twisted.
     - Twisted releases will be done from GitHub
     - the Twisted developers who are now "core committers" for SVN, must be 
       given access to be "core committers" to https://github.com/twisted/twisted

- Trac will still be used for filing tickets.  Filing issues in GitHub will be disabled.  

## Task Items ##

- Task items for this effort will be tracked here: https://github.com/twisted-infra/braid/milestones/Migrate-to-Git

## Plan ##
### Staging Environment ###
- [ ] Create a staging repository on GitHub, NOT under ``twisted/twisted``
- [ ] Do a Git -> SVN format migration -- turning SVN commits into Git commits for ``trunk`` (git-svn does this fine).  See: https://git-scm.com/book/en/v2/Git-and-Other-Systems-Migrating-to-Git
- [ ] Investigate to see if we can trim out older branches, and only leaving tags and trunk/master.
- [ ] Make the base branch "master" instead of trunk
- [ ] Push this 'staging' repo to GitHub, NOT under ``twisted/twisted``
- [ ] Create a staging Trac server
- [ ] In 'staging' Trac, install https://github.com/trac-hacks/trac-GitHub
- [ ] In 'staging' GitHub repo add the webhook to poke the 'staging' Trac
- [ ] Commit some things to the staging GitHub repo, make sure the staging trac picks them up, and it's propagated to Kenaan and such.

### Accounts ###
- [ ] Make sure that all users who have SVN commit access have a GitHub account which can commit to the Twisted repository on GitHub, #158

### Infrastructure ###
- [ ] Migrate SVN commit hooks to GitHub, #138, #139, #141
- [ ] Update all buildbots to get code from GitHub, #73, #141, #147
- [ ] Change Kenaan IRC bot to monitor GitHub, #137

### Documentation ###
- [ ] Update all wiki documentation to change all references to getting code from Subversion, to getting code from GitHub. , #159
- [ ] Update Release Engineering documentation for doing a release from GitHub, #156

### Migration schedule ###
- [ ] Pick a weekend where Amber isn't doing anything, send out warnings, queue up a ticket for testing
- [ ] Send e-mail one week before scheduled maintenance.
- [ ] Before the maintenance begins, send another HEADSUP e-mail.
- [ ] Disable commits to Subversion: http://stackoverflow.com/questions/2411122/how-to-freeze-entire-svn-repository-to-make-it-read-only
- [ ] Bring down ``svn.twistedmatrix.com``, and Trac for maintenance.
- [ ] Move the existing ``twisted/twisted`` repo, redo the format migration with most recent SVN trunk, push it up to ``twisted/twisted``.
- [ ] Install trac-GitHub as on the staging on the production trac, and set up the new ``twisted/twisted`` to connect to the production webhook.
- [ ] Merge the ticket queued up for testing, make sure production Trac knows about it.
- [ ] Bring Trac out of maintenance.
- [ ] Send HEADSUP e-mail saying that GitHub migration is done, #68
