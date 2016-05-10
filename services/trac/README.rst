Trac
====

This is the configuration for twistedmatrix.com's trac installation.

It is adminstered using braid[1]. It is installed in ``/srv/trac`` as user trac.

It uses the following directories:

- ``~/config`` - This repository.
- ``~/config/trac-env`` - Trac environment
- ``~/config/htpasswd`` - Trac passwords
- ``~/bin`` - commands to start and stop the server
- ``~/log`` - log files
- ``~/run`` - pid files
- ``~/attachments`` - trac attachments
- ``~/twisted.git`` - checkout of Twisted.

It uses https://github.com/twisted-infra/twisted-trac-plugins, DefaultCCPlugin (from Trac Hacks SVN), trac-github (from PyPI), and spam-filter (from Trac SVN).

This currently depends on the binaries (message, ticket) from Kenaan (another braid service) living at ``/srv/kenaan/bin/*``.

A webhook from GitHub updates the repository at ``~/twisted.git`` and notifies trac via a pb-server run from the monitor script.
The GitHub webhook is configured at https://github.com/twisted/twisted/settings/hooks, with a payload URL of ``https://twistedmatrix.com/trac/github``.
More information about how the post-commit hook works is available in the `trac-github readme <https://github.com/trac-hacks/trac-github#post-commit-hook>`_.

The following fabric commands are available:

- ``install`` - Create user and install configuration.
- ``installTestData`` - Makes a blank database for basic testing.
- ``getGithubMirror:<reponame>`` - Get ``twisted/<reponame>`` from GitHub and put it at ``~/twisted.git``. It will be automatically updated by Trac afterwards.
- ``update`` - Updates the configuration and restarts the server.
- ``upgrade`` - Upgrades the Trac database.
- ``start`` - Start server.
- ``stop`` - Stop server.
- ``restart`` - Restart the server.
- ``giveAdmin:<user>`` - Gives super admin to the mentioned Trac user.
- ``dump:<dump-file>`` - Dump trac db and attachments
- ``restore:<dump-file>`` - Restore trac db and attachments
