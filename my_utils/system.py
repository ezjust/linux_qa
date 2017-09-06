import os
import subprocess
import platform
import requests
import time
import errno
from datetime import datetime
import ConfigParser



class SystemUtils(object):
    #distname = None
    #version = None

    def __init__(self):
        pass

    def machine_type(self): #Returns the machine type, e.g. 'i386'. An empty string is returned if the value cannot be determined.
        return platform.machine()

    def pythonver(self):
        return platform.python_revision()

    def distname(self):
        # (self.distname, self.version)
        # []
        # {"key": "val"}
        # set{1, 2, 3}
        return platform.linux_distribution()[0]

    def version(self):
        ver = platform.linux_distribution()[1]
        return ver



class Executor(object):
    __instance = None
    __logDir = "Logs"
    __logFile = None
    __debug = True
    distr = SystemUtils()


    def __init__(self, cmd=None):
        self.cmd = cmd

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(Executor, cls).__new__(cls)
            start_log_time = time.strftime("%Y%m%d-%H%M%S")
            if not os.path.exists(cls.__logDir):
                os.mkdir(cls.__logDir)
            cls.__logFile = open(cls.__logDir + "/Log-%s.log" % start_log_time,
                                 "w+")
        return cls.__instance




    def package_manager(self):

        distributive = self.distr.distname().split()
        distributive = distributive[0]
        if distributive.lower() in ["rhel", "centos", "oracle"]:
            return "yum"
        elif distributive.lower() in ["ubuntu", "debian"]:
            return "apt-get"
        elif distributive.lower() in ["suse", "sles"]:
            return "zypper"
        else:
            raise ValueError('The package manager of the system is not recognized')

    def execute(self, cmd=None):
        # type: (object) -> object
        if cmd is not None:
            self.cmd = cmd
        p = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE,
                             stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        #((output, err), code)
        (output, err) = p.communicate(input="{}\n".format("Y")), p.returncode
        # print("OUT=", output)
        # print(output)
        # print(err)
        # p.stdin.write("Y\n")
        p_status = p.wait()
        #error_code = p.communicate()[0]
        if err not in (0, 100):
            raise Exception("Exception: '%s' command finished with error code %d" %(self.cmd, err))
        elif err is 100:
            count = 0
            # print('This is err %s' % err)
            while err is 100:

                p = subprocess.Popen(self.cmd, shell=True,
                                     stdout=subprocess.PIPE,
                                     stdin=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
                # ((output, err), code)
                (output, err) = p.communicate(
                    input="{}\n".format("Y")), p.returncode
                # print("OUT=", output)
                # print(output)
                # p.stdin.write("Y\n")
                p_status = p.wait()
                # error_code = p.communicate()[0]
                print("%s :: I am in %s retry. 100 error core is received for '%s' command" % (time.ctime(), count, self.cmd))
                # print(err)
                count+=1
                time.sleep(60)
                if 'install' in self.cmd or 'update' in self.cmd:
                    clean_all = self.package_manager() + " clean all"
                    self.execute(cmd=clean_all)
                    find_all_apt = "ps -A | grep apt | awk '{print $1}'"
                    if self.error_code(cmd=find_all_apt) is not 100:
                        result_find = self.execute(find_all_apt)[0][0]
                        # print result_find
                        if len(result_find) is not 0:
                            kill = "kill -9 " + result_find
                            # print kill
                            self.execute(kill)
                    if self.error_code(cmd=self.package_manager() + " update") is 0:
                        self.execute(cmd=self.package_manager() + " update")
                if 'remove' in self.cmd:
                    break


            return (output, err)
        else:
            return (output, err)

    def error_code(self, cmd=None):
        # type: (object) -> object
        if cmd is not None:
            self.cmd = cmd
        p = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE,
                             stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        #((output, err), code)
        (output, err) = p.communicate(input="{}\n".format("Y")), p.returncode
        # print("OUT=", output)
        #print(output)
        # p.stdin.write("Y\n")
        p_status = p.wait()
        #error_code = p.communicate()[0]
        return (p.poll())

    def get_logfile(self):
        return self.__logFile

    def set_debug(self, setter):
        self.__debug = setter

    def set_ignore_err(self, ignore):
        self.__ignoreError = ignore


    def log(self, string, timestamp=True):
        if self.__debug:
            print string
        if timestamp:
            ts = time.strftime("%H:%M:%S | ")
        else:
            ts = ""
        self.__logFile.write("%s%s" % (ts, string))
        self.__logFile.flush()






class Repoinstall(SystemUtils): # this class should resolve all needed information
                            #for downloading repo package and install agent in
                            #the system.Configuration of the agent should be
                            # done in the configuration class.

#https://s3.amazonaws.com/repolinux/7.0.0/repo-packages/rapidrecovery-repo-debian8-x86_32.deb

    # test = SystemUtils()
    # test2 = test.distr()
    build = None
    agent = "rapidrecovery-agent"
    repo =  "rapidrecovery-repo"
    link = None
    su = SystemUtils()
    repo_path = os.getcwd() + "/repo"
    print repo_path
    execute = Executor()


    def __init__(self):
        super(SystemUtils, self).__init__()

    def read_cfg(self):
        conf_file = "config.ini"
        self.conf_parser = ConfigParser.ConfigParser()
        self.conf_parser.optionxform = str
        self.conf_parser.readfp(open(conf_file))
        self.test_list = dict(self.conf_parser.items("tests"))
        self.build = self.conf_parser.get('general', 'build_agent')

    def install_distname(self):
        distributive = self.distname().split()
        distributive = distributive[0]
        if distributive.lower() in ["rhel", "centos", "oracle"]:
            return "rhel"
        elif distributive.lower() in ["ubuntu", "debian"]:
            return "debian"
        elif distributive.lower() in ["suse", "sles"]:
            return "sles"
        else:
            raise ValueError('The distributive of the system is not recognized')

    def install_packmanager(self):
        distributive = self.distname().split()
        distributive = distributive[0]
        if distributive.lower() in ["rhel", "centos", "oracle"]:
           return "rpm"
        elif distributive.lower() in ["ubuntu", "debian"]:
           return "deb"
        elif distributive.lower() in ["suse", "sles"]:
           return "rpm"
        else:
           raise ValueError('The pack_manager of the system is not recognized')

    def packmanager(self):
        distributive = self.distname().split()
        distributive = distributive[0]
        if distributive.lower() in ["rhel", "centos", "oracle"]:
           return "rpm"
        elif distributive.lower() in ["ubuntu", "debian"]:
           return "dpkg"
        elif distributive.lower() in ["suse", "sles"]:
           return "rpm"
        else:
           raise ValueError('The packmanager of the system is not recognized')

    def installed_package(self):
        distributive = self.distname().split()
        distributive = distributive[0]
        if distributive.lower() in ["rhel", "centos", "oracle"]:
           return "rpm -qa"
        elif distributive.lower() in ["ubuntu", "debian"]:
           return "dpkg --list"
        elif distributive.lower() in ["suse", "sles"]:
           return "rpm -qa"
        else:
           raise ValueError('The command for installed package is not reqognized')

    def software_manager(self):
        distributive = self.distname().split()
        distributive = distributive[0]
        if distributive.lower() in ["rhel", "centos", "oracle"]:
           return "yum"
        elif distributive.lower() in ["ubuntu", "debian"]:
           return "apt-get"
        elif distributive.lower() in ["suse", "sles"]:
            return "zypper"
        else:
            raise ValueError('The packmanager of the system is not recognized')

    def install_version(self):
        distributive = self.distname().split()
        distributive = distributive[0]
        version = self.version()
        version = version.rsplit('.')[0] + "." + version.rsplit('.')[1]
        if distributive.lower() in "debian, ubuntu" and version in ["15.04", "16.04", "16.10", "17.04", "17.10", "8.0", "8.1", "8.2", "8.3", "8.4", "8.5", "8.6", "8.7", "9.0", "9.1", "9.2", "9.3"]:
            return "8"
        elif distributive.lower() in "debian, ubuntu" and version in ["12.04", "12.10", "14.04", "14.10", "7"]:
            return "7"
        elif distributive.lower() in "rhel, centos, oracle" and version in ["7.0", "7.1", "7.2", "7.3", "7.4", "7.5", "7.6", "7.7", "7.8", "7.9"]:
            return "7"
        elif distributive.lower() in "rhel, centos, oracle" and version in ["6.0", "6.1", "6.2", "6.3", "6.4", "6.5", "6.6", "6.7", "6.8", "6.9"]:
            return "6"
        elif distributive.lower() in "sles, suse" and version in ["11.0", "11.1", "11.2", "11.3"]:
            return "11"
        elif distributive.lower() in "sles, suse" and version in ["12.0", "12.1", "12.2", "12.3"]:
            return "12"
        else:
            raise ValueError('The version of the distributive is not recognized')

    def create_link(self):
        self.read_cfg()
        build = self.build
        check = Repoinstall()
        test = SystemUtils()
        link = 'https://s3.amazonaws.com/repolinux/' + build + '/repo-packages/rapidrecovery-repo-' + check.install_distname() + check.install_version() + '-' + test.machine_type() + '.' + check.install_packmanager()
        return link

    def download_file(self):
        self.test = Repoinstall()
        filename = 'repo'
        r = requests.get(self.test.create_link())
        file = open(filename, 'wb')
        for chunk in r.iter_content(100000):
            file.write(chunk)
        file.close()

    def run_repo_installer(self):
        check = Repoinstall()
        install = "sudo " + check.packmanager() + " -i" + " repo"
        execute = Executor()
        execute.execute(install)
        update = "sudo " + check.software_manager() + " update"
        execute.execute(update)

    def install_agent_fromrepo(self):
        self.create_link()
        self.download_file()
        check = Repoinstall()
        try:
            execute = Executor()
            if self.check_installed_code_rapid() is 1:

                install = "sudo " + check.packmanager() + " -i" + " repo"
                execute.execute(install)

            elif self.check_installed_code_rapid() not in [0, 1]:
                raise Exception("Received not [0,1] result code for check rapid")

            update = "sudo " + check.software_manager() + " update -y"
            execute.execute(update)
            #print self.agent
            clean_all = "sudo " + check.software_manager() + " clean all"
            # print(clean_all)
            execute.execute(clean_all)
            execute.execute(update)
            installation = "sudo " + check.software_manager() + " install" + " -y " + self.agent
            # print installation
            execute.execute(installation)

        except Exception as e:
            print(e)


    def check_installed_code_rapid(self):
        '''Return if any rapidrecovery package is installed on the system.
        Returns 0 if package/s is available. 1 if not available'''
        execute = Executor()
        check_installed_code = None

        if self.packmanager() in "rpm":
            check_installed_code = execute.error_code(
                self.installed_package() + " | grep rapid")
        elif self.packmanager() in "dpkg":
            check_installed_code = execute.error_code(
                self.installed_package() + "| grep ii | grep rapid")

        return check_installed_code


    def uninstall_agent(self):
        execute = Executor()

        if self.check_installed_code_rapid() is 0:
            uninstallation_agent = self.software_manager() + " -y" + " remove" + " " + self.agent
            unistallation_other = self.software_manager() + " -y" + " remove" + " rapidrecovery-*"
            execute.execute(uninstallation_agent)
            not_removed = execute.execute(
                self.software_manager() + " | grep rapid | awk '{print $2}'")[
                0][0]
            not_removed_dkms = execute.execute(
                self.software_manager() + " | grep dkms | awk '{print $2}'")[
                0][0]
            if self.check_installed_code_rapid() is 0:
                execute.execute(unistallation_other)
            not_removed = execute.execute(self.software_manager() + " | grep rapid | awk '{print $2}'")[0][0]
            not_removed_dkms = execute.execute(self.software_manager() + " | grep dkms | awk '{print $2}'")[0][0]
            # print("completed uninstall agent")

    def uninstall_autoremove(self):
        execute = Executor()
        # print(self.install_version())
        version = self.install_version()
        if version is "6":
            uninstallation_dkms = self.software_manager() + " -y" + " remove" + " dkms"
            execute.execute(uninstallation_dkms)
        else:
            # print("I am in else statement")
            autoremove = "sudo " + self.software_manager() + " -y" + " autoremove"
            execute.execute(autoremove)
            uninstallation_dkms = self.software_manager() + " -y" + " remove" + " dkms"
            execute.execute(uninstallation_dkms)


    def uninstall_repo(self):
        execute = Executor()
        uninstallation_repo = self.software_manager() + " remove" + " " + self.repo
        execute.execute(uninstallation_repo)

    def get_process_pid(self, cmd):
        self.cmd = 'pidof ' + cmd
        return self.execute.execute(self.cmd)

    def get_installed_package(self, cmd):
        self.cmd = cmd
        if self.packmanager() in "rpm":
            self.command = self.installed_package() + " | " + "grep " + self.cmd
        elif self.packmanager() in "dpkg":
            self.command = self.installed_package() + " | " + "grep ii" + " | " + "grep " + self.cmd
        else:
            raise Exception("self.packmanager indicated error during execution")

        # print(self.execute.execute(self.command))
        code = self.execute.error_code(self.command)
        if code is 0:
            result = True
        elif code is 1:
            result = False
        else:
            raise Exception("I have received not [0, 1] exit codes for the %s" % self.command)
        # print(self.command + " is %s" % result)
        return result


    def get_service_status(self, cmd):
        pass

    def check_package_installed(self, cmd, expected_result):
        # self.getinstalledpackage(cmd)
        self.cmd = cmd
        self.expected_result = expected_result
        if self.expected_result is True:
            if self.expected_result is self.get_installed_package(self.cmd):
                return True
            else:
                raise Exception(
                    "%s package is NOT installed. But should be installed." % self.cmd)
        else:
            if self.expected_result is self.get_installed_package(self.cmd):
                return True
            else:
                print(" self.get_installed_package(self.cmd) is %s" % self.get_installed_package(self.cmd))
                print(" self.expected_result is %s" % self.expected_result)
                raise Exception(
                    "%s package is installed. But should NOT be installed." % self.cmd)


    def return_of_unix_command(self, command):
        self.command = command
        result = self.execute.execute(self.command)[0][0]
        return result


    def check_initd(self):
        '''127 error code is recevied for systemc --v on the init systems'''
        execute = Executor()
        a = Repoinstall()
        command = 'systemctl --v'
        if 127 is a.execute.error_code(command):
            return '/etc/init.d'
        else:
            return 'systemctl'

    def status_of_the_service(self, cmd, code):
        a = Repoinstall()
        self.cmd = cmd
        self.code = code
        if a.check_initd() == 'systemctl':
            command = 'systemctl status %s'% self.cmd
            if self.code is not None:
                if self.execute.error_code(command) is not self.code:
                    raise Exception("SYSTEMCTL: Got %s error code instead of %s for %s command" % (self.execute.error_code(command), self.code, self.cmd))
            #return self.execute.error_code(command)
        elif a.check_initd() == '/etc/init.d':
            command = '/etc/init.d/%s status'% self.cmd
            if self.code is not None:
                if self.execute.error_code(command) is not self.code:
                    raise Exception("INITD: Got %s error code instead of %s for %s command" % (self.execute.error_code(command), self.code, self.cmd))
            #return self.execute.error_code(command)
        else:
            raise Exception("Pizdec!")

    def error_code_of_the_service(self, cmd):
        a = Repoinstall()
        self.cmd = cmd
        if a.check_initd() == 'systemctl':
            command = 'systemctl status %s' % self.cmd
            return self.execute.error_code(command)
        elif a.check_initd() == '/etc/init.d':
            command = '/etc/init.d/%s status' % self.cmd
            return self.execute.error_code(command)
        else:
            raise Exception("Error is return of the error code of service")


    def service_activity(self, cmd, action):
        a = Repoinstall()
        self.cmd = cmd
        self.action = action
        if a.check_initd() == 'systemctl':
            command = 'systemctl %s %s' % (self.action, self.cmd)
            self.execute.execute(command)
        elif a.check_initd() == '/etc/init.d':
            command = '/etc/init.d/%s %s' % (self.cmd, self.action)
            self.execute.execute(command)
        else:
            raise Exception("failed to start service!")


class Agent(Repoinstall):
    bsctl_v = "sudo bsctl -v | awk '{print$5}'"
    rapidrecovery_vss_v = "dmesg | grep 'rapidrecovery-vss: loaded' | tail -n1 | tr ' ' '\n' | tail -n4 | head -n1"
    module_name = "rapidrecovery-vss"
    check_module_is_loaded = "lsmod | grep rapidrecovery_vss"
    nbd_check = "ps axf | grep 'nbd[0-9]'; echo $?"
    rapid_vss_installed = "/usr/sbin/dkms status | grep rapidrecovery-vss | tr ' ' '\n' | tail -n1"

    def file_exists(self, result, file):
        self.result = result
        self.file = file
        if self.result is True:
            if os.path.isfile(self.file) is True:
                return
            else:
                raise Exception("%s : File is not exist" % self.file)
        if self.result is False:
            if os.path.isfile(self.file) is False:
                return
            else:
                raise Exception("%s : File exists. This is error, it should not be existed." % self.file)

    def check_agent_is_running(self):
        if self.status_of_the_service('rapidrecovery-agent', None) is not 0:
            self.service_activity('rapidrecovery-agent', 'restart')
            self.status_of_the_service('rapidrecovery-agent', 0)
            print("I am in servicce agent is running. Agent should be running now.")

    def bsctl_hash(self):
        bsctl_hash = self.execute.execute(self.bsctl_v)
        return bsctl_hash

    def rapidrecovery_vss_hash(self):
        result = self.execute.execute(self.rapidrecovery_vss_v)[0][0]
        while len(result) is 0:
            result = self.execute.execute(self.rapidrecovery_vss_v)[0][0]
            time.sleep(5)
            # print("Waiting for the rapidrecovery_vss_v")
        rapidrecovery_vss_hash = self.execute.execute(self.rapidrecovery_vss_v)
        return rapidrecovery_vss_hash


    def unload_module(self):
        if self.execute.error_code(self.check_module_is_loaded) is 0:
            self.execute.execute('rmmod ' + self.module_name)

    def load_module(self):
        if self.execute.error_code(self.check_module_is_loaded) is not 0:
            self.execute.execute('modprobe' + self.module_name)

    def rapidrecovery_vss_installed(self):
        result = self.execute.execute(self.rapid_vss_installed)[0][0].rstrip()
        return result

    def rapidrecovery_config_api(self, port=None, user=None, method=None, build=None, start=None, vault=None, delete_user=None):
        '''
        :param port: 8006 
        :param user: rr
        :param method: firewalld, lokkit
        :param build: all, 0, 1, 2
        :param start: true
        :param vault: on, off
        :param delete_user: rr
        :return: True/False
        '''
        if build:
            self.build = build
        if port:
            self.port = port
        if user:
            self.user = user
        if start:
            self.start = start
        if method:
            self.method = method
        if vault:
            self.vault = vault
        if delete_user:
            self.delete_user = delete_user

        config = "/usr/bin/rapidrecovery-config"
        try:
            if port:
                self.execute.execute(cmd=config + " -p " + self.port)
            if user:
                self.execute.execute(cmd=config + " -u " + self.user)
            if build:
                self.execute.execute(cmd=config + " -m " + self.build)
            if method:
                self.execute.execute(cmd=config + " -f " + self.method)
            if start:
                self.execute.execute(cmd=config + " -s")
            if vault:
                self.execute.execute(cmd=config + " -v " + self.vault)
            if delete_user:
                self.execute.execute(cmd=config + " -d " + self.delete_user)
            return True

        except Exception as E:
            print E
            raise Exception


    def parse_configuration_log(self):
        configuration_log = "/var/log/apprecovery/configuration.log"
        try:
            with open(configuration_log, 'r') as f:
                words = ["Failed", "Error", "8006"]
                for line in f:
                    if any(s in line for s in words):
                        print(line)
                        words_error = ["Failed", "Error"]
                        if any(k in line for k in words_error):
                            print(line)
                            raise Exception("There are Failed states in the configuration.")

        except Exception as E:
            print E
            raise Exception
