from __future__ import print_function
from my_utils.system import *


class AgentCommands(Agent):
    counter = 0
    link = None

    # def __init__(self):
    #     super(Repoinstall, self).__init__()

    def setUp(self):
        self.unload_module()
        self.install_agent_fromrepo()

    def tearDown(self):
        self.uninstall_agent()
        self.unload_module()

    def runTest(self):
        try:
            self.check_package_installed('rapidrecovery-repo', expected_result=True)
            self.check_package_installed('rapidrecovery-agent', expected_result=True)
            self.check_package_installed('rapidrecovery-mono', expected_result=True)

            self.check_package_installed('dkms', expected_result=True)

            self.check_agent_is_running()
            print('Testplace')
            if self.install_distname() in ["ubuntu", "debian"]:
                self.counter = 0
                while self.error_code_of_the_service('rapidrecovery-vdisk') is not 0 and self.counter <= 12:
                    time.sleep(5)
                    self.counter = self.counter + 1
                    # print(self.counter)
                self.status_of_the_service('rapidrecovery-vdisk', 0)
            if self.install_distname() in ["rhel", "centos", "oracle", "sles", "suse"]:
                if self.error_code_of_the_service('rapidrecovery-vdisk') is not 0:
                    raise Exception("The vdisk is not started by default after agent installation")
                self.rapidrecovery_config_api(build="all")
                self.service_activity('rapidrecovery-vdisk', 'restart')
                self.counter = 0
                while self.error_code_of_the_service('rapidrecovery-vdisk') is not 0 and self.counter <= 12:
                    time.sleep(5)
                    self.counter = self.counter + 1
                if self.error_code_of_the_service('rapidrecovery-vdisk') is not 0:
                    print(self.error_code_of_the_service('rapidrecovery-vdisk'))
                    raise Exception("ERROR: Rapidrecovery-vdisk is not 0 even after start command.")

            if self.error_code(self.nbd_check) is not 0:
                raise Exception("ERROR: There are no open nbd device.")

            counter = 0
            while str(self.rapidrecovery_vss_installed().rstrip()) != str(
                    "installed") and counter <= 6:
                """We are awiting until rapidrecovery-vss is build on the box"""
                time.sleep(5)
                counter = counter + 1

            if self.bsctl_hash() != self.rapidrecovery_vss_hash():
                """we assume, that if agent is started without configuring, module
                should be loaded automaticaly. Here we are comparing versions
                of the bsctl and rapidrecovery-vss"""
                raise Exception('There is missmatch in the bsctl -v and rapidreco'
                                'very-vss versions')
            self.service_activity('rapidrecovery-agent', 'restart')
            self.status_of_the_service('rapidrecovery-agent', 0)
            self.status_of_the_service('rapidrecovery-vdisk', 0) # rapidrecovery-vdisk should not be linked with the agent

            self.service_activity('rapidrecovery-agent', 'stop')
            if self.check_initd() in "/etc/init.d":
                self.status_of_the_service('rapidrecovery-agent', 1) #seems like 3 is return when service is not running. Needs to be clarified. INIT.
            else:
                self.status_of_the_service('rapidrecovery-agent', 3) #seems like 3 is return when service is not running. Needs to be clarified. SYSTEMD.

            self.status_of_the_service('rapidrecovery-vdisk', 0) # rapidrecovery-vdisk should not be linked with the agent

            self.service_activity('rapidrecovery-agent', 'start')
            self.status_of_the_service('rapidrecovery-agent', 0)

            #self.service_activity('rapidrecovery-agent', 'reload')
            #print("I am here after reload")
            #self.status_of_the_service('rapidrecovery-agent', 3) #Here is bug : RR-103626. Once is fixed, make sure that agent is running, so, exit code should be 0

            self.status_of_the_service('rapidrecovery-vdisk', 0) # rapidrecovery-vdisk should not be linked with the agent

        except Exception as e:
            print(e)
            raise e


            # TODO: /etc/services needs to be updated with the port entries. Example: 8006 port on the agent startup.
