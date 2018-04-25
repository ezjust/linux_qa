from __future__ import print_function
import sys
import os
sys.path.append(os.path.abspath('.'))
from my_utils.web import *

class ForceSnapshot(WebAgent):

    link = None

    def setUp(self):
        self.open_core_ui()

    def tearDown(self):
        self.driver.get_screenshot_as_file(filename="/tmp/snapshot_image.png")
        self.remove_agent_by_id(ip_machine)
        self.driver.close()


    def runTest(self):
        self.protect_new_agent(ip_machine, username_machine, password_machine)
        self.status(ip_machine)
        self.force_snapshot(ip_machine, base=True)
        self.status(ip_machine)
        self.force_snapshot(ip_machine, base=False)
        self.status(ip_machine)

