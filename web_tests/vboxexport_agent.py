from __future__ import print_function
import sys
import os
sys.path.append(os.path.abspath('.'))
from my_utils.web import *

class VboxexportAgent(WebAgent):

    link = None

    def setUp(self):
        self.open_core_ui()

    def tearDown(self):
        self.driver.get_screenshot_as_file(filename="/tmp/autobmr_image")
        self.remove_agent_by_id(ip_machine)
        self.driver.close()


    def runTest(self):
        self.protect_new_agent(ip_machine, username_machine, password_machine)
        self.status(ip_machine)
        self.export_vbox(ip_machine, vbox_export_vmname, ip_livecd, pass_livecd)
        self.status(ip_machine)
        self.export_vbox_bootable(ip_machine, vbox_export_vmname)