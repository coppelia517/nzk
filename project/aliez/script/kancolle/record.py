import time
import pytest

from stve.log import Log
from aliez.utility import *
from aliez.script.kancolle import testcase_kancolle

L = Log.get(__name__)
def info(string, cr=True):
    desc(string, L, cr)


class TestCase(testcase_kancolle.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestCase, self).__init__(*args, **kwargs)

    @classmethod
    def setUpClass(cls):
        info("*** Start TestCase   : %s *** " % __file__)

    def test_exercises(self):
        try:
            self.minicap_start(); self.sleep()

            info("*** Test SetUp. ***", cr=False)
            assert self.initialize()
            while self.expedition_result():
                self.sleep()

            time.sleep(30)

            self.minicap_finish(); self.sleep()

        except Exception as e:
            self.minicap_finish(); self.sleep()
            L.warning(type(e).__name__ + ": " + str(e))
            #self.minicap_create_video()
            assert False

    @classmethod
    def tearDownClass(cls):
        info("*** End TestCase     : %s *** " % __name__)
