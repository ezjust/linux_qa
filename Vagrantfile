# -*- mode: ruby -*-
# vi: set ft=ruby :
#lfs_disk1 = './tmp/disk1.vdi'
#lfs_disk2 = './tmp/disk2.vdi'
#lfs_disk3 = './tmp/disk3.vdi'
#lfs_disk4 = './tmp/disk4.vdi'
#lfs_disk5 = './tmp/disk5.vdi'

Vagrant.configure("2") do |config|
  config.vm.provider "virtualbox" do |v|
    v.memory = 2048
    v.cpus = 2
    v.gui = false
    #unless File.exist?(lfs_disk1)
    #    v.customize ['createhd', '--filename', lfs_disk1, '--size', 10 * 1024]
    #end
    #v.customize ['storageattach', :id, '--storagectl', 'SATA Controller', '--port', 1, '--device', 0, '--type', 'hdd', '--medium', lfs_disk1]
    #unless File.exist?(lfs_disk2)
    #    v.customize ['createhd', '--filename', lfs_disk2, '--size', 10 * 1024]
    #end
    #v.customize ['storageattach', :id, '--storagectl', 'SATA Controller', '--port', 2, '--device', 0, '--type', 'hdd', '--medium', lfs_disk2]
    #unless File.exist?(lfs_disk3)
    #    v.customize ['createhd', '--filename', lfs_disk3, '--size', 10 * 1024]
    #end
    #v.customize ['storageattach', :id, '--storagectl', 'SATA Controller', '--port', 3, '--device', 0, '--type', 'hdd', '--medium', lfs_disk3]
    #unless File.exist?(lfs_disk4)
    #    v.customize ['createhd', '--filename', lfs_disk4, '--size', 10 * 1024]
    #end
    #v.customize ['storageattach', :id, '--storagectl', 'SATA Controller', '--port', 4, '--device', 0, '--type', 'hdd', '--medium', lfs_disk4]
    #unless File.exist?(lfs_disk5)
    #    v.customize ['createhd', '--filename', lfs_disk5, '--size', 10 * 1024]
    #end
    #v.customize ['storageattach', :id, '--storagectl', 'SATA Controller', '--port', 5, '--device', 0, '--type', 'hdd', '--medium', lfs_disk5]

  end

  config.vm.define "centos_7_x64" do |centos7|
    centos7.vm.box = "/home/mbugaiov/Documents/boxes/centos_7_x64.box"
    centos7.vm.network "public_network", bridge: "enp3s0", type: "dhcp"
    centos7.ssh.username = "vagrant"
    centos7.ssh.password = "vagrant"
  end
  config.vm.define "sles_12_x64" do |sles12|
    sles12.vm.box = "/home/mbugaiov/Documents/boxes/sles_12_x64.box"
    sles12.vm.network "public_network", bridge: "enp3s0", type: "dhcp"
    sles12.ssh.username = "vagrant"
    sles12.ssh.password = "vagrant"
  end
  config.vm.define "sles_10_x64" do |sles10|
    sles10.vm.box = "trueability/sles-12-sp2"
    sles10.vm.box_version = "20171101.11"
  end

  config.vm.define "debian_9_x64" do |debian9|
    debian9.vm.box = "/home/mbugaiov/Documents/boxes/debian_9_x64.box"
    debian9.vm.network "public_network", bridge: "enp3s0", type: "dhcp"
    debian9.ssh.username = "vagrant"
    debian9.ssh.password = "vagrant"
  end

  config.vm.define "sl_7_x64" do |sl7|
    sl7.vm.box = "/home/mbugaiov/Documents/boxes/sl_7_x64.box"
    sl7.vm.network "public_network", bridge: "enp3s0", type: "dhcp"
    sl7.ssh.username = "vagrant"
    sl7.ssh.password = "vagrant"
  end

  config.vm.define "sles_11_x64" do |sles11|
    sles11.vm.box = "/home/mbugaiov/Documents/boxes/sles_12_x64.box"
    sles11.vm.network "public_network", bridge: "enp3s0", type: "dhcp"
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
  config.vm.define "livecd" do |live|
    live.vm.box = "/home/mbugaiov/Documents/git/linux_qa/livecd.box"
    live.vm.network "public_network", bridge: "enp3s0", type: "dhcp"
    live.ssh.forward_x11 = true
    live.ssh.username = "vagrant"
    live.ssh.password = "vagrant"
  end

end

