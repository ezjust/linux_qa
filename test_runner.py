from __future__ import print_function
import sys
import os
import pkgutil
import ConfigParser
from my_utils.system import Executor
from tests.install_agent import InstallAgent


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

    def __init__(self):
        self.executor = Executor()

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
        pass

    def teardown(self):
        pass



    def run_tests(self):
        self.setup()
        self.read_cfg()

        for key, value in self.test_list.items():
          #  if key == "InstallAgent" and int(value) == 1:
            if int(value) == 1:
                test = self.test_classes[key]()
                test.setUp()
                test.runTest()
                test.tearDown()

            #    test = self.test_classes[key]()
            #   test.runTest()


