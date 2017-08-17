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
        print("Start")
        if self.check_initd() == 'systemctl':
            self.status_of_the_service('rapidrecovery-agent' , 3) #error code 3 is received when service is not istalled
            print("1")
            self.install_agent_fromrepo()
            self.check_package_installed('rapidrecovery-repo', expected_result=True)
            self.check_package_installed('rapidrecovery-agent', expected_result=True)
            print("2")
            self.check_package_installed('rapidrecovery-mono', expected_result=True)
            self.check_package_installed('dkms', expected_result=True)
            self.status_of_the_service('rapidrecovery-agent', 3) # rapidrecovery-agent should not be started right after install. It should be started only after configuring.
            print("3")
            self.status_of_the_service('rapidrecovery-mapper', 3) # rapidrecovery-mapper should not be started right after install. It should be started only after configuring.
            self.status_of_the_service('rapidrecovery-vdisk', 3) # rapidrecovery-vdisk should not be started right after install. It should be started only after configuring.
        else:
            self.status_of_the_service('rapidrecovery-agent',
                                       127)  # error code 127 is received when service is not istalled
            print("1")
            self.install_agent_fromrepo()
            self.check_package_installed('rapidrecovery-repo',
                                         expected_result=True)
            self.check_package_installed('rapidrecovery-agent',
                                         expected_result=True)
            print("2")
            self.check_package_installed('rapidrecovery-mono',
                                         expected_result=True)
            self.check_package_installed('dkms', expected_result=True)
            self.status_of_the_service('rapidrecovery-agent',
                                       1)  # 1 is received when service is not running. rapidrecovery-agent should not be started right after install. It should be started only after configuring.
            print("3")
            self.status_of_the_service('rapidrecovery-mapper',
                                       1)  # rapidrecovery-mapper should not be started right after install. It should be started only after configuring.
            self.status_of_the_service('rapidrecovery-vdisk',
                                       1)  # rapidrecovery-vdisk should not be started right after install. It should be started only after configuring.
