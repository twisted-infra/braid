Plan A: AMBER'S SUPER SECRET AWESOME PLAN FOR MIGRATING TO GIT, GITHUB, AND WORLD LEADERSHIP
============================================================================================

Objectives of Plan A
--------------------

- Migrate our source code repository to Git.
- Make our contribution process easier
- Allow contributors to contribute code via GitHub


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
