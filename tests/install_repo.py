from __future__ import print_function
import subprocess
import platform
import os
import sys
sys.path.append("..")
from my_utils.system import *

class newclass():
    pass


class InstallRepo(Repoinstall):
    build = "7.0.0"
    link = None

    def __init__(self):
        super(Repoinstall, self).__init__()

    def setUp(self):
        self.uninstall_agent()

    def tearDown(self):
        #os.remove(self.repo_path)
        self.uninstall_repo()
        print("******")


    def runTest(self):

        #print(sys.platform, "this is platform")
        #print(sys.api_version, "this is api_version")
        self.create_link()
        self.download_file()
        self.run_repo_installer()
        self.get_process_pid(cmd='ssh')
        #self.check_initd()
        #cmd = 'rapidrecovery-repo'
        # self.getinstalledpackage(cmd)
        #if (cmd + "\n") in self.getinstalledpackage(cmd)[0]:
        #    return os.system('dpkg --list | grep rapid')
        #else:
        #    raise Exception("%s package is not installed. But should be installed." % cmd)
        self.check_package_installed('rapidrecovery-repo', True)


