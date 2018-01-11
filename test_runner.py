from __future__ import print_function

import ConfigParser
import os
import pkgutil

from my_utils.system import Executor
from tests import *


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


import imp


def __import__(name, globals=None, locals=None, fromlist=None):
    # First path: see if module has already been imported
    try:
        """ Ensure that module isn't already loaded """
        return sys.modules[name]
    except KeyError:
        pass

    fp, pathname, descr = imp.find_module(name)

    try:
        return imp.load_module(name, fp, pathname, descr)
    finally:
        if fp:
            fp.close()

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
            self.test_classes.update({class_name: getattr(loaded_mod, class_name)})
            # self.test_classes[class_name] = getattr(loaded_mod, class_name)
            self.test_modules[class_name] = mod_name
        sys.path.remove(path_)

        # return


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

            test = None
            #  if key == "InstallAgent" and int(value) == 1:
            if int(value) == 1:
                result = None
                try:
                    #self.executor.log("%s test :\n" % key)
                    # test = self.test_classes[key]
                    test = self.test_classes[key]()
                    # print("print test ", test)
                    # test = test()

                    # print(test.__dict__)
                    # print("================", test)
                    #exit(1)
                    self.executor.log("Setting Up %s test .....\n" % key)
                    test.setUp()
                    #self.executor.log("Done")
                    self.executor.log("Running %s test ........\n" % key)
                    stat_loops.started +=1 #increment started count before runTest and after setUp
                    #self.executor.log("Done")
                    test.runTest()
                    self.executor.log("Completed %s test ......\n" % key)
                    stat_loops.passed +=1 #increment passed in case if run
                    #self.executor.log("Done")
                    #print("%s" % ('Test %s is: ''OK') % key)
                    result = "passed"
                except Exception as e:
                    stat_loops.failed +=1
                    self.executor.log(e)
                    #print("%s" % ('Test %s is: ''FAIL') % key)
                    result = "failed"
                finally:
                    self.executor.log("Cleaning Up %s test ....\n" % key)
                    test.tearDown()
                    #self.executor.log("Done")
                print("Test %s is: %s\n" % (key, ('OK' if result is "passed" else 'FAIL')))
                print("================================================================="
                      "\n"
                      "\n"
                      "=================================================================")

        self.executor.log("\vTests are finished. %d are OK, %d are FAILED\n" % (stat_loops.passed, stat_loops.failed))

        #    test = self.test_classes[key]()
        #   test.runTest()




        # TODO: Move from web_runner and test_runner all needed fucntions of the create and write to file into parser.py file in my.utils.