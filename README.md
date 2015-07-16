A very work-in-progress library of fabric stuff for deploying twisted infrastrucutre.
The immeidate goal is to be able to redeploy everything from cube onto dornkirk.

This package is a library of tools for deploying individual services.
It also currently contains a fabfile for global configuration of dornkirk.

The idea is that each individual service (e.g., t-names, www-data, trac,
buildbot) will have a configuration repo with a fabfile that uses braid to
deploy itself on a given machine.


Currently Supported Services
============================

- amptrac
- t-names
- [t-web](https://github.com/twisted-infra/t-web)
- buildbot
- codespeed
- [diffresource](https://github.com/twisted-infra/diffresource)
- kenaan
- [hiscore](svn.twistedmatrix.com:infra/twisted-highscore)
- [trac](https://github.com/twisted-infra/trac-config)
- [mailman](https://github.com/twisted-infra/mailman-config)

Server Dependencies
===================
braid currently assumes that it is being run against a ubuntu server (precise).

It requires that the `universe` component be enabled, as well `sudo`.

Usage Notes
===========

```shell
# Get the code
$ git clone https://github.com/twisted-infra/braid
# Get the configurations for each service.
# This will clone all the repos in to service/*
$ cd braid
$ git submodule update --init
```

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

Each service has its own Fabric namespace. Actions are available as part of each namespace. For example, the `dns` service can be started, stopped,  and restarted as follows:

```shell
fab dns.start
```

```shell
fab dns.stop
```

```shell
fab dns.restart
```

#### How to update existing services ####

Similarly as done for managing the running states, an `update` task lives in each service namespace. It can be run as follows:

```shell
fab dns.update
```

Note that this will restart the service after updating.

#### How to install new services ####

A service which was just added to the fabfile can be installed by running its `install` task:

```shell
fab dns.install
```

Note, however, that while the previous actions did not require root privileges, installing a new service requires to be able to `sudo` to `root`.
This is needed to create the necessary users, install additional packages and create the base environment.


style-notes
===========
Things that want to root want to be run with `sudo`, and files `put` with `use_sudo`.
When dealing with things that want to be run as other users, `run` should be
used, and a ssh connection as that user (with `settings(user='user')` or the like.
`braid.base.sshConfig` sets things up so anybody with root keys can log-in as any user in the `service` group.


Vagrant
=======

There is `Vagrantfile` provided with braid, that will setup a staging sever.
It uses the address `172.16.255.140`, and there is a braid config named `vagrant` that connects to it by default.

```shell
# Get the required base OS image if you don't have it yet.
vagrant box add precise64 http://files.vagrantup.com/precise64.box
# Start the VM
vagrant up
# With ssh-aget add private key used by Vagrant
ssh-add ~/.vagrant.d/insecure_private_key
fab config.vagrant COMMAND
# Or without ssh-agent
fab -i ~/.vagrant.d/insecure_private_key config.vagrant COMMAND
```
