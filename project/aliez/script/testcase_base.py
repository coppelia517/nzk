import os
import sys
import time
import unittest
import argparse
try:
    import configparser
except:
    import ConfigParser as configparser


from stve import library
from stve.log import Log
from aliez.utility import *

L = Log.get(__name__)

class TestCase_Unit(unittest.TestCase):
    config = {}
    service = library.register(library.register(), LIB_DIR)

    def __init__(self, *args, **kwargs):
        super(TestCase_Unit, self).__init__(*args, **kwargs)
        self.__parse()

    @classmethod
    def set(cls, name, value):
        cls.config[name] = value

    @classmethod
    def get(cls, name):
        return cls.config.get(name)

    def __parse(self):
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        parser = self.arg_parse(parser)

        results = parser.parse_args()
        for k, v in vars(results).items():
            self.set("args.%s" % k, v)

    def arg_parse(self, parser):
        parser.add_argument(action='store', dest='testcase', help='TestCase Name.')
        # parser.add_argument("-p", "--package", action='store', dest='package', help='TestCase Package Name.')

        parser.add_argument("--debug", action='store_true', default=False, dest="debug", help="Debug Flag.")
        return parser

    @classmethod
    def get_service(cls, settings):
        pass

    def get_config(cls, conf=None):
        if cls.get("args.package") != None: host = os.path.join(SCRIPT_DIR, cls.get("args.package"))
        else: host = SCRIPT_DIR

        if conf == None: conf = os.path.join(host, "config.ini")
        else: conf = os.path.join(host, "config", conf + ".ini")

        try:
            config = configparser.RawConfigParser()
            cfp = open(conf, 'r')
            config.readfp(cfp)
            for section in config.sections():
                for option in config.options(section):
                    cls.set("%s.%s" % (section, option), config.get(section, option))
        except Exception as e:
            L.warning('error: could not read config file: %s' % str(e))
