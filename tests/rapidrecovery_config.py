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

            elif self.install_distname() in ["rhel", "centos", "oracle"]:

                if self.install_version() is "7":
                    firewall = "firewalld"
                else:
                    firewall = "lokkit"
                self.file_exists(result=True, file=config)
                self.file_exists(result=False, file=configuration_log)
                self.rapidrecovery_config_api(port="8006", user="vagrant",
                                              method=firewall,
                                              build="all", start=True)

            elif self.install_distname() in ["suse", "sles"]:
                if self.execute.error_code(cmd='sudo /sbin/rcSuSEfirewall2 status') is 3: #check that firewall is disabled
                    self.file_exists(result=True, file=config)
                    self.file_exists(result=False, file=configuration_log)
                    self.rapidrecovery_config_api(port="8006", user="vagrant", build="all", snapper="disable", start=True)
                else:
                    firewall = "lokkit"
                    self.file_exists(result=True, file=config)
                    self.file_exists(result=False, file=configuration_log)
                    self.rapidrecovery_config_api(port="8006", user="vagrant", method=firewall,
                                              build="all", snapper="disable", start=True)

            else:
                return Exception("The is error in the os determination/")

        except Exception as E:
            print(E)
            raise Exception

        finally:
            self.parse_configuration_log()
