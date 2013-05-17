A very work-in-progress library of fabric stuff for deploying twisted
infrastrucutre. The immeidate goal is to be able to redeploy everything from
cube onto dornkirk.

This package is a library of tools for deploying individual services. It also
currently contains a fabfile for global configuration of dornkirk.

The idea is that each individual service (e.g., t-names, www-data, trac,
buildbot) will have a configuration repo with a fabfile that uses braid to
deploy itself on a given machine.


Currently Supported Services
============================

- [t-names](https://github.com/twisted-infra/t-names)
- [t-web](https://github.com/twisted-infra/t-web)
- [buildbot](https://github.com/twisted-infra/twisted-buildbot-configuration)
- [diffresource](https://code.launchpad.net/~tom.prince/twisted-trac-integration/braided-diffresource)
- [kenaan](https://github.com/twisted-infra/kenaan)
- [hiscore](svn.twistedmatrix.com:infra/twisted-highscore)
- [trac](https://github.com/twisted-infra/trac-config)
- [mailman](https://github.com/twisted-infra/mailman-config)

Usage Notes
===========

# Get the code
$ git clone https://github.com/twisted-infra/braid
# Get the configurations for each service.
# This will clone all the repos in to service/*
$ cd braid
$ git submodule update --init

Some notable commands:

# Add keys from file to remote user
$ fab users.uploadKeyFile:<user>,<keyfile>
# Add keys from launchpad to remote user
$ fab users.uploadLaunchpadKeys:<user>[,<launchpadUser>]

# Install base packages, and ssh config
$ fab base.bootstrap

There are some tools to help specifying which machines to target.

# Install against dornkirk
$ fab config.production

There is a sample `testing.env` that can be put in ~/.config/braid/. Any files matching *.env
are accessible via
$ fab config.testing



style-notes
===========
Things that want to root want to be run with `sudo`, and files `put` with
`use_sudo`. When dealing with things that want to be run as other users,
`run` should be used, and a ssh connection as that user (with
`settings(user='user')` or the like. `braid.base.sshConfig` sets things up so
anybody with root keys can log-in as any user in the `service` group.
