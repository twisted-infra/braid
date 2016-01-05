Trac
====

This is the configuration for twistedmatrix.com's trac installation.

It is adminstered using braid[1]. It is installed in ``/srv/trac`` as user trac.

It uses the following directories:

- ~/config - This repository.
- ~/config/trac-env - Trac environment
- ~/config/htpasswd - Trac passwords
- ~/bin - commands to start and stop the server
- ~/log - log files
- ~/run - pid files
- ~/attachments - trac attachments
- ~/twisted.git - checkout of Twisted.
- ~/website - containst a checkout of t-web

It uses https://github.com/twisted-infra/twisted-trac-plugins, TracAccountManager (from PyPI), DefaultCCPlugin (from Trac Hacks SVN), trac-github (from PyPI), and spam-filter (from Trac SVN).

This currently depends on the binaries (message, ticket) from Kenaan (another braid service) living at ``/srv/kenaan/bin/*`` .

A post-commit hook from GitHub updates the repository at ``~/twisted.git`` and notifies trac via a pb-server run from the monitor script.
The GitHub post-commit hook is configured at https://github.com/twisted/twisted/settings/hooks, with a payload URL of ``https://twistedmatrix.com/trac/github``.

The following fabric commands are available:

- install - Create user and install configuration.
- update - Updates the configuration and restarts the server.
- start - Start server.
- stop - Stop server.
- restart - Restart the server.
- dump:<dump-file> - Dump trac db and attachments
- restore:<dump-file> - Restore trac db and attachments

[1] https://github.com/twisted-infra/braid
