import os
import subprocess
import platform
import requests
import time
import errno
from datetime import datetime



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

    def execute(self, cmd=None):
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
        if err not in (0, 100):
            raise Exception("Exception: '%s' command finished with error code %d" %(self.cmd, err))
        elif err is 100:
            count = 0
            print('This is err %s' % err)
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
                print(err)
                count+=1
                time.sleep(20)

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
    build = "7.0.0"
    agent = "rapidrecovery-agent"
    repo =  "rapidrecovery-repo"
    link = None
    su = SystemUtils()
    repo_path = os.getcwd() + "/repo"
    print repo_path
    execute = Executor()


    def __init__(self):
        super(SystemUtils, self).__init__()

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
        print distributive.lower()
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
        print(distributive)
        print(distributive.lower())
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
        print("I am here in install version")
        print(distributive)
        version = self.version()
        print(version)
        version = version.rsplit('.')[0] + "." + version.rsplit('.')[1]
        print(version)
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
        build = Repoinstall.build
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
        install = check.packmanager() + " -i" + " repo"
        execute = Executor()
        execute.execute(install)
        update = check.software_manager() + " update"
        execute.execute(update)

    def install_agent_fromrepo(self):
        self.create_link()
        self.download_file()
        check = Repoinstall()
        install = check.packmanager() + " -i" + " repo"
        execute = Executor()
        execute.execute(install)
        update = check.software_manager() + " update"
        execute.execute(update)
        #print self.agent
        installation = check.software_manager() + " install" + " " + self.agent
        #print installation
        execute.execute(installation)

    def uninstall_agent(self):
        check_installed_code = None
        execute = Executor()
        print("I am here is uninstall0")

        print(self.installed_package())
        print("I am here is uninstall")
        print(execute.error_code(self.installed_package() + " | grep rapid"))
        if self.packmanager() in "rpm":
            check_installed_code = execute.error_code(self.installed_package() + " | grep rapid")
        elif self.packmanager() in "dpkg":
            check_installed_code = execute.error_code(
                self.installed_package() + "| grep ii | grep rapid")
        if check_installed_code is 0:
            print("I am here in uninstallation process")
            uninstallation_agent = self.software_manager() + " -y" + " remove" + " " + self.agent
            unistallation_other = self.software_manager() + " -y" + " remove" + " rapidrecovery-*"
            print("UNinstallation_other, %s" % unistallation_other)
            execute.execute(uninstallation_agent)
            execute.execute(unistallation_other)
            print("List of not-removeed packages:")
            not_removed = execute.execute(self.software_manager() + " | grep rapid | awk '{print $2}'")[0][0]
            print("not removed= %s" % not_removed)
            not_removed_dkms = execute.execute(self.software_manager() + " | grep dkms | awk '{print $2}'")[0][0]
            print("not removed_dkms= %s" % not_removed_dkms)

    def uninstall_autoremove(self):
        execute = Executor()
        autoremove = self.software_manager() + " -y" + " autoremove"
        execute.execute(autoremove)
        not_removed_dkms = execute.execute(self.software_manager() + " | grep dkms | awk '{print $2}'")[0][0]
        print("not removed_dkms= %s" % not_removed_dkms)


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
            self.command = self.installed_package() + " | " + "grep ii" + " | " + "grep " + self.cmd + " | awk '{print $2}' | head -n1"
        else:
            raise Exception("self.packmanager indicated error during execution")

        # print(self.execute.execute(self.command))
        return self.execute.execute(self.command)[0][0]

    def get_service_status(self, cmd):
        pass

    def check_package_installed(self, cmd, result):
        # self.getinstalledpackage(cmd)
        self.cmd = cmd
        self.result = result
        if self.result is True:
            print("self.cmd=" + self.cmd)
            print("asd")
            print(self.get_installed_package(self.cmd))
            print("dsa")
            if (self.cmd) in self.get_installed_package(self.cmd):
                print("Finally")
                return
            else:
                print(self.get_installed_package(self.cmd))
                raise Exception(
                    "%s package is NOT installed. But should be installed." % self.cmd)
        else:
            if (self.cmd + "\n") not in self.get_installed_package(self.cmd):
                return
            else:
                print(self.get_installed_package(self.cmd))
                raise Exception(
                    "%s package is installed. But should NOT be installed." % self.cmd)


    def return_of_unix_command(self, command):
        self.command = command
        result = self.execute.execute(self.command)[0][0]#
        return result


    def check_initd(self):
        execute = Executor()
        a = Repoinstall()
        command = 'systemctl --v'
        if ('systemd') in a.return_of_unix_command(command):
            return 'systemctl'
        else:
            return '/etc/init.d'

    def status_of_the_service(self, cmd, code):
        a = Repoinstall()
        self.cmd = cmd
        self.code = code
        if a.check_initd() == 'systemctl':
            command = 'systemctl status %s'% self.cmd
            if self.code is not None:
                if self.execute.error_code(command) is not self.code:
                    raise Exception("Got %s error code instead of %s for %s command" % (self.execute.error_code(command), self.code, self.cmd))
            #return self.execute.error_code(command)
        elif a.check_initd() == '/etc/init.d':
            command = '/etc/init.d/%s status'% self.cmd
            if self.code is not None:
                if self.execute.error_code(command) is not self.code:
                    raise Exception("Got %s error code instead of %s for %s command" % (self.execute.error_code(command), self.code, self.cmd))
            #return self.execute.error_code(command)
        else:
            raise Exception("Pizdec!")


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
            raise Exception("Pizdec!")


class Agent(Repoinstall):
    bsctl_v = "sudo bsctl -v | awk '{print$5}'"
    rapidrecovery_vss_v = "dmesg | grep 'rapidrecovery-vss: loaded' | tail -n1 | tr ' ' '\n' | tail -n4 | head -n1"
    module_name = "rapidrecovery-vss"
    check_module_is_loaded = "lsmod | grep rapidrecovery_vss"
    nbd_check = "ps axf | grep 'nbd[0-9]'; echo $?"
    rapid_vss_installed = "/usr/sbin/dkms status | grep rapidrecovery-vss | tr ' ' '\n' | tail -n1"

    def file_exists(self, file):
        self.file = file
        if os.path.isfile(self.file) is True:
            return
        else:
            raise Exception("%s : File is not exist" % self.file)

    def check_agent_is_running(self):
        if self.status_of_the_service('rapidrecovery-agent', None) is not 0:
            self.service_activity('rapidrecovery-agent', 'restart')
            self.status_of_the_service('rapidrecovery-agent', 0)
            print("I am in servicce agent is running. Agent should be running now.")

    def bsctl_hash(self):
        bsctl_hash = self.execute.execute(self.bsctl_v)
        print(bsctl_hash)
        return bsctl_hash

    def rapidrecovery_vss_hash(self):
        result = self.execute.execute(self.rapidrecovery_vss_v)[0][0]
        while len(result) is 0:
            result = self.execute.execute(self.rapidrecovery_vss_v)[0][0]
            time.sleep(5)
            print("Waiting for the rapidrecovery_vss_v")
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

