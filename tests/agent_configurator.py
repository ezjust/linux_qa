from __future__ import print_function
#sys.path.append("..")
from my_utils.system import *

class AgentConfigurator(Agent):
    link = None

    def __init__(self):
        super(Repoinstall, self).__init__()

    def setUp(self):
        self.install_agent_fromrepo()

    def tearDown(self):
        self.uninstall_agent()
        print("******")


    def runTest(self):

        rapidrecovery_config = "/usr/bin/rapidrecovery-config"
        agent_installation_log = "/var/log/apprecovery/agent.installation.log"
        apprecovery_log = "/var/log/apprecovery/apprecovery.log"
        bsctl_log = "/var/log/apprecovery/bsctl.log"
        configuration_log = "/var/log/apprecovery/configuration.log"

        if self.install_distname() in ["ubuntu", "debian"]:
            self.file_exists(result=True, file=rapidrecovery_config)
            self.file_exists(result=True, file=agent_installation_log)
            self.file_exists(result=False, file=apprecovery_log)
            self.file_exists(result=True, file=bsctl_log)
            self.file_exists(result=False, file=configuration_log)
        elif self.install_distname() in ["rhel", "centos", "oracle", "sles", "suse"]:
            self.file_exists(result=True, file=rapidrecovery_config)
            self.file_exists(result=True, file=agent_installation_log)
            self.file_exists(result=False, file=apprecovery_log)
            self.file_exists(result=True, file=bsctl_log)
            self.file_exists(result=False, file=configuration_log)
        else:
            return Exception("The error in expected test result")


