from my_utils.system import Executor, Repoinstall


class UninstallAgent(Repoinstall):
    def __init__(self):
        super(Repoinstall, self).__init__()

    def setUp(self):
        self.create_link()
        self.download_file()
        self.install_agent_fromrepo()

    def runTest(self):
        execute = Executor()
        self.uninstall_agent()
        self.check_package_installed('dkms', expected_result=True) # we aren't remove dkms by default

        self.check_package_installed('rapidrecovery-mono', expected_result=False)

        self.check_package_installed('rapidrecovery-vdisk', expected_result=False)

        self.uninstall_autoremove()
        self.check_package_installed('dkms', expected_result=False) # dkms should be removed after autoremove

    def tearDown(self):
        self.uninstall_agent()