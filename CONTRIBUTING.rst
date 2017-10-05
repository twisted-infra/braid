Contributing to the Twisted Infrastructure
##########################################

Here you should find the required information to get you started with working
at maintaining and developing the Twisted infrastructure.

Before pushing things into production you should give them a try on a staging
environment.

A VM managed using Vagrant is provided as a local staging environment.
While making changes make sure the changes still work on Vagrant.


style-notes
===========

Things that want to root want to be run with `sudo`, and files `put` with `use_sudo`.
When dealing with things that want to be run as other users, `run` should be
used, and a ssh connection as that user (with `settings(user='user')` or the like.
`braid.base.sshConfig` sets things up so anybody with root keys can log-in as any user in the `service` group.


Vagrant
=======

> [Vagrant](https://www.vagrantup.com/) 1.7+ is required to use the Vagrant image.

There is `Vagrantfile` provided with braid, that will set up a staging server.
It uses the address `172.16.255.140`.
There is a braid config named `vagrant` that connects to it by default using
the Vagrant private key.

```shell
# Start the VM
vagrant up

# In case you already have a VM, re-provision it using:
vagrant provision

# New VMs should be initialized using:
fab config.vagrant base.bootstrap

# Run the braid commands using:
fab config.vagrant COMMAND
```

The following ports are in use on the Vagrant VM, listed here for easy
discovery and to avoid conflicts:

* 80 - Twisted Web
* 8000 - Buildmaster redirection placeholder (port 80 in production)
* 8080 - Buildmaster WebStatus
* 9987 - Buildmaster slave listener
