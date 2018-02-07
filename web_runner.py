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
        path_ = "%s/%s" % (os.path.abspath('.'), "web_tests")
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
        self.test_list = dict(self.conf_parser.items("web_tests"))


    def setup(self):
        self.get_tests_list()

    def teardown(self):
        pass

    def open_log(self):
        self.result_log = open("result.log", 'a+')

    def write_log(self, message):
        self.message = message
        print("Wrote")
        result_log = open("result.log", 'a+')
        result_log.write(self.message)
        result_log.write("TESTING")
        result_log.close()

    def close_log(self):
        #self.result_log = open("result.log", 'a+')
        self.result_log.close()

    def remove_log(self):
        if os.path.isfile('result.log'):
            os.remove('result.log')
            print('REMOVED RESULT.LOG')

    def run_tests(self):
        result = True
        stat_loops = TestsStat()
        self.setup()
        self.read_cfg()
        print("----------------------")
        # print("test_list.items()")
        # print(self.test_list.items())
        # print("test_classes.items()")
        # print(self.test_classes.items())
        # print("test_modules.items()")
        # print(self.test_modules.items())
        print("----------------------")
        for key, value in self.test_list.items():
            #  if key == "InstallAgent" and int(value) == 1:
            if int(value) == 1:
                # print(key)
                key_word = key
                for key, value in self.test_modules.items():
                    if value == key_word:
                        # print(key)
                        key_modules = key
                        for key, value in self.test_classes.items():
                            if key == key_modules:
                                try:
                                    test = value()
                                    self.executor.log(
                                        "Setting Up %s test .....\n" % key_modules)
                                    test.setUp()
                                    self.executor.log(
                                        "Running %s test ........\n" % key)
                                    stat_loops.started +=1 #increment started count before runTest and after setUp
                                    test.runTest()
                                    self.executor.log("Completed %s test ......\n" % key)
                                    stat_loops.passed +=1 #increment passed in case if run
                                    print("%s" % ('Test %s is: ''OK') % key_modules)
                                    result = "passed"
                                except Exception as e:
                                    stat_loops.failed +=1
                                    self.executor.log(e)
                                    print("%s" % ('Test %s is: ''FAIL') % key)
                                    result = "failed"
                                finally:
                                    self.executor.log("Cleaning Up %s test ....\n" % key)
                                    test.tearDown()
                                    print("Test %s is: %s\n" % (key, ('OK' if result is "passed" else 'FAIL')))
                                    self.write_log(message="Test %s is: %s\n" % (key, ('OK' if result is "passed" else 'FAIL')))
                                    print("================================================================="
                                                  "\n"
                                                  "\n"
                                          "=================================================================")

        self.executor.log("\vTests are finished. %d are OK, %d are FAILED\n" % (stat_loops.passed, stat_loops.failed))
        #         print(self.test_list.values())
        #         print(self.test_classes.get([key]))
        #         result = None
        #         try:
        #             self.executor.log("%s test :\n" % key)
        #             test = self.test_classes[key]()
        #             print(test)
        #             print("123")
        #
        #             print(test)
        #             print("125")
        #             self.executor.log("Setting Up %s test .....\n" % key)
        #             test.setUp()
        #             #self.executor.log("Done")
        #             self.executor.log("Running %s test ........\n" % key)
        #             stat_loops.started +=1 #increment started count before runTest and after setUp
        #             #self.executor.log("Done")
        #             test.runTest()
        #             self.executor.log("Completed %s test ......\n" % key)
        #             stat_loops.passed +=1 #increment passed in case if run
        #             #self.executor.log("Done")
        #             #print("%s" % ('Test %s is: ''OK') % key)
        #             result = "passed"
        #         # except Exception as e:
        #         #     stat_loops.failed +=1
        #         #     self.executor.log(e)
        #         #     print("%s" % ('Test %s is: ''FAIL') % key)
        #         #     result = "failed"
        #         finally:
        #             self.executor.log("Cleaning Up %s test ....\n" % key)
        #             test.tearDown()
        #             #self.executor.log("Done")
        #         print("Test %s is: %s\n" % (key, ('OK' if result is "passed" else 'FAIL')))
        #         print("================================================================="
        #               "\n"
        #               "\n"
        #               "=================================================================")
        #
        # self.executor.log("\vTests are finished. %d are OK, %d are FAILED\n" % (stat_loops.passed, stat_loops.failed))

        #    test = self.test_classes[key]()
        #   test.runTest()


if __name__ == '__main__':
    test_obj = TestRunner()
    test_obj.run_tests()

