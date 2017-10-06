# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"


# Provision root account by copying the ssh key from the default user.    
$root_ssh_authorized_keys = <<ENDMARKER   
mkdir -p /root/.ssh    
cp /home/ubuntu/.ssh/authorized_keys /root/.ssh
chmod -R 700 /root/.ssh    
ENDMARKER

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  config.vm.synced_folder ".", "/vagrant", disabled: true

  config.vm.provider "virtualbox" do |v|
      v.cpus = 1
      v.memory = 2048
  end

  config.vm.define "dornkirk-staging" do |box|
  # Every Vagrant virtual environment requires a box to build off of.
    box.vm.box = "ubuntu/xenial64"
    box.vm.network :private_network, :ip => "172.16.255.140"
  end

  # The only vagrant provisioning is to enable SSH access for root account by
  # copying the 
  # The actual provisioning is done outside of vagrant using fabric/braid.
  config.vm.provision :shell, inline: $root_ssh_authorized_keys

end
