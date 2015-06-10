# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

# Provision root account with the insecure Vagrant ssh key.
$root_ssh_authorized_keys = <<ENDMARKER
mkdir /root/.ssh
chmod 700 /root/.ssh
cp ~vagrant/.ssh/authorized_keys /root/.ssh
ENDMARKER

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # Every Vagrant virtual environment requires a box to build off of.
  config.vm.box = "ubuntu/precise64"
  config.vm.network :private_network, :ip => "172.16.255.140"
  # Default folder synchronization is disables as the host is managed using
  # fabric/braid.
  config.vm.synced_folder ".", "/vagrant", disabled: true

  # The only vagrant provisioning is to enable SSH access for root account.
  # After that provisioning is done using fabric/braid.
  config.vm.provision "shell",
    inline: $root_ssh_authorized_keys, privileged: true

end
