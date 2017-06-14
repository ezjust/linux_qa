from __future__ import print_function, with_statement
import vagrant
from fabric.api import *


log_cm = vagrant.make_file_cm('deployment.log')
machine_name = "ubuntu_16.04_x64"




#@task
def start(machine_name):
    """Starts the specified machine using vagrant"""
    v = vagrant.Vagrant(out_cm=log_cm, err_cm=log_cm)
    print(v.up(vm_name=machine_name))
    v.up(vm_name=machine_name)
    with settings(host_string= v.user_hostname_port(vm_name=machine_name), key_filename = v.keyfile(vm_name=machine_name), disable_known_hosts = True):
        run("echo hello")
    v.destroy(vm_name=machine_name)


a = start(machine_name)