from __future__ import print_function
import subprocess
import platform
import os
import sys
#import debug
#print sys.path
sys.path.append("..")
#print sys.path
from my_utils.system import *

class newclass():
    pass


class InstallAgent(Repoinstall, SystemUtils):
    build = "7.0.0"
    link = None

    def __init__(self):
        super(Repoinstall, self).__init__()

    def setUp(self):
        self.uninstall_agent()

    def tearDown(self):

        os.remove(self.repo_path)
        self.uninstall_agent()
        #print("The agent uninstall has been completed")

    def runTest(self):

        #print(sys.platform, "this is platform")
        #print(sys.api_version, "this is api_version")
        self.status_of_the_service('rapidrecovery-agent' , 3) #error code 3 is received when service is not running for systemctl
        self.create_link()
        self.download_file()
        self.install_agent_fromrepo()
        self.check_package_installed('rapidrecovery-repo', True)
        self.check_package_installed('rapidrecovery-agent', True)
        self.check_package_installed('rapidrecovery-mono', True)
        self.check_package_installed('dkms', True)
        self.status_of_the_service('rapidrecovery-agent', 3) # Agent should not be started right after install. It should be started only after configuring.
        self.status_of_the_service('rapidrecovery-mapper', 3)
        self.status_of_the_service('rapidrecovery-vdisk', 3)
        self.status_of_the_service('ssh', 0)



        #print("The testing of the install_agent is completed", end='\n\n')






    from my_utils.system import Executor

    #link = 	"https://s3.amazonaws.com/repolinux/$build/repo-packages/rapidrecovery-repo-$os$version-$arch.$package" -O "repo.file"



    #os = sys.platform
    #print sys.platform
    #pass
