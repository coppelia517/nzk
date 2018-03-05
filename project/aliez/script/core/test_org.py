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
        self.minicap_start()
        self.sleep(3)
        self.minicap_screenshot()
        self.sleep(3)
        self.minicap_finish(); self.sleep(3)
        self.minicap_create_video()

    @classmethod
    def tearDownClass(cls):
        info("*** End TestCase     : %s *** " % __name__)
