from __future__ import print_function
from my_utils.system import *

class AgentCommands(Agent):
    build = "7.0.0"
    link = None

    def __init__(self):
        super(Repoinstall, self).__init__()

    def setUp(self):
        self.unload_module()
        self.install_agent_fromrepo()

    def tearDown(self):
        pass
        #self.uninstall_agent()
        #self.unload_module()

    def runTest(self):

        self.install_agent_fromrepo()
        self.check_package_installed('rapidrecovery-repo', True)
        self.check_package_installed('rapidrecovery-agent', True)
        self.check_package_installed('rapidrecovery-mono', True)
        self.check_package_installed('dkms', True)
        self.service_activity('rapidrecovery-agent', 'start') # we are restaring agent
        self.status_of_the_service('rapidrecovery-agent', 0) # agent now should be running
        self.status_of_the_service('rapidrecovery-vdisk', 0)
        if self.execute.error_code(self.nbd_check) is not 0:
            raise Exception("ERROR: There are no open nbd device.")

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
        self.status_of_the_service('rapidrecovery-agent', 3) #seems like 3 is return when service is not running. Needs to be clarified.
        self.status_of_the_service('rapidrecovery-vdisk', 0) # rapidrecovery-vdisk should not be linked with the agent


        self.service_activity('rapidrecovery-agent', 'reload')
        self.status_of_the_service('rapidrecovery-agent', 3) #Here is bug : RR-103626. Once is fixed, make sure that agent is running, so, exit code should be 0
        self.status_of_the_service('rapidrecovery-vdisk', 0) # rapidrecovery-vdisk should not be linked with the agent


        #TODO: /etc/services needs to be updated with the port entries. Example: 8006 port on the agent startup.
