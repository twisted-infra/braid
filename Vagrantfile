# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  config.vm.synced_folder ".", "/vagrant", disabled: true
  config.vm.network :forwarded_port, guest: 22, host: 2222, id: "ssh", disabled: true

  config.vm.provider "virtualbox" do |v|
      v.cpus = 1
      v.memory = 2048
  end

  config.vm.define "dornkirk-staging" do |box|
  # Every Vagrant virtual environment requires a box to build off of.
    box.vm.box = "ubuntu/precise64"
    box.vm.network :private_network, :ip => "172.16.255.140"
    box.vm.network "forwarded_port", guest: 22, host: 2522
  end

  # The only vagrant provisioning is to enable SSH access for root account.
  # After that provisioning is done using fabric/braid.
  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "provisioning/playbook.yml"
    ansible.extra_vars = { ansible_ssh_user: 'vagrant'}
  end

end
