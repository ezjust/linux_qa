from __future__ import print_function, with_statement
from web_runner import *
from my_utils.system import SystemUtils, retry_call
import vagrant
from fabric.api import *
from fabric.network import disconnect_all
import logging
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
    testing_result = None
    cp = ConfigParser.ConfigParser()
    #logging.raiseExceptions = False

    def write_cfg(self, ipaddr, **kwargs):
        config = ConfigParser.ConfigParser()
        config.optionxform = str
        config.readfp(open(config_web))
        config.set('web', 'ip', ipaddr)
        with open(config_web, 'w') as configfile:
            config.write(configfile)

    def read_cfg(self, **kwargs):

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
        self.multiprocess = self.cp.getboolean('general', 'multiprocess')
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
    #@parallel(pool_size=3)   # Testing an ability to run tasks in parallel
    def start_up(self):
        """Starts the specified machine using vagrant"""
        #self.create_tar(work_path)
        v = vagrant.Vagrant(out_cm=log_cm, err_cm=log_cm)

        # below option prevents pramiko transport error. They appears in paramiko==2.4.1 version. Current paramiko==2.2.1
        logging.basicConfig()
        paramiko_logger = logging.getLogger("paramiko.transport")
        paramiko_logger.disabled = True

        box_distro = self.box_distro_name.split('_')
        box_distro_name = box_distro[0]

        @retry_call(2)
        def prepare_deb():
            try:
                clean = "echo `ps -A | grep apt | awk '{print $1}'`"
                result_clean = run(clean)
                if len(result_clean) is not 0:
                    sudo(stderr=False, command='kill -9 ' + result_clean)
                sudo("sed -i -e 's/zesty/artful/g' /etc/apt/sources.list", stdout=configuration_log)
                sudo('apt-get update', stdout=configuration_log)
                sudo('DEBIAN_FRONTEND=noninteractive apt-get install -y ' + self.deb_packages, stdout=configuration_log)
                return True # this key is needed by the retry_call
            except Exception as e:
                print('Got exception')
                print(e)
                return False # this key is needed by the retry_call


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
                        v.destroy(vm_name=self.box_distro_name) # try to destroy all machines. If the were no machines for destroing returns non-0 exit code. For this case we are using try, except block.
                    except Exception as e:
                        print(e)

                    try:
                        v.up(vm_name=self.box_distro_name)
                    except Exception:
                        raise Exception("I have no ability to start vagrant machine %s" % self.box_distro_name)

            #self.write_log(message="\n Running test on the : %s \n" % self.box_distro_name)
            # added: timeout=30, connection_attempts=5, no_agent=True, allow_agent=False,look_for_keys=False, warn_only=True

            with settings(timeout=30, connection_attempts=5, no_agent=True, allow_agent=False,look_for_keys=False, host_string= v.user_hostname_port(vm_name=self.box_distro_name), key_filename = v.keyfile(vm_name=self.box_distro_name), disable_known_hosts = True, warn_only=True):
                try:
                    print("Install environment is in progress...")
                    if box_distro_name in ('ubuntu', 'debian'):

                        try:
                            prepare_deb()
                        except Exception as e:
                            print(e)
                            time.sleep(10)
                            print('Retry of the deb_preparation() installation')
                            prepare_deb()

                    elif box_distro_name in ('rhel', 'centos', 'sl', 'oracle'):
                        def install_rhel_preparation():
                            if box_distro_name is ('oracle_69_x64'):
                                exit(0)
                                sudo('wget http://vault.centos.org/6.9/extras/Source/SPackages/centos-release-scl-rh-2-3.el6.centos.src.rpm', stdout=configuration_log)
                                sudo('rpm -i centos-release-scl-rh-2-3.el6.centos.src.rpm', stdout=configuration_log)
                                sudo('yum install -y yum-utils', stdout=configuration_log)
                                sudo('yum-config-manager --enable "Software Collection Library release 2.3 packages for Oracle Linux 6 (x86_64)"', stdout=configuration_log)
                                sudo('yum install -y python27', stdout=configuration_log)
                                #run('scl enable python27 bash')
                                sudo('scl enable python27 "easy_install-2.7 pip"', stdout=configuration_log)
                                sudo('ln -s `which python` /usr/bin/python2.7', stdout=configuration_log)
                                sudo('echo ln -s `which python` /usr/bin/python2.7 >> /etc/rc.local', stdout=configuration_log)
                            else:
                                sudo('yum update -y', stdout=configuration_log)
                                sudo('yum install -y ' + self.rhel_packages, stdout=configuration_log)
                                sudo('yum --disablerepo=epel -y update  ca-certificates', stdout=configuration_log)
                                sudo('yum install -y ' + self.rhel_packages, stdout=configuration_log)
                                sudo('wget https://bootstrap.pypa.io/get-pip.py', stdout=configuration_log)
                                sudo('/usr/bin/python2.7 get-pip.py', stdout=configuration_log)
                                sudo('pip install --upgrade pip', stdout=configuration_log)
                            if box_distro[1] in ('6') and box_distro_name in ('rhel', 'centos', 'sl'):
                                sudo('/usr/bin/python2.7 /usr/local/bin/pip2.7 install ' + self.pip_packages, stdout=configuration_log)
                            else: sudo('pip install ' + self.pip_packages, stdout=configuration_log)
                        try:
                            install_rhel_preparation()
                        except Exception as E:
                            print(E)
                            time.sleep(15)
                            print('Retry of the rhel_preparation() installation')
                            install_rhel_preparation()
                            pass

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
                        try:
                            sudo('zypper clean -M', stdout=configuration_log)
                            sudo("zypper repos | grep SP2 && sudo zypper repos | grep SP2 | awk {'print $3'} | xargs sudo zypper rr || echo 'No repository for SP2 was found. Skipped.'")
                            sudo('zypper ar http://download.opensuse.org/repositories/devel:/languages:/python/SLE_12_SP2/ python', stdout=configuration_log)

                            '''For the SLES 11 SP3 the valid link is :
                            sudo zypper ar http://ftp.gwdg.de/pub/linux/misc/packman/suse/11.3/ packman
                            '''

                            #sudo('zypper ar http://download.opensuse.org/tumbleweed/repo/oss/ oss')
                            sudo('zypper --no-gpg-checks install -n -y ' + self.sles_packages, stdout=configuration_log)
                            sudo('pip install ' + self.pip_packages, stdout=configuration_log)
                            sudo('pip install --upgrade pyOpenSSL')
                        except Exception as E:
                            print(E)
                            pass


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
                    #disconnect_all()
                    try:
                        v.reload(vm_name=self.box_distro_name)
                    except Exception as e:
                        print(e)
                        print('Addition reload did not fix the issue.')
                        pass

        with settings(host_string= v.user_hostname_port(vm_name=self.box_distro_name), key_filename = v.keyfile(vm_name=self.box_distro_name), disable_known_hosts = True):
            try:
                '''The case, when reload was applied, there is still chanse apt will be running by the system update'''
                if self.reload_vm:
                    if box_distro_name in ('ubuntu', 'debian'):
                        prepare_deb()

                sudo('uname -r')
                run('[ -f ~/.bashrc ] && sudo echo export LANG=en_US.utf8 >> ~/.bashrc; source ~/.bashrc || echo "No ~/.bashrc file was found. Skipped."')   # set the language to english for all machines.
                if self.run_test:
                    try:
                        self.create_tar(work_path)
                        put(work_path + tar_name, box_work_path + "/" + tar_name,
                            use_sudo=True)
                        #                run("chmod +x " + box_work_path + "/" + tar_name)
                        run("tar -xf " + box_work_path + "/" + tar_name, stdout=configuration_log)
                        run("cd " + box_work_path, stdout=configuration_log)
                        file_to_write = 'Logs/Log.log'
                        run("echo Running tests on the : %s >> %s" % (self.box_distro_name, file_to_write))
                        run('whoami')
                        run("/usr/bin/python2.7 test_main.py")
                        self.clean_log(name='/tmp/Log.log')   #'/tmp/Log.log'
                        get('Logs/Log.log', '/tmp/Log.log')   #'/tmp/Log.log'
                        with open('/tmp/Log.log', "r") as input:    #'/tmp/Log.log'
                            with open("result.log", 'a+') as output:
                                for line in input:
                                    output.write(line)
                    except Exception as e:
                        print(e)
                        self.testing_result = False

                if self.run_web:
                    if self.run_configurator:
                        sudo('wget https://raw.github.com/mbugaiov/linux-qa-scripts/master/configurator.sh')
                        sudo('chmod +x ./configurator.sh')
                        sudo('./configurator.sh --install --disk=/dev/sdb,/dev/sdc,/dev/sdd,/dev/sde,/dev/sdf', stdout=configuration_log)
                        run('lsblk')
                    if self.install_agent:
                        sudo(
                        'wget https://raw.github.com/mbugaiov/linux-qa-scripts/master/agent_install.sh')
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
                                os.system("/usr/bin/python2.7 web_runner.py")
                                print("Testing is completed")
                        except Exception:
                            self.testing_result = False
                            pass
            except Exception as e:
                print(e)
                print("Got Exception in last block. Going to destroy vm %s", self.box_distro_name)
                pass

            finally:

                if self.destroy_vm:
                    print("destroing")
                    try:
                        v.destroy(vm_name=self.box_distro_name)
                    except Exception as e:
                        print('disconnect_all() will be called')
                        print(e)
                        disconnect_all()
                        v.destroy(vm_name=self.box_distro_name)
                        pass

                print("------------------------------------------------------------------------------------------------------------------"
                      "\n"
                      "\n"
                      "\n"
                      "------------------------------------------------------------------------------------------------------------------")

        if self.testing_result is False:
            raise Exception('Failed test execution')

    def open_box_log(self):
        self.box_log_object = open(self.__logDir + VagrantAutomation.box_log, 'a')
        global TEST_VAR

    def clean_box_log(self):
        if os.path.isfile(self.__logDir + VagrantAutomation.box_log):
            os.remove(self.__logDir + VagrantAutomation.box_log)

    def clean_log(self, name):
        if os.path.isfile(name):
            os.remove(name)

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
        if os.path.isfile(work_path + tar_name):
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
    from datetime import datetime
    print('The start time is: ', datetime.now())
    from multiprocessing import Process, Queue, Pipe, Pool
    import traceback
    start = VagrantAutomation()
    start.read_cfg()
    start.clean_box_log()
    start.clean_log(name='installation_agent.log')
    start.clean_log(name='configuration.log')
    start.clean_log(name='result.log')
    start.clean_log(name='/tmp/Log.log')
    start.clean_log(name='Logs/Log.log')
    start.open_box_log()
    #start.remove_log()

    # config = ConfigParser.ConfigParser()
    # config.optionxform = str
    # config.readfp(open(config_web))
    def test(vm):
        '''The function, which needs to be run for one instance to complete testing.
        We will use flags to run multiprocess for the installation tests or single mode for integration web tests.'''
        print("VM NAME = ", vm)
        # start.save_vmname(vm=vm)
        print(vm + " : executing....")
        start.write_in_box_log(vm + " tests are completed:" + '\n')
        start.read_cfg(box_distro_name=vm)
        start.start_up()
        start.remove_archive()
        start.parse_box_log()

    if start.run_test and start.multiprocess and not start.run_web:  # run_web is not elighable for the parallel. Probably BMR only.
        print('I am in Multiprocess')
        p = None
        #global tested_os
        #tested_os = None
        #for vm in start.os_list:
        print("STARTOSLIST ", start.os_list) # here we get the list of the machines we need to run tests on
        #p_obj=[]

        @retry_call(3)
        def letstry(tested_os):
            '''letstry - is the function, which run the test(vm) function several times(retry_call decorator does it).
            True/False are used to communicate with the decorator'''

            try:
                print('I am inside of the decorator function, the name of tested_os: ', tested_os)
                test(tested_os) # run the test(vm) function, which is working with the vagrant machine
                return True
            except:   #remove Exception. Now simple except is used
                print('In Exception of the letstry()')
                return False

        #@start.executor.retry()
        def process_file_wrapped(vm):
            """This function we use in Pool.map for multiprocess. In case of the exception in the test(vm) ->
             letsry(tested_os) will be called and letsry(tested_os) used decorator to repeat it).
             This is needed for the vagrant machines. Sometimes network issues/etc interrupts the connection"""
            try:
                global tested_os  # global variable is used to use it in other function, letstry(tested_os)
                tested_os = vm # will be used to shift the vm name
                test(vm)
            except:
                print('%s: %s' % (vm, traceback.format_exc()))
                print('I am in Exception of the Multiprocess. Needs to be rerun by the decorator.')
                letstry(tested_os)   # decorated function will be used to repeat the start of the vagrant box
        try:
            #for vm in start.os_list:
                # p = Process(target=test, args=(vm,))
                # p.start()
            p = Pool(processes=3)
            r = p.map(process_file_wrapped, start.os_list) # was test, start.os_list. Start.os_list is the argument to the process_file_wrapped.
            print('This is process %s',r)
            p.close()   # this line seems not needed if we have the same in finally block.
        except KeyboardInterrupt:
            print('%s' % (traceback.format_exc()))
            p.terminate()
            p.join()
        finally:
            p.close()

    else:
        print('I am in SingleProcess')
        for vm in start.os_list:
            start.save_vmname(vm) # save the name of the running instance, needs to be used in web tests.
            test(vm)  # Simple run of the test(vm) function.



    #     print(p.pid)
    #     p_obj.append(p)
    # for pid in p_obj:
    #     print(pid.pid, pid.is_alive())
    #     while pid.is_alive():
    #         time.sleep(5)

    #parent_conn.recv()
    #p.join()

    if start.run_web:
        #start.parse_installation_agent_log()
        pass
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    with open('result.log') as f:
        failed_result = False
        test_word = [': FAIL', 'Exception']
        failed_array = []
        for line in f:
            print(line)
            if any(x in line for x in test_word):
                failed_array.append(line)
                failed_result = True
    print('The end time is: ', datetime.now())
    if failed_result:
        print("There are failed tests")
        for i in failed_array:
            print(i)
        raise Exception("There are failed tests.")
    else:
        print("Testing completed with no errors")
    #start.close_log()


