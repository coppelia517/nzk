import os
import sys
import glob

from stve import library
from stve.exception import *

from aliez.utility import *
from aliez.script import testcase_base
from aliez.resource import Parser as P

class TestCase_Base(testcase_base.TestCase_Unit):
    def __init__(self, *args, **kargs):
        super(TestCase_Base, self).__init__(*args, **kwargs)
        self.get_config(self.get("args.config"))
        self.get_service()

    def arg_parse(self, parser):
        super(TestCase_Base, self).arg_parse(parser)
        parser.add_argument("-s", "--serial", action='store', dest="serial", help="Android Serial.")
        parser.add_argument("-c", "--config", action='store', dest="config", help="Config File Name.")
        return parser

    @classmethod
    def get_service(cls):
        if cls.get("args.package") != None:
            prof = os.path.join(SCRIPT_DIR, cls.get("args.package"), "profile")
            cls.adb = cls.service["stve.android"].get(cls.get("args.serial"), prof)
        else:
            cls.adb = cls.service["stve.android"].get(cls.get("args.serial"))
        cls.pic = cls.service["stve.picture"].get()
