Buildbot
========

This is the configuration for buildbot.twistedmatrix.com's buildmaster.

It is installed in ``/srv/bb-master`` as user ``bb-master``.

It uses the following directories:

- ``~/config`` - This repository
- ``~/config/master`` - The buildbot configuration
- ``~/bin`` - commands to start and stop the server
- ``~/log`` - log files
- ``~/run`` - pid files
- ``~/data`` - buildbot data
- ``~/private`` - private configuration
- ``~/data/state.sqlite`` - buildbot's db
- ``~/data/build_products`` - built packages and build output

Note: http.log is located in ~/data

A webhook from GitHub notifies BuildBot of changes.
The GitHub webhook is configured at https://github.com/twisted/twisted/settings/hooks, with a payload URL of ``https://twistedmatrix.com/trac/github``, and will just send the ``push`` event.
More details about Buildbot's support of GitHub webhooks is available in the `Buildbot docs <http://docs.buildbot.net/latest/manual/cfg-wwwhooks.html#github-hook>`_.

The following fabric commands are available:

- ``install`` - Create user and install configuration.
- ``installTestData`` - install fake private configuration and db
  - This happens automatically if `installPrivateData` is set to False
    in the fabric environment.
- ``update`` - Updates Buildbot, the configuration, and restarts server
- ``updatefast`` - Updates the configuration and restart server
- ``updatePrivateData`` - Updates ``~/private``.
  - This happens automatically if ``installPrivateData`` is set
    in the fabric environment.
- ``start`` - Start server.
- ``stop`` - Stop server.
- ``restart`` - Restart the server.
