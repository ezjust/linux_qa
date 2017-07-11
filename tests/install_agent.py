from __future__ import print_function
from my_utils.system import *

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

    def runTest(self):

        self.status_of_the_service('rapidrecovery-agent' , 3) #error code 3 is received when service is not running for systemctl
        print("1")
        self.install_agent_fromrepo()
        self.check_package_installed('rapidrecovery-repo', True)
        self.check_package_installed('rapidrecovery-agent', True)
        print("2")
        self.check_package_installed('rapidrecovery-mono', True)
        self.check_package_installed('dkms', True)
        self.status_of_the_service('rapidrecovery-agent', 3) # rapidrecovery-agent should not be started right after install. It should be started only after configuring.
        print("3")
        self.status_of_the_service('rapidrecovery-mapper', 3) # rapidrecovery-mapper should not be started right after install. It should be started only after configuring.
        self.status_of_the_service('rapidrecovery-vdisk', 3) # rapidrecovery-vdisk should not be started right after install. It should be started only after configuring.
        self.status_of_the_service('ssh', 0)

