from __future__ import print_function
import sys
import os
import pkgutil
import ConfigParser
from my_utils.system import Executor
from tests.install_repo import InstallRepo
from tests.install_agent import *

class TestsStat(object):
    started = 0
    passed = 0
    failed = 0
    def add(self, stat):
        self.started += stat.started
        self.passed += stat.passed
        self.failed += stat.failed



def get_class_name(mod_name):
        """ Return the class name from a plugin name """
        output = ""

        # Split on the _
        words = mod_name.split("_")[0:]

        # Capitalise the first letter of each word and add to string
        for word in words:
            output += word.title()

        return output

class TestRunner(object):

    conf_file = None
    test_classes = {}
    test_modules = {}
    executor = Executor()

    def __init__(self):
        self.success_count = 0
        self.fail_count = 0

    def get_tests_list(self):
        # Read tests directory and import test classes
        path_ = "%s/%s" % (os.path.dirname(__file__), "tests")
        sys.path.append(path_)
        modules = pkgutil.iter_modules(path=[path_])

        for loader, mod_name, ispkg in modules:
            # Import module
            loaded_mod = __import__(mod_name, fromlist=[mod_name])
            # Load class from imported module
            class_name = get_class_name(mod_name)
            self.test_classes[class_name] = getattr(loaded_mod, class_name)
            self.test_modules[class_name] = mod_name
        sys.path.remove(path_)

        return


    def read_cfg(self):
        conf_file = "config.ini"
        self.conf_parser = ConfigParser.ConfigParser()
        self.conf_parser.optionxform = str
        self.conf_parser.readfp(open(conf_file))
        self.test_list = dict(self.conf_parser.items("tests"))


    def setup(self):
        self.get_tests_list()

    def teardown(self):
        pass



    def run_tests(self):
        result = True
        stat_loops = TestsStat()
        self.setup()
        self.read_cfg()
        for key, value in self.test_list.items():
            #  if key == "InstallAgent" and int(value) == 1:
            if int(value) == 1:
                # print(self.test_classes[key])
                result = None
                try:
                    self.executor.log("%s test :" % key)
                    test = self.test_classes[key]()
                    self.executor.log("Setting Up %s test ....." % (key)),
                    test.setUp()
                    self.executor.log("Done")
                    self.executor.log("Running %s test ........" % key),
                    stat_loops.started +=1 #increment started count before runTest and after setUp
                    self.executor.log("Done")
                    test.runTest()
                    self.executor.log("Completed %s test ......" % key),
                    stat_loops.passed +=1 #increment passed in case if run
                    self.executor.log("Done")
                    #print("%s" % ('Test %s is: ''OK') % key)
                    result = "passed"
                except Exception as e:
                    stat_loops.failed +=1
                    self.executor.log(e)
                    #print("%s" % ('Test %s is: ''FAIL') % key)
                    result = "failed"
                finally:
                    self.executor.log("Cleaning Up %s test ...." % key),
                    test.tearDown()
                    self.executor.log("Done")
                print("Test %s is: %s\n" % (key, ('OK' if result is "passed" else 'FAIL')))

        self.executor.log("\vTests are finished. %d are OK, %d are FAILED\n" % (stat_loops.passed, stat_loops.failed))

        #    test = self.test_classes[key]()
        #   test.runTest()




