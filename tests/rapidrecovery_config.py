from __future__ import print_function
from my_utils.system import *

class RapidrecoveryConfig(Agent):

    def __init__(self):
        super(Repoinstall, self).__init__()

    def setUp(self):
        self.install_agent_fromrepo()

    def tearDown(self):
        self.uninstall_agent()


    def runTest(self):

        config = "/usr/bin/rapidrecovery-config"
        configuration_log = "/var/log/apprecovery/configuration.log"
        try:
            if self.install_distname() in ["ubuntu", "debian"]:
                self.file_exists(result=True, file=config)
                self.file_exists(result=False, file=configuration_log)
                self.rapidrecovery_config_api(port="8006", user="vagrant", method="ufw", build="all", start=True)
                self.parse_configuration_log()


            elif self.install_distname() in ["rhel", "centos", "oracle", "sles", "suse"]:

                if self.install_version() is "7":
                    firewall = "systemd"
                else:
                    firewall = "lokkit"

                self.file_exists(result=True, file=config)
                self.file_exists(result=False, file=configuration_log)
                self.rapidrecovery_config_api(port="8006", user="vagrant", method=firewall,
                                              build="all", start=True)
                self.parse_configuration_log()
            else:
                return Exception("The error in expected test result")
        except Exception as E:
            print(E)
            raise Exception

