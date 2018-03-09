import pytest
import unittest


from stve.log import Log
from aliez.utility import *
from aliez.script import testcase

L = Log.get(__name__)
def info(string, cr=True):
    desc(string, L, cr)

class TestCase(testcase.TestCase_Base):
    def __init__(self, *args, **kwargs):
        super(TestCase, self).__init__(*args, **kwargs)

    @classmethod
    def setUpClass(cls):
        info("*** Start TestCase   : %s *** " % __name__)

    def test_1(self):
        info("*** Test Original. ***", cr=False)
        try:
            self.minicap_start()
            self.adb.stop(self.get("settings.app")); self.sleep()
            self.adb.invoke(self.get("settings.app")); self.sleep()
            assert self.exists("settings")

            while not self.exists("settings/device_info"):
                x = str(int(self.adb.get().WIDTH) / 2)
                self.adb.input("swipe %s %s %s %s" % (x, self.adb.get().HEIGHT, x, "0")); self.sleep()

            assert self.exists("settings/device_info")
            self.tap("settings/device_info")

            while not self.exists("settings/device_info/build_number"):
                x = str(int(self.adb.get().WIDTH) / 2)
                self.adb.input("swipe %s %s %s %s" % (x, self.adb.get().HEIGHT, x, "0")); self.sleep()

            filename = self.minicap_screenshot("result.png")
            _box = POINT(25, 1115, (200-25), (1150 - 1115))
            L.info(_box)
            L.info(self.ocr.img_to_string(filename, "eng", _box, TMP_DIR))

            self.minicap_finish(); self.sleep(3)
        except Exception as e:
            L.warning(type(e).__name__ + ": " + str(e))
            self.minicap_finish(); self.sleep(2)
            self.minicap_create_video()


    @classmethod
    def tearDownClass(cls):
        info("*** End TestCase     : %s *** " % __name__)
