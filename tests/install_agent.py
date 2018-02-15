from __future__ import print_function
from my_utils.system import *

class InstallAgent(Repoinstall, SystemUtils):
    link = None

    def __init__(self):
        super(Repoinstall, self).__init__()

    def setUp(self):
        self.uninstall_agent()

    def tearDown(self):

        os.remove(self.repo_path)
        self.uninstall_agent()


    def runTest(self):
        # print("Start")
        if self.check_initd() == 'systemctl':
            version = self.version().split(".")[0]
            # print(version)
            if self.install_distname() in ["ubuntu", "debian", "sles"] and version not in ["18", "17", "9"]:

                '''
                There is difference in error code for the not-installed service in 17.04 and 16.04. 17.04, 17.10, debian 9 return error code 4, 16.04 return error code 3
                '''

                self.status_of_the_service('rapidrecovery-agent' , 3) #error code 3 is received when service is not istalled
            else:
                self.status_of_the_service('rapidrecovery-agent' , 4) #error code 4 is received when service is not istalled

            self.install_agent_fromrepo()
            self.check_package_installed('rapidrecovery-repo', expected_result=True)
            self.check_package_installed('rapidrecovery-agent', expected_result=True)
            # print("2")
            self.check_package_installed('rapidrecovery-mono', expected_result=True)
            self.check_package_installed('dkms', expected_result=True)
            if self.install_distname() in ["ubuntu", "debian"]:
                self.status_of_the_service('rapidrecovery-agent',
                                           3)  # rapidrecovery-agent should be started right after install. DPKG systems
                # print("3")
                self.status_of_the_service('rapidrecovery-mapper',
                                           3)  # rapidrecovery-mapper should be started right after install. DPKG systems
                self.status_of_the_service('rapidrecovery-vdisk',
                                           3)  # rapidrecovery-vdisk should be started right after install. DPKG systems.
            else:
                # print('4')
                self.status_of_the_service('rapidrecovery-agent', 3) # rapidrecovery-agent should not be started right after install. It should be started only after configuring.
                # print("3")
                self.status_of_the_service('rapidrecovery-mapper', 3) # rapidrecovery-mapper should not be started right after install. It should be started only after configuring.
                self.status_of_the_service('rapidrecovery-vdisk', 3) # rapidrecovery-vdisk should not be started right after install. It should be started only after configuring.
        else:
            self.status_of_the_service('rapidrecovery-agent',
                                       127)  # error code 127 is received when service is not istalled
            # print("1")
            self.install_agent_fromrepo()
            self.check_package_installed('rapidrecovery-repo',
                                         expected_result=True)
            self.check_package_installed('rapidrecovery-agent',
                                         expected_result=True)
            # print("2")
            self.check_package_installed('rapidrecovery-mono',
                                         expected_result=True)
            self.check_package_installed('dkms', expected_result=True)
            if self.install_distname() in ["ubuntu", "debian"]:
                self.status_of_the_service('rapidrecovery-agent',
                                           0)  # 1 is received when service is not running. rapidrecovery-agent should be started right after install.
                # print("3")
                self.status_of_the_service('rapidrecovery-mapper',
                                           0)  # rapidrecovery-mapper should be started right after install.
                self.status_of_the_service('rapidrecovery-vdisk',
                                           0)  # rapidrecovery-vdisk should be started right after install.

            else:
                self.status_of_the_service('rapidrecovery-agent',
                                           1)  # 1 is received when service is not running. rapidrecovery-agent should not be started right after install. It should be started only after configuring.
                # print("3")
                self.status_of_the_service('rapidrecovery-mapper',
                                           1)  # rapidrecovery-mapper should not be started right after install. It should be started only after configuring.
                self.status_of_the_service('rapidrecovery-vdisk',
                                           1)  # rapidrecovery-vdisk should not be started right after install. It should be started only after configuring.
