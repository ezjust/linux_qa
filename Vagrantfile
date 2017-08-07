# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.provider "virtualbox" do |v|
    v.memory = 2048
    v.cpus = 2
  end
  config.vm.define "centos_7_x64" do |centos7|
    centos7.vm.box = "/home/mbugaiov/Documents/boxes/centos_7_x64.box"
    centos7.vm.network "public_network", bridge: "enp3s0", type: "dhcp"
    centos7.ssh.username = "vagrant"
    centos7.ssh.password = "vagrant"
  end
  config.vm.define "sles_12_x64" do |sles12|
    sles12.vm.box = "/var/lib/our_data/boxes/sles_12_x64.box"
    sles12.ssh.username = "vagrant"
    sles12.ssh.password = "vagrant"
  end
  config.vm.define "sles_11_x64" do |sles11|
    sles11.vm.box = "/var/lib/our_data/boxes/sles_11_x64.box"
    sles11.ssh.username = "vagrant"
    sles11.ssh.password = "vagrant"
  end
  config.vm.define "centos_6_x64" do |centos664|
    centos664.vm.box = "/home/mbugaiov/Documents/boxes/centos_6_x64.box"
    centos664.vm.network "public_network", bridge: "enp3s0", type: "dhcp"
    centos664.ssh.username = "vagrant"
    centos664.ssh.password = "vagrant"
  end

  config.vm.define "centos_6_x32" do |centos632|
    centos632.vm.box = "/var/lib/our_data/boxes/centos_6_x32.box"
    centos632.ssh.username = "vagrant"
    centos632.ssh.password = "vagrant"
  end
  config.vm.define "ubuntu_16.04_x64" do |ubuntu1604|
    ubuntu1604.vm.box = "/home/mbugaiov/Documents/boxes/ubuntu_16.04_x64.box"
    ubuntu1604.vm.network "public_network", bridge: "enp3s0", type: "dhcp"
    ubuntu1604.ssh.username = "vagrant"
    ubuntu1604.ssh.password = "vagrant"
  end
  config.vm.define "ubuntu_15.04_x32" do |ubuntu150432|
    ubuntu150432.vm.box = "/var/lib/our_data/boxes/ubuntu_15.04_x32.box"
    ubuntu150432.ssh.username = "vagrant"
    ubuntu150432.ssh.password = "vagrant"
  end
  config.vm.define "ubuntu_15.04_x64" do |ubuntu150464|
    ubuntu150464.vm.box = "/var/lib/our_data/boxes/ubuntu_15.04_x64.box"
    ubuntu150464.ssh.username = "vagrant"
    ubuntu150464.ssh.password = "vagrant"
  end
  config.vm.define "ubuntu_14.04_x32" do |ubuntu140432|
    ubuntu140432.vm.box = "/var/lib/our_data/boxes/ubuntu_14.04_x32.box"
    ubuntu140432.ssh.username = "vagrant"
    ubuntu140432.ssh.password = "vagrant"
  end
  config.vm.define "ubuntu_14.04_x64" do |ubuntu140464|
    ubuntu140464.vm.box = "/var/lib/our_data/boxes/ubuntu_14.04_x64.box"
    ubuntu140464.ssh.username = "vagrant"
    ubuntu140464.ssh.password = "vagrant"
  end
  config.vm.define "ubuntu_12.04_x32" do |ubuntu120432|
    ubuntu120432.vm.box = "/var/lib/our_data/boxes/ubuntu_12.04_x32.box"
    ubuntu120432.ssh.username = "vagrant"
    ubuntu120432.ssh.password = "vagrant"
  end
  config.vm.define "ubuntu_12.04_x64" do |ubuntu120464|
    ubuntu120464.vm.box = "/var/lib/our_data/boxes/ubuntu_12.04_x64.box"
    ubuntu120464.ssh.username = "vagrant"
    ubuntu120464.ssh.password = "vagrant"
  end
  config.vm.define "debian_8_x64" do |debian864|
    debian864.vm.box = "/home/mbugaiov/Documents/boxes/debian_8_x64.box"
    debian864.vm.network "public_network", bridge: "enp3s0", type: "dhcp"
    debian864.ssh.username = "vagrant"
    debian864.ssh.password = "vagrant"
  end
  config.vm.define "debian_7_x32" do |debian732|
    debian732.vm.box = "/var/lib/our_data/boxes/debian_7_x32.box"
    debian732.ssh.username = "vagrant"
    debian732.ssh.password = "vagrant"
  end
end

