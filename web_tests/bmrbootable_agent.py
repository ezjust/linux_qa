from __future__ import print_function
import sys
import os
sys.path.append(os.path.abspath('.'))
from my_utils.web import *


class BmrbootableAgent(WebAgent):

    link = None

    def setUp(self):
        self.open_core_ui()

    def tearDown(self):
        self.driver.get_screenshot_as_file(filename="/tmp/bmrbootable_image")
        self.remove_agent_by_id(ip_machine)
        self.driver.close()


    def runTest(self):
        self.protect_new_agent(ip_machine, username_machine, password_machine)
        self.status(ip_machine)
        self.auto_bmr(ip_machine, vbox_vmname, ip_livecd, pass_livecd)
        self.status(ip_machine)
        self.bmr_fix_boot(ip_machine, ip_livecd, pass_livecd, vbox_vmname)
        self.bmr_bootable(ip_machine, ip_livecd, pass_livecd, vbox_vmname)

