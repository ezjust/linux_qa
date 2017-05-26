from __future__ import print_function
import subprocess
import platform
import os
import sys
#import debug
#print sys.path
sys.path.append("..")
#print sys.path
from my_utils.system import *

class newclass():
    pass


class InstallAgent(Agentinstall):
    build = "7.0.0"
    link = None

    def __init__(self):
        super(Agentinstall, self).__init__()

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def runTest(self):

        print(sys.platform, "this is platform")
        print(sys.api_version, "this is api_version")

        self.create_link()
        self.download_file()
        self.run_installer()
        print("The testing of the install_agent is completed", end='\n\n')






    from my_utils.system import Executor

    #link = 	"https://s3.amazonaws.com/repolinux/$build/repo-packages/rapidrecovery-repo-$os$version-$arch.$package" -O "repo.file"



    #os = sys.platform
    #print sys.platform
    #pass
