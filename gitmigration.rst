LIKE RIPPING OFF A BANDAID, THE GITHUB MIGRATION IS INEVITABLE
===============================================================

Move to GitHub(r)(tm)(pat pending). This involves JUST moving to GitHub, not accepting PRs.

Objectives
----------

- Replace the SVN primary code repo with a GitHub-hosted Git repo.
- Migrate Trac from reading the SVN repo to reading GitHub one.
- Set up logging in with GitHub.

Plan
----

1. Do a Git -> SVN format migration -- turning SVN commits into Git commits for ``trunk`` (git-svn does this fine). Investigate trimming everything but tags and trunk/master.
2. Make the base branch "master" (because everything assumes that these days)
3. Push this 'staging' repo to GitHub, NOT under ``twisted/twisted``
4. In a 'staging' Trac, install https://github.com/trac-hacks/trac-github, and then add the webhook that trac-github gives us to the staging repo)
5. Commit some things to the staging github repo, make sure the staging trac picks them up, and it's propagated to Kenaan and such.
6. Fix any issues with Kenaan/buildbot/other bits that used to assume SVN, SVN triggers, or SVN-esque branch names.
   6.1. Make sure logging in with GitHub works.
   6.2. Replace the SVN pre-commit triggers with a tox builder.
   6.3. Make sure Kenaan puts sane things in IRC.
7. Do a few common workflow things - make a branch, make sure it is added to the ticket, add some commits with 'refs' which will add messages to the ticket, merge it to master and make sure the ticket is closed. Revert the merge and make sure the ticket is re-opened.
8. Pick a weekend where Amber isn't doing anything, send out warnings, queue up a ticket for testing
9. Bring down ``svn.twistedmatrix.com``, and Trac for maint. on that weekend.
10. Move the existing ``twisted/twisted`` repo, redo the format migration with most recent SVN trunk, push it up to ``twisted/twisted``.
11. Install trac-github as on the staging on the prod trac, and set up the new ``twisted/twisted`` to connect to the prod webhook.
12. Merge the ticket queued up for testing, make sure prod Trac knows about it
13. Bring Trac out of maint, send out an announcement saying 'hey github is a thing now'.
