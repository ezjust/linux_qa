import subprocess
import platform

class Execute(object):

    def __init__(self, cmd=None):
        self.cmd = cmd

    def distributive(self):
        '''Return the name of the distributive
        example: Ubuntu, Centos'''
        distributive = platform.linux_distribution()[0].split()
        distributive = distributive[0]
        return distributive.lower()

    def distributive_version(self):
        '''Return the version of the distributive
        example: 18.04, 17'''
        return platform.linux_distribution()[1]

    def execute(self, cmd=None, debug=True):
    # type: (object) -> object
        if cmd is not None:
            self.cmd = cmd
        if debug:
            print('cmd is : ', self.cmd)
        p = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE,
                             stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        (output, err) = p.communicate(input="{}\n".format("Y"))
        if debug:
            print(output)
            print(err)
        if p.poll() is 0:
            return output
        else:
            return Exception('There is non 0 exit code (%s) for the %s', (p.poll(), self.cmd))

    def package_system(self):
        try:
            if self.distributive() in ['Ubuntu', 'Debian']:
                return 'apt-get'
            elif self.distributive() in ["rhel", "centos", "oracle", "scientific"]:
                return 'yum'
            elif self.distributive() in ["suse", "sles"]:
                return 'zypper'
        except Exception as e:
            raise e

    def list_packages(self):
        try:
            if self.distributive() in ["rhel", "centos", "oracle", "scientific", "suse", "sles"]:
                return "rpm -qa"
            elif self.distributive() in ["ubuntu", "debian"]:
                return "dpkg --list"
        except Exception as e:
            raise e

    def package_installed(self, package_name):
        if package_name:
            try:
                if self.execute(cmd=self.list_packages() + ' | grep ' + package_name):
                    return True
                else:
                    return False
            except Exception as e:
                raise e