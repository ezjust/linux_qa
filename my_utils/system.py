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
        return (p.returncode)

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
        distributive = self.distname()
        if distributive.lower() in ["rhel", "centos", "oracle"]:
            return "rhel"
        elif distributive.lower() in ["ubuntu", "debian"]:
            return "debian"
        elif distributive.lower() in ["suse", "sles"]:
            return "sles"
        else:
            raise ValueError('The distributive of the system is not recognized')

    def install_packmanager(self):
        distributive = self.distname()
        if distributive.lower() in ["rhel", "centos", "oracle"]:
           return "rpm"
        elif distributive.lower() in ["ubuntu", "debian"]:
           return "deb"
        elif distributive.lower() in ["suse", "sles"]:
           return "rpm"
        else:
           raise ValueError('The pack_manager of the system is not recognized')

    def packmanager(self):
        distributive = self.distname()
        if distributive.lower() in ["rhel", "centos", "oracle"]:
           return "rpm"
        elif distributive.lower() in ["ubuntu", "debian"]:
           return "dpkg"
        elif distributive.lower() in ["suse", "sles"]:
           return "rpm"
        else:
           raise ValueError('The packmanager of the system is not recognized')

    def installed_package(self):
        distributive = self.distname()
        if distributive.lower() in ["rhel", "centos", "oracle"]:
           return "rpm -qa"
        elif distributive.lower() in ["ubuntu", "debian"]:
           return "dpkg --list"
        elif distributive.lower() in ["suse", "sles"]:
           return "rpm -qa"
        else:
           raise ValueError('The command for installed package is not reqognized')

    def software_manager(self):
        distributive = self.distname()
        if distributive.lower() in ["rhel", "centos", "oracle"]:
           return "yum"
        elif distributive.lower() in ["ubuntu", "debian"]:
           return "apt-get"
        elif distributive.lower() in ["suse", "sles"]:
            return "zypper"
        else:
            raise ValueError('The packmanager of the system is not recognized')

    def install_version(self):
        distributive = self.install_distname()
        version = self.version()
        if distributive.lower() == "debian" and version in ["15.04", "16.04", "16.10", "17.04", "17.10", "8", "9"]:
            return "8"
        elif distributive.lower() is "debian" and version in ["12.04", "12.10", "14.04", "14.10", "7"]:
            return "7"
        elif distributive.lower() is "rhel" and version in ["7.0", "7.1", "7.2", "7.3", "7.4", "7.5", "7.6", "7.7", "7.8"]:
            return "7"
        elif distributive.lower() is "rhel" and version in ["6.0", "6.1", "6.2", "6.3", "6.4", "6.5", "6.6", "6.7", "6.8"]:
            return "6"
        elif distributive.lower() is "sles" and version in ["11.0", "11.1", "11.2", "11.3"]:
            return "11"
        elif distributive.lower() is "sles" and version in ["12.0", "12.1", "12.2", "12.3"]:
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
        execute = Executor()
        uninstallation_agent = self.software_manager() + " remove" + " " + self.agent
        execute.execute(uninstallation_agent)
        unistallation_other = self.software_manager() + " remove" + " rapidrecovery-*"
        execute.execute(unistallation_other)
        autoremove = self.software_manager() + " autoremove"
        execute.execute(autoremove)
        not_removed = execute.execute(self.software_manager() + " | grep rapid | awk '{print $2}'")
        print(not_removed)

    def uninstall_repo(self):
        execute = Executor()
        uninstallation_repo = self.software_manager() + " remove" + " " + self.repo
        execute.execute(uninstallation_repo)

    def get_process_pid(self, cmd):
        self.cmd = 'pidof ' + cmd
        return self.execute.execute(self.cmd)

    def get_installed_package(self, cmd):
        self.cmd = self.installed_package() + " | " + "grep " + cmd + " | awk '{print $2}'"
        return self.execute.execute(self.cmd)

    def get_service_status(self, cmd):
        pass

    def check_package_installed(self, cmd, result):
        # self.getinstalledpackage(cmd)
        self.cmd = cmd
        self.result = result
        if self.result is "True":
            if (self.cmd + "\n") in self.get_installed_package(self.cmd)[0]:
                return
            else:
                raise Exception(
                    "%s package is not installed. But should be installed." % self.cmd)
        else:
            if (self.cmd + "\n") not in self.get_installed_package(self.cmd)[0]:
                return
            else:
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
            if self.execute.error_code(command) is not self.code:
                raise Exception("Got %s error code instead of %s for %s command" % (self.execute.error_code(command), self.code, self.cmd))
            #return self.execute.error_code(command)
        elif a.check_initd() == '/etc/init.d':
            command = '/etc/init.d/%s status'% self.cmd
            if self.execute.error_code(command) is not self.code:
                raise Exception("Got %s error code instead of %s for %s command" % (self.execute.error_code(command), self.code, self.cmd))
            #return self.execute.error_code(command)
        else:
            raise Exception("Pizdec!")









