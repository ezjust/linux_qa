from __future__ import print_function
from my_utils.system import *

class AgentConfigurator(Agent):

    rapidrecovery_config = "/usr/bin/rapidrecovery-config"
    agent_installation_log = "/var/log/apprecovery/agent.installation.log"
    apprecovery_log = "/var/log/apprecovery/apprecovery.log"
    bsctl_log = "/var/log/apprecovery/bsctl.log"
    configuration_log = "/var/log/apprecovery/configuration.log"


    def __init__(self):
        super(Repoinstall, self).__init__()

    def setUp(self):
        '''By default, configuration file is not create once installation is 
                completed. But, in case if previous tests with the using of the
                 rapidrecovery-config were used, this file might be before start of the
                 test. Due to this we are checking that and remove.'''
        if os.path.isfile(self.configuration_log):
            os.system("sudo rm -rf " + self.configuration_log)
        if os.path.isfile(self.agent_installation_log):
            os.system("sudo rm -rf " + self.agent_installation_log)
        if os.path.isfile(self.apprecovery_log):
            os.system("sudo rm -rf " + self.apprecovery_log)
        if os.path.isfile(self.bsctl_log):
            os.system("sudo rm -rf " + self.bsctl_log)

        self.install_agent_fromrepo()

    def tearDown(self):
        self.uninstall_agent()
        self.unload_module()


    def runTest(self):

        if self.install_distname() in ["ubuntu", "debian"]:
            self.file_exists(result=True, file=self.rapidrecovery_config)
            self.file_exists(result=True, file=self.agent_installation_log)
            self.file_exists(result=False, file=self.apprecovery_log)
            self.file_exists(result=True, file=self.bsctl_log)
            self.file_exists(result=False, file=self.configuration_log)
        elif self.install_distname() in ["rhel", "centos", "oracle", "sles", "suse"]:
            self.file_exists(result=True, file=self.rapidrecovery_config)
            self.file_exists(result=True, file=self.agent_installation_log)
            self.file_exists(result=False, file=self.apprecovery_log)
            self.file_exists(result=True, file=self.bsctl_log)
            self.file_exists(result=False, file=self.configuration_log)
        else:
            return Exception("The error in expected test result")


