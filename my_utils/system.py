import os
import subprocess
import platform
import requests


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
    def __init__(self, cmd=None):
        self.cmd = cmd

    def execute(self, cmd=None):
        # type: (object) -> object
        if cmd is not None:
            self.cmd = cmd
        p = subprocess.Popen(self.cmd, shell=True, stderr=subprocess.STDOUT)
        (output, err) = p.communicate()
        p_status = p.wait()
        return output

class Agentinstall(SystemUtils): # this class should resolve all needed information
                            #for downloading repo package and install agent in
                            #the system.Configuration of the agent should be
                            # done in the configuration class.

#https://s3.amazonaws.com/repolinux/7.0.0/repo-packages/rapidrecovery-repo-debian8-x86_32.deb

    # test = SystemUtils()
    # test2 = test.distr()
    build = "7.0.0"
    link = None
    su = SystemUtils()

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
        #l = 10 / 0
        build = Agentinstall.build
        check = Agentinstall()
        test = SystemUtils()
        link = 'https://s3.amazonaws.com/repolinux/' + build + '/repo-packages/rapidrecovery-repo-' + check.install_distname() + check.install_version() + '-' + test.machine_type() + '.' + check.install_packmanager()
        return link

    def download_file(self):
        l = 10 / 0
        self.test = Agentinstall()
        filename = 'repo'
        r = requests.get(self.test.create_link())
        file = open(filename, 'wb')
        for chunk in r.iter_content(100000):
            file.write(chunk)
        file.close()

    def run_installer(self):
        check = Agentinstall()
        install = check.packmanager() + " -i" + " repo"
        execute = Executor()
        execute.execute('date')
        execute.execute('ls -l')
        execute.execute(install)
        print(install)
        update = check.software_manager() + " update"
        execute.execute(update)







