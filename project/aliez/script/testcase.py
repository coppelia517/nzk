import os
import sys
import glob
import time
import random

from stve.log import Log
from stve.exception import *

from aliez.capture import MinicapProc
from aliez.utility import *
from aliez.script import testcase_base
from aliez.resource import Parser as P

L = Log.get(__name__)


class TestCase_Base(testcase_base.TestCase_Unit):
    def __init__(self, *args, **kwargs):
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
        stream = cls.service["aliez.stve.minicap"].get_stream(cls.get("minicap.ip"), cls.get("minicap.port"))
        proc = cls.service["aliez.stve.minicap"].get_process(LOG_DIR)
        cls.minicap = MinicapProc(stream, proc, debug=cls.get("args.debug"))

    def minicap_start(self):
        self.minicap.start(self.adb)

    def minicap_finish(self):
        self.minicap.finish(); time.sleep(2)

    def minicap_screenshot(self, filename=None):
        if filename == None: filename = "capture.png"
        return self.minicap.capture_image(filename)

    def minicap_create_video(self):
        self.minicap.create_video(TMP_EVIDENCE_DIR, TMP_VIDEO_DIR)

    def sleep(self, base=3):
        sleep_time = (base - 0.5 * random.random())
        time.sleep(sleep_time)

    def debug(self):
        return self.get("args.debug")
