Braid
#####

The main code for deploying the Twisted infrastructure into production.

A library of fabric stuff for deploying Twisted infrastrucutre.

It contains tools for deploying individual services.

The idea is that each individual service (e.g., t-names, www-data, trac,
buildbot) will have a dedicated fabfile that uses braid to deploy itself on a
given machine.

This README.rst describes how to use this tools and how to deploy.

See CONTRIBUTING.rst for info about how to run a staging server and develop
and maintain the code.


Currently Supported Services
============================

- amptrac
- t-names
- t-web
- buildbot (buildmaster)
- buildslave
- codespeed
- kenaan
- [hiscore](svn.twistedmatrix.com:infra/twisted-highscore)
- trac
- mailman


Server Dependencies
===================

braid currently assumes that it is being run against a Ubuntu 16.04.

It requires that the `universe` component be enabled, as well as `sudo`.

It only works on Python 2.7:

```shell
$ virtualenv -p python2.7 build
$ . build/bin/activate
$ pip install -e .
```

Usage Notes
===========

Fabric configuration is located at `braid/settings.py`
(don't be fooled by braid/config.py).

Some notable commands:

```shell
# Add keys from file to remote user
$ fab users.uploadKeyFile:<user>,<keyfile>
# Add keys from launchpad to remote user
$ fab users.uploadLaunchpadKeys:<user>[,<launchpadUser>]
```

```shell
# Install base packages, and ssh config
$ fab base.bootstrap
```

There are some tools to help specifying which machines to target.

```shell
# Install against dornkirk
$ fab config.production
```

There is a sample `testing.env` that can be put in ~/.config/braid/.
Any files matching *.env are accessible via
```shell
$ fab config.testing
```


Service configuration conventions
--------------------------------


### Directory structure ###

Each service has its own directory under `/srv`.

### Users, groups and privileges ###

Each service runs as its own system user and owns his root directory (i.e.  `/srv/<service>`).
Each service user has to be part of the `service` group.
Any ssh-key that can be used to authenticate as root can also be use to authenticate as any use in the `service` group.

### Init scripts ###
Most service provide scripts to start and stop the service in `~/bin`.

### Available tools ###

#### How to start/stop/restart services ####

Each service has its own Fabric namespace.
Actions are available as part of each namespace. For example, the `t-names` service can be started, stopped, and see the logs as follows::

    fab config.production t-names.start
    fab config.production t-names.stop
    fab config.production t-names.log
    ```

#### How to update existing services ####

Similarly as done for managing the running states, an `update` task lives in each service namespace. It can be run as follows::

    fab config.production t-names.update

Note that this will restart the service after updating.

#### How to install new services ####

A service which was just added to the fabfile can be installed by running its `install` task::

    fab config.production t-names.install

Note, however, that while the previous actions did not require root privileges, installing a new service requires to be able to `sudo` to `root`.
This is needed to create the necessary users, install additional packages and create the base environment.


Managing secrets
================

A private repository, protected by `git secret` is used to store the sensitive
data for the Twisted infrastructure.

The private repository is located at:
https://github.com/twisted-infra/twisted-infra-secret

Since `git secret` don't support submodules, you will need to clone the
`twisted-infra-secret` repo and `git secret reveal` it in a directory
which is a sibling of the braid base clone directory.

Make sure you pull and reveal the changes before running in production.
Make sure you push and hide your changes mode in production.
