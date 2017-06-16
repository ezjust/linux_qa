from __future__ import print_function, with_statement
import vagrant
from fabric.api import *
import os
import re
import tarfile
import ConfigParser

log_cm = vagrant.make_file_cm('deployment.log')
machine_name = "ubuntu_16.04_x64"
work_path = os.getcwd() + "/" #Returns current directory, where script is run.
box_work_path = "/home/vagrant"
tar_name = "linux_qa.tar"
config = work_path + "/cfg/vagrant_up.ini"


class VagrantAutomation(object):
    box_distro_name = None
    os_list = []
    __logDir = 'Logs'
    box_log = '/box.log'
    box_log_object = None

    def read_cfg(self, **kwargs):
        self.cp = ConfigParser.ConfigParser()
        self.cp.readfp(open(config))
        self.deb_packages = self.cp.get('remote', 'deb_packages')
        self.rhel_packages = self.cp.get('remote', 'rhel_packages')
        self.sles_packages = self.cp.get('remote', 'sles_packages')
        self.os_list = re.split(' |\\n',
                                self.cp.get('host', 'box_distro_name'))
        if kwargs != {}:
            self.box_distro_name = kwargs['box_distro_name']
        print(self.os_list)

    def create_tar(self, work_path):
        """Create archive from the place, where tests are run."""
        self.work_path = work_path
        self.tar_name = tar_name
        with tarfile.open(self.tar_name, "w") as tar:
            for name in os.listdir(self.work_path):
                tar.add(name)

#@task
    def start_up(self):
        """Starts the specified machine using vagrant"""
        self.create_tar(work_path)
        v = vagrant.Vagrant(out_cm=log_cm, err_cm=log_cm)

        v.up(vm_name=self.box_distro_name)
        with settings(host_string= v.user_hostname_port(vm_name=self.box_distro_name), key_filename = v.keyfile(vm_name=self.box_distro_name), disable_known_hosts = True):
            try:
                box_distro = self.box_distro_name.split('_')
                box_distro_name = box_distro[0]
                #v.up(vm_name=self.box_distro_name)

                print("Install environment is in progress...")
                if box_distro_name in ('ubuntu', 'debian'):
                    clean = "`ps -A | grep apt | awk '{print $1}'`"
                    sudo('kill -9 ' + clean)
                    sudo('apt-get update')
                    sudo('apt-get install -y ' + self.deb_packages)
                elif box_distro_name in ('rhel', 'centos'):
                    sudo('yum update')
                    sudo('yum install -y ' + self.rhel_packages)
                elif box_distro_name in ('sles', 'suse'):
                    sudo('zyppre update -y')
                    sudo('zypper install -y ', + self.sles_packages)
                print("Done")
                put(work_path + tar_name, box_work_path + "/" + tar_name, use_sudo=True)
#                run("chmod +x " + box_work_path + "/" + tar_name)
                run("tar -xf " + box_work_path + "/" + tar_name)
                run("cd " + box_work_path)
                run("sudo python test_main.py")
            finally:
                pass
                v.destroy(vm_name=self.box_distro_name)



    def open_box_log(self):
        self.box_log_object = open(self.__logDir + VagrantAutomation.box_log, 'a')

    def clean_box_log(self):
        if os.path.isfile(self.__logDir + VagrantAutomation.box_log):
            os.remove(self.__logDir + VagrantAutomation.box_log)

    def write_in_box_log(self, message):
        self.message = message
        self.box_log_object.write(self.message)

    def parse_box_log(self):
        with open(self.__logDir + VagrantAutomation.box_log, 'r') as test_log:
            words = ["OK", "FAIL", "completed", "Executing"]
            for line in test_log:
                if any(s in line for s in words):
                    line = re.sub(r'.*out:', '', line)
                    print(line)

    def remove_archive(self):
        os.remove(work_path + tar_name)


if __name__ == '__main__':

    start = VagrantAutomation()
    start.read_cfg()
    start.clean_box_log()
    start.open_box_log()
    for vm in start.os_list:
        print(vm + " : executing....")
        start.write_in_box_log(vm + " tests are comleted:" + '\n')
        start.read_cfg(box_distro_name=vm)
        start.start_up()
        start.remove_archive()
    start.parse_box_log()
    start.remove_archive()




