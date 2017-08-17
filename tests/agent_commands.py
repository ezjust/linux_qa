from __future__ import print_function
from my_utils.system import *

class AgentCommands(Agent):
    build = "7.0.0"
    counter = 0
    link = None

    def __init__(self):
        super(Repoinstall, self).__init__()

    def setUp(self):
        self.unload_module()
        self.install_agent_fromrepo()

    def tearDown(self):
        pass
        self.uninstall_agent()
        self.unload_module()

    def runTest(self):
        try:
            self.check_package_installed('rapidrecovery-repo', expected_result=True)
            self.check_package_installed('rapidrecovery-agent', expected_result=True)
            self.check_package_installed('rapidrecovery-mono', expected_result=True)

            self.check_package_installed('dkms', expected_result=True)

            self.service_activity('rapidrecovery-agent', 'start') # we are restaring agent. Agent has not been configured yet.
            print("next")
            self.status_of_the_service('rapidrecovery-agent', 0) # agent now should be running

            while self.error_code_of_the_service('rapidrecovery-vdisk') is not 0 and self.counter <= 12:
                time.sleep(5)
                self.counter = self.counter + 1
                print(self.counter)
                print("waining")

            self.status_of_the_service('rapidrecovery-vdisk', 0)

            if self.execute.error_code(self.nbd_check) is not 0:
                raise Exception("ERROR: There are no open nbd device.")

            while str(self.rapidrecovery_vss_installed().rstrip()) != str(
                    "installed"):
                """We are awiting until rapidrecovery-vss is build on the box"""
                time.sleep(5)
                pass

            if self.bsctl_hash() != self.rapidrecovery_vss_hash():

                """we assume, that if agent is started without configuring, module
                should be loaded automaticaly. Here we are comparing versions
                of the bsctl and rapidrecovery-vss"""
                raise Exception('There is missmatch in the bsctl -v and rapidreco'
                                'very-vss versions')

            self.service_activity('rapidrecovery-agent', 'restart')
            self.status_of_the_service('rapidrecovery-agent', 0)
            self.status_of_the_service('rapidrecovery-vdisk', 0) # rapidrecovery-vdisk should not be linked with the agent
            print("restart option is completed")

            self.service_activity('rapidrecovery-agent', 'stop')
            self.status_of_the_service('rapidrecovery-agent', 3) #seems like 3 is return when service is not running. Needs to be clarified.
            self.status_of_the_service('rapidrecovery-vdisk', 0) # rapidrecovery-vdisk should not be linked with the agent
            print("stop option is completed")

            self.service_activity('rapidrecovery-agent', 'start')
            self.status_of_the_service('rapidrecovery-agent', 0)

            #self.service_activity('rapidrecovery-agent', 'reload')
            #print("I am here after reload")
            #self.status_of_the_service('rapidrecovery-agent', 3) #Here is bug : RR-103626. Once is fixed, make sure that agent is running, so, exit code should be 0

            self.status_of_the_service('rapidrecovery-vdisk', 0) # rapidrecovery-vdisk should not be linked with the agent

        except Exception as e:
            print(e)
            raise Exception("EXCEPTION:: Failed some test action")


            # TODO: /etc/services needs to be updated with the port entries. Example: 8006 port on the agent startup.
