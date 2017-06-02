import os
import sys
from my_utils.system import Executor, Repoinstall, SystemUtils
#import debug
#print sys.path


class UninstallAgent(Repoinstall):
    def __init__(self):
        super(Repoinstall, self).__init__()

    def setUp(self):
        self.create_link()
        self.download_file()
        self.install_agent_fromrepo()

    def runTest(self):
        execute = Executor()
        execute.execute('ls -1')
        self.uninstall_agent()
        self.check_package_installed('rapidrecovery-mono', False)
        self.check_package_installed('rapidrecovery-vdisk', False)
        self.check_package_installed('dkms', False)





    def tearDown(self):
        pass