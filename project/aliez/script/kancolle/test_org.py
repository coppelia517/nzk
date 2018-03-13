import pytest
import unittest


from stve.log import Log
from aliez.utility import *
from aliez.script.kancolle import testcase_normal

L = Log.get(__name__)
def info(string, cr=True):
    desc(string, L, cr)

class TestCase(testcase_normal.TestCase_Normal):
    def __init__(self, *args, **kwargs):
        super(TestCase, self).__init__(*args, **kwargs)

    @classmethod
    def setUpClass(cls):
        info("*** Start TestCase   : %s *** " % __name__)

    def test_1(self):
        info("*** Test Original. ***", cr=False)
        try:
            self.minicap_start(); self.sleep()
            assert self.initialize(0, "Second Fleet")

            self.minicap_finish(); self.sleep(3)

        except Exception as e:
            self.minicap_finish(); self.sleep(2)
            L.warning(type(e).__name__ + ": " + str(e))
            self.minicap_create_video()


    @classmethod
    def tearDownClass(cls):
        info("*** End TestCase     : %s *** " % __name__)
