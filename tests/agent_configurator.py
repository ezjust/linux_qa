from __future__ import print_function
#sys.path.append("..")
from my_utils.system import *

class AgentConfigurator(Agent):
    build = "7.0.0"
    link = None

    def __init__(self):
        super(Repoinstall, self).__init__()

    def setUp(self):
        self.install_agent_fromrepo()

    def tearDown(self):
        self.uninstall_agent()

    def runTest(self):

        rapidrecovery_config = "/usr/bin/rapidrecovery-config"
        agent_installation_log = "/var/log/apprecovery/agent.installation.log"
        apprecovery_log = "/var/log/apprecovery/apprecovery.log"
        bsctl_log = "/var/log/apprecovery/bsctl.log"
        configuration_log = "/var/log/apprecovery/configuration.log"


        self.file_exists(rapidrecovery_config)
        self.file_exists(agent_installation_log)
        self.file_exists(apprecovery_log)
        self.file_exists(bsctl_log)
        self.file_exists(configuration_log)

