from __future__ import print_function, with_statement
from web_runner import *
from my_utils.system import SystemUtils
import vagrant
from fabric.api import *
from fabric.network import disconnect_all
import os
import re
import tarfile
import ConfigParser
import time
import subprocess
# from my_utils.web import WebAgent


log_cm = vagrant.make_file_cm('deployment.log')
configuration_log = open('configuration.log', 'a+')
installation_agent_log = open('installation_agent.log', 'a')
work_path = os.getcwd() + "/" #Returns current directory, where script is run.
box_work_path = "/home/vagrant"
tar_name = "linux_qa.tar"
config = work_path + "/cfg/vagrant_up.ini"
config_web = work_path + "config.ini"


class VagrantAutomation(SystemUtils, TestRunner):
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
            #print(output)
            return output

#@task
    def start_up(self):
        """Starts the specified machine using vagrant"""
        self.create_tar(work_path)
        v = vagrant.Vagrant(out_cm=log_cm, err_cm=log_cm)
        if self.vagrant_up:
            try:
                v.up(vm_name=self.box_distro_name)
            except Exception:
                time.sleep(10)
                try:
                    v.up(vm_name=self.box_distro_name)
                except Exception as E:
                    print(E)
                    list = []
                    command = "echo `ps axf | grep virtualbox | grep VBoxHead | awk {'print $1'}`"
                    for item in self.execute(cmd=command).split():
                        self.execute(cmd='sudo kill -9 ' + item) # kill of the pids - releted to the virtualbox machine. May affect not only Vagrant boxes.

                    try:
                        v.destroy() # try to destroy all machines. If the were no machines for destroing returns non-0 exit code. For this case we are using try, except block.
                    except Exception as e:
                        print(e)

                    try:
                        v.up(vm_name=self.box_distro_name)
                    except Exception:
                        raise Exception("I have no ability to start vagrant machine %s" % self.box_distro_name)


            self.write_log(message="\n Running test on the : %s \n" % self.box_distro_name)

            with settings(host_string= v.user_hostname_port(vm_name=self.box_distro_name), key_filename = v.keyfile(vm_name=self.box_distro_name), disable_known_hosts = True):
                try:
                    box_distro = self.box_distro_name.split('_')
                    box_distro_name = box_distro[0]
                    print("Install environment is in progress...")
                    if box_distro_name in ('ubuntu', 'debian'):
                        clean = "echo `ps -A | grep apt | awk '{print $1}'`"
                        result_clean = run(clean)
                        if len(result_clean) is not 0:
                            sudo(stderr=False, command='kill -9 ' + result_clean)
                        sudo("sed -i -e 's/zesty/artful/g' /etc/apt/sources.list", stdout=configuration_log)
                        sudo('apt-get update', stdout=configuration_log)
                        sudo('DEBIAN_FRONTEND=noninteractive apt-get install -y ' + self.deb_packages, stdout=configuration_log)
                    elif box_distro_name in ('rhel', 'centos', 'sl'):

                        def install_rhel_preparation():
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
                        try:
                            install_rhel_preparation()
                        except Exception as E:
                            print(E)
                            time.sleep(15)
                            install_rhel_preparation()

                    elif box_distro_name in ('sles', 'suse'):
                        #sudo('zypper rr 2', stdout=configuration_log, shell=False)
                        # Looks like the image of the SLES box already contains installed rapidrecovery-agent. Uninstall.
                        #print("Hello")
                        # there is bug in the non-interactive install on the
                        # SLES OS, when there is conflicts on some packages,
                        # you cannot avoid on by scripting in non-interactive mode.
                        #sudo('zypper -n update -y', stdout=configuration_log)
                        #print(self.sles_packages)
                        #print('zypper install -n ' + self.sles_packages)
                        sudo('zypper clean -M', stdout=configuration_log)
                        sudo('zypper ar http://download.opensuse.org/repositories/devel:/languages:/python/SLE_12_SP2/ python', stdout=configuration_log)
                        #sudo('zypper ar http://download.opensuse.org/tumbleweed/repo/oss/ oss')
                        sudo('zypper --no-gpg-checks install -n -y ' + self.sles_packages, stdout=configuration_log)
                        sudo('pip install ' + self.pip_packages,
                             stdout=configuration_log)


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
                        sudo('wget https://raw.github.com/mbugaiov/myrepo/master/configurator.sh')
                        sudo('chmod +x ./configurator.sh')
                        sudo('./configurator.sh --install --disk=/dev/sdb,/dev/sdc,/dev/sdd,/dev/sde,/dev/sdf', stdout=configuration_log)
                        run('lsblk')
                    if self.install_agent:
                        sudo(
                        'wget https://raw.github.com/mbugaiov/myrepo/master/agent_install.sh')
                        sudo('chmod +x ./agent_install.sh')
                        sudo('./agent_install.sh --install --branch=' + self.build_agent,
                        stdout=installation_agent_log)
                        try:
                            ipaddr = sudo("ip addr show | grep '10.10' | awk '{print $2}' | cut -d'/' -f1")
                            counter = 0
                            while "10.10." not in ipaddr and counter < 10:
                                time.sleep(5)
                                ipaddr = sudo(
                                    "ip addr show | grep '10.10' | awk '{print $2}' | cut -d'/' -f1")
                                counter = counter + 1
                            if "10.10." not in ipaddr:
                                raise Exception('Failed to determine IP of the vagrant machine')
                            else:
                                self.write_cfg(ipaddr=ipaddr)
                                time.sleep(5)
                                os.system("sudo /usr/bin/python2.7 web_runner.py")
                                print("Testing is completed")
                        except Exception:
                            pass

            finally:

                if self.destroy_vm:
                    print("destroing")
                    try:
                        v.destroy(vm_name=self.box_distro_name)
                    except Exception as e:
                        print(e)
                        disconnect_all()
                        v.destroy(vm_name=self.box_distro_name)
                        pass

                print("------------------------------------------------------------------------------------------------------------------"
                      "\n"
                      "\n"
                      "\n"
                      "------------------------------------------------------------------------------------------------------------------")


    def open_box_log(self):
        self.box_log_object = open(self.__logDir + VagrantAutomation.box_log, 'a')
        global TEST_VAR

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

    def save_vmname(self, vm=None, **kwargs):
        if vm is not None:
            config = ConfigParser.ConfigParser()
            config.optionxform = str
            config.readfp(open(config_web))
            config.set('web', 'os', vm)
            with open(config_web, 'w') as configfile:
                config.write(configfile)




if __name__ == '__main__':

    start = VagrantAutomation()
    start.read_cfg()
    start.clean_box_log()
    start.clean_installation_agent_log()
    start.clean_configuration_log()
    start.open_box_log()
    start.remove_log()

    for vm in start.os_list:
        print("VM NAME = ", vm)
        start.save_vmname(vm=vm)
        print(vm + " : executing....")
        start.write_in_box_log(vm + " tests are comleted:" + '\n')
        start.read_cfg(box_distro_name=vm)
        start.start_up()
        start.remove_archive()
        start.parse_box_log()
    if start.run_web:
        #start.parse_installation_agent_log()
        pass
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    with open('result.log') as f:
        for line in f:
            print(line)
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    start.close_log()


