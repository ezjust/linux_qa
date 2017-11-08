from __future__ import print_function, with_statement
import vagrant
from fabric.api import *
from fabric.network import disconnect_all
import os
import re
import tarfile
import ConfigParser
import time
import subprocess

log_cm = vagrant.make_file_cm('deployment.log')
configuration_log = open('configuration.log', 'a+')
installation_agent_log = open('installation_agent.log', 'a')
work_path = os.getcwd() + "/" #Returns current directory, where script is run.
box_work_path = "/home/vagrant"
tar_name = "linux_qa.tar"
config = work_path + "/cfg/vagrant_up.ini"
config_web = work_path + "config.ini"


class VagrantAutomation(object):
    box_distro_name = None
    os_list = []
    __logDir = 'Logs'
    box_log = '/box.log'
    box_log_object = None
    env.password = "vagrant"


    def write_cfg(self, ipaddr, **kwargs):
        config = ConfigParser.ConfigParser()
        config.optionxform = str
        config.readfp(open(config_web))
        config.set('web', 'ip', ipaddr)
        with open(config_web, 'w') as configfile:
            config.write(configfile)

    def read_cfg(self, **kwargs):
        self.cp = ConfigParser.ConfigParser()
        self.cp.readfp(open(config))
        self.deb_packages = self.cp.get('remote', 'deb_packages')
        self.rhel_packages = self.cp.get('remote', 'rhel_packages')
        self.pip_packages = self.cp.get('remote', 'pip_packages')
        self.sles_packages = self.cp.get('remote', 'sles_packages')
        self.os_list = re.split(' |\\n',
                                self.cp.get('host', 'box_distro_name'))
        if kwargs != {}:
            self.box_distro_name = kwargs['box_distro_name']
        self.cp.readfp(open(config_web))
        self.build_agent = self.cp.get('general', 'build_agent')
        self.destroy_vm = self.cp.getboolean('vagrant', 'destroy_vm')
        self.reload_vm = self.cp.getboolean('vagrant', 'reload_vm')
        self.run_web = self.cp.getboolean('general', 'run_web')
        self.run_test = self.cp.getboolean('general', 'run_test')
        self.run_configurator = self.cp.getboolean('general', 'run_configurator')
        self.install_agent = self.cp.getboolean('general', 'install_agent')
        self.vagrant_up = self.cp.getboolean('general', 'vagrant_up')
        # print(self.os_list)

    def create_tar(self, work_path):
        """Create archive from the place, where tests are run."""
        self.work_path = work_path
        self.tar_name = tar_name
        with tarfile.open(self.tar_name, "w") as tar:
            for name in os.listdir(self.work_path):
                tar.add(name)

    def execute(self, cmd=None):
        # type: (object) -> object
        if cmd is not None:
            self.cmd = cmd
            p = subprocess.Popen(self.cmd, shell=True,
                                     stdout=subprocess.PIPE,
                                     stdin=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
            # ((output, err), code)
            output, err = p.communicate()
            print(output)

#@task
    def start_up(self):
        """Starts the specified machine using vagrant"""
        self.create_tar(work_path)
        v = vagrant.Vagrant(out_cm=log_cm, err_cm=log_cm)
        if self.vagrant_up:
            try:
                v.up(vm_name=self.box_distro_name)
            except Exception:
                time.sleep(60)
                v.up(vm_name=self.box_distro_name)

            with settings(host_string= v.user_hostname_port(vm_name=self.box_distro_name), key_filename = v.keyfile(vm_name=self.box_distro_name), disable_known_hosts = True):
                try:
                    box_distro = self.box_distro_name.split('_')
                    box_distro_name = box_distro[0]
                    #v.up(vm_name=self.box_distro_name)

                    print("Install environment is in progress...")
                    if box_distro_name in ('ubuntu', 'debian'):
                        clean = "echo `ps -A | grep apt | awk '{print $1}'`"
                        result_clean = run(clean)
                        # print(result_clean)
                        # print(len(result_clean))
                        if len(result_clean) is not 0:
                            sudo(stderr=False, command='kill -9 ' + result_clean)
                        sudo('apt-get update', stdout=configuration_log)
                        sudo('DEBIAN_FRONTEND=noninteractive apt-get install -y ' + self.deb_packages, stdout=configuration_log)
                    elif box_distro_name in ('rhel', 'centos', 'sl'):
                        # sudo('mv /usr/bin/python /usr/bin/python2.6_old')
                        # sudo('ln -s /usr/bin/python2.7 /usr/bin/python')
                        sudo('yum update -y', stdout=configuration_log)
                        sudo('yum install -y ' + self.rhel_packages, stdout=configuration_log)
                        sudo('yum --disablerepo=epel -y update  ca-certificates', stdout=configuration_log)
                        sudo('yum install -y ' + self.rhel_packages, stdout=configuration_log)
                        sudo('wget https://bootstrap.pypa.io/get-pip.py', stdout=configuration_log)
                        sudo('/usr/bin/python2.7 get-pip.py', stdout=configuration_log)
                        sudo('pip install --upgrade pip', stdout=configuration_log)
                        if box_distro[1] in ('6'):
                            sudo('/usr/bin/python2.7 /usr/local/bin/pip2.7 install ' + self.pip_packages, stdout=configuration_log)
                        else: sudo('pip install ' + self.pip_packages, stdout=configuration_log)
                    elif box_distro_name in ('sles', 'suse'):
                        #sudo('zypper rr 2', stdout=configuration_log, shell=False)
                        # Looks like the image of the SLES box already contains installed rapidrecovery-agent. Uninstall.
                        print("Hello")
                        # there is bug in the non-interactive install on the
                        # SLES OS, when there is conflicts on some packages,
                        # you cannot avoid on by scripting in non-interactive mode.
                        #sudo('zypper -n update -y', stdout=configuration_log)
                        print(self.sles_packages)
                        print('zypper install -n ' + self.sles_packages)
                        sudo('zypper clean -M')
                        sudo('zypper ar http://download.opensuse.org/repositories/devel:/languages:/python/SLE_12_SP2/ python')
                        #sudo('zypper ar http://download.opensuse.org/tumbleweed/repo/oss/ oss')
                        sudo('zypper --no-gpg-checks install -n -y ' + self.sles_packages)


                    sudo('uname -r')

                except Exception as e:
                    print("Exceptions has been received. Skipped, proceeding for the next OS.")
                    print(e)
                    pass


            if self.reload_vm:
                try:
                    print("Reloading machine")
                    v.reload(vm_name=self.box_distro_name)
                except Exception as e:
                    print(e)
                    disconnect_all()
                    v.reload(vm_name=self.box_distro_name)
                    pass

        with settings(host_string= v.user_hostname_port(vm_name=self.box_distro_name), key_filename = v.keyfile(vm_name=self.box_distro_name), disable_known_hosts = True):
            try:
                sudo('uname -r')
                if self.run_test:
                    put(work_path + tar_name, box_work_path + "/" + tar_name,
                        use_sudo=True)
                    #                run("chmod +x " + box_work_path + "/" + tar_name)
                    run("tar -xf " + box_work_path + "/" + tar_name, stdout=configuration_log)
                    run("cd " + box_work_path, stdout=configuration_log)
                    run("sudo /usr/bin/python2.7 test_main.py")

                if self.run_web:
                    if self.run_configurator:
                        sudo('wget --user=mbugaiov --password=201988 https://raw.github.com/mbugaiov/myrepo/master/configurator.sh')
                        sudo('chmod +x ./configurator.sh')
                        sudo('./configurator.sh --create /dev/sdb,/dev/sdc,/dev/sdd,/dev/sde,/dev/sdf', stdout=configuration_log)
                        run('lsblk')
                    if self.install_agent:
                        sudo(
                        'wget --user=mbugaiov --password=201988 https://raw.github.com/mbugaiov/myrepo/master/agent_install.sh')
                        sudo('chmod +x ./agent_install.sh')
                        sudo('./agent_install.sh --install ' + self.build_agent,
                         stdout=installation_agent_log)
                        #ipaddr = sudo(
                        #"ifconfig | grep '10.10' | awk '{print $2}' | sed 's/.*://'")
                        ipaddr = sudo("ip addr show | grep '10.10' | awk '{print $2}' | cut -d'/' -f1")
                        self.write_cfg(ipaddr=ipaddr)
                    os.system("sudo /usr/bin/python2.7 web_runner.py")

                print("Testing is completed")


            finally:

                if self.destroy_vm:
                    print("destroing")
                    v.destroy(vm_name=self.box_distro_name)
                print("------------------------------------------------------------------------------------------------------------------"
                      "\n"
                      "\n"
                      "\n"
                      "------------------------------------------------------------------------------------------------------------------")


    def open_box_log(self):
        self.box_log_object = open(self.__logDir + VagrantAutomation.box_log, 'a')

    def clean_box_log(self):
        if os.path.isfile(self.__logDir + VagrantAutomation.box_log):
            os.remove(self.__logDir + VagrantAutomation.box_log)

    def clean_installation_agent_log(self):
        if os.path.isfile("installation_agent.log"):
            os.remove("installation_agent.log")

    def clean_configuration_log(self):
        if os.path.isfile("configuration.log"):
            os.remove("configuration.log")

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

    def parse_installation_agent_log(self):
        with open("installation_agent.log", 'r') as test_log:
            words = ["Failed", "Error"]
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
    start.clean_installation_agent_log()
    start.clean_configuration_log()

    start.open_box_log()

    for vm in start.os_list:
        print(vm + " : executing....")
        start.write_in_box_log(vm + " tests are comleted:" + '\n')
        start.read_cfg(box_distro_name=vm)
        start.start_up()
        start.remove_archive()
        start.parse_box_log()
    if start.run_web:
        start.parse_installation_agent_log()





