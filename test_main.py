import os
import sys
from test_runner import TestRunner

__author__ = 'mbugaiov'
__copyright__ = "Copyright (C) 2017 Quest, Inc.  All rights reserved"

#if os.getuid() != 0:
#    sys.exit("Please run script as root.")
ver = sys.version.split()[0]
if ver[0:3] != "2.7":
    sys.exit("Please use python version 2.7")


if __name__ == '__main__':
    test_obj = TestRunner()
    test_obj.run_tests()