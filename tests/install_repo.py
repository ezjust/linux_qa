from __future__ import print_function
import sys
#sys.path.append("..")
from my_utils.system import *

class InstallRepo(Repoinstall):
    build = "7.0.0"
    link = None

    def __init__(self):
        super(Repoinstall, self).__init__()

    def setUp(self):
        self.uninstall_agent()

    def tearDown(self):
        self.uninstall_repo()
        print("******")


    def runTest(self):

        self.create_link()
        self.download_file()
        self.run_repo_installer()
        #self.get_process_pid(cmd='ssh')
        self.check_package_installed('rapidrecovery-repo', result=True)


