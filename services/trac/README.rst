Trac
====

This is the configuration for twistedmatrix.com's Trac installation.

It requires that the `t-web` service to be started::

    fab t-web.install
    fab t-web.start

It is installed in ``/srv/trac`` as user `trac`.

Inside the `t-web` service, it is available at `http://server.name/trac/`

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

Use `fab -l` to check the available commands.

Trac is available inside the Vagrant VM at http://172.16.255.140/trac


GitHub Login
------------

First create a an OAuth Application or update the existing one at
https://github.com/organizations/twisted/settings/applications

Set/update the public client ID inside trac-env/conf/trac.ini

Manually save the file as user trac  (mode 600) in secrets/secret.txt
