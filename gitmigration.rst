Plan A: AMBER'S SUPER SECRET AWESOME PLAN FOR MIGRATING TO GIT, GITHUB, AND WORLD LEADERSHIP
============================================================================================

Objectives of Plan A
--------------------

- Migrate our source code repository to Git.
- Make our contribution process easier
- Allow contributors to contribute code via GitHub
- Migrate off Trac


Plan
----

Migration of repository to Git
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Git repository migration will simply be a format change, from SVN to Git, with little/no workflow changes (with the exception of typing `git` where `svn` was once used). This involves:

- Doing a Git -> SVN format migration -- turning SVN commits into Git commits for `trunk`
  - Potential tools are git-svn or ESR's reposurgeon (http://www.catb.org/~esr/reposurgeon/dvcs-migration-guide.html) -- reposurgeon seems to have better mapping, so it will give us a cleaner history
- Make the base branch "master"
- Converting the SVN commit triggers to Git `prerecieve` triggers
- Setting up a `git.twistedmatrix.com` with the smallest surface possible
- Install gitolite (http://gitolite.com/gitolite/gitolite.html#basic-use-case) so that we don't need to use icky UNIX accounts
- Add existing contribitors the gitolite
- Pointing Trac to the Git repo
- Make GitHub a mirror of `git.twistedmatrix.com/repos/Twisted.git`

After this, Twisted will not use SVN, and will use Git on self-hosted infrastructure. Release management changes are minimal, rather than git branches there will be tags.


Make our contribution process easier
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This makes some things more like GitHub, to ease the transition.

- Move Twisted into a src/ directory (https://hynek.me/articles/testing-packaging/)
- Make all builder configurations into tox configs (usable on Travis later)
- Make Buildbot build using Tox
- Configure gitolite to allow people going through the contribution process the ability to make branches, spin builders, but not merge to master
- Migrate the important parts of the Trac wiki to the Git repository/docs

After this, our self-hosted Git repo will be flexible enough to allow contributors going through the contributor acceptance process be able to make branches and spin builders, but not merge to trunk (only core will be able to do this).


Allow contributors to contribute code via GitHub
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This would make our code hosted by GitHub (with a self-hosted mirror, Just In Case).

- Set up Travis, for basic PR filtering, that runs Py2.7/3.3/3.4/3.5 tests + linters in the tox envs
- Change the prerecieve triggers into tests (eg. checking for a topfile)
- Write a bot so that committers + contribution process participants can say "please test", to run it on the multi-system Buildbot infra
- Write a bot so that contributors can associate PRs with a Trac ticket
- Write a plugin to allow Buildbot builds to show up on GitHub PRs as a status
- Change GitHub to be the primary, set git.twistedmatrix.com to mirror
- Change Trac to have direct links to the PRs?

After this, our self-hosted Git repo will be a mirror to the GitHub primary. Core contributors have the 'merge bit', and can merge PRs. All other contributors issue PRs from personal forks. People working to be in core have the ability to spin builders for their and other PRs.


Migrate off Trac
~~~~~~~~~~~~~~~~

According to correspondance with the GitHub team, migrating our tickets to GitHub Issues will not be possible in the near future:

    You're right -- only users with push access can add labels currently. We don't comment on product plans or timelines publicly, so I can't say if/when such a feature might be available. I do agree with you that it would be a very useful feature, though. I'll pass your feedback to the team working on issues to consider, but I wouldn't expect this to be implemented in the near future.

    In the meantime, there's perhaps a workaround you might consider. You could build an OAuth application and ask your contributors to sign in:

    https://developer.github.com/v3/oauth/

    That OAuth app would have a token stored internally from someone who has push access to the project (you might even create a special "machine" account for that purpose, which would never be removed from the project). When a contributor signs into the app, the app would list their issues and pull requests on the project and allow them to add labels to those via the API (using the internal token):

    https://developer.github.com/v3/issues/#edit-an-issue

    https://developer.github.com/v3/#authentication

    https://github.com/settings/tokens

    In other words, you would be exposing a single permission (editing the list of labels) from a user who has push access to the project to other users who do not have that access. And the way you would be doing that is a small webapp so that the token is kept secret. While the GitHub Web UI doesn't support your workflow regarding labels, you could use the API to build tools that do fit your workflow.


Plan B: LIKE RIPPING OFF A BANDAID, THE GITHUB MIGRATION IS INEVITABLE
======================================================================

This plan takes elements of A, but does it all on one go, with a direct SVN -> GitHub migration.

Objectives of Plan A
--------------------

- Migrate to GitHub.

Plan
----

Migrate to GitHub
~~~~~~~~~~~~~~~~~

- Doing a Git -> SVN format migration -- turning SVN commits into Git commits for `trunk`
  - Potential tools are git-svn or ESR's reposurgeon (http://www.catb.org/~esr/reposurgeon/dvcs-migration-guide.html) -- reposurgeon seems to have better mapping, so it will give us a cleaner history
- Make the base branch "master"
- Push this repo to GitHub
- Point Trac to the Git repo, synced with GitHub
- Point Buildbot to GitHub's repo
- Migrate the important parts of the Trac wiki to the Git repository/docs
- Move Twisted into a src/ directory (https://hynek.me/articles/testing-packaging/)
- Make all builder configurations into tox configs (usable on Travis later)
- Turn the old precommit triggers into tests (eg. checking for a topfile)
- Set up Travis, for basic PR filtering, that runs Py2.7/3.3/3.4/3.5 tests + linters in the tox envs
- Write a bot so that committers + contribution process participants can say "please test", to run it on the multi-system Buildbot infra
- Write a bot so that contributors can associate PRs with a Trac ticket
- Change Trac to have direct links to the PRs?
- Write a plugin to allow Buildbot builds to show up on GitHub PRs as a status
- Set up a Git mirror on our infra, Just In Case

This compresses many elements into one, but most of it should be locally testable, in virtual machines. Like a bandaid, it will have a long buildup but the actual pushing it to production will take a short amount of time.
