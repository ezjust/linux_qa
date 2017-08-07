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
        execute.execute('ls -1')
        print("Hello")
        self.uninstall_agent()
        print("Firstcheck")
        self.check_package_installed('dkms', True) # we aren't remove dkms by default

        self.check_package_installed('rapidrecovery-mono', False)
        self.check_package_installed('rapidrecovery-vdisk', False)
        self.uninstall_autoremove()
        print("I am here2")
        self.check_package_installed('dkms', False) # dkms should be removed after autoremove

    def tearDown(self):
        self.uninstall_agent()