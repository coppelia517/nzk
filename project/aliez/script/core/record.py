import time
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
        info("*** Start TestCase   : %s *** " % __file__)

    def test_1(self):
        info("*** Test Original. ***", cr=False)
        try:
            self.minicap_start()
            time.sleep(60)
            self.minicap_finish()
        except Exception as e:
            L.warning(type(e).__name__ + ": " + str(e))
            self.minicap_finish(); self.sleep(2)

    @classmethod
    def tearDownClass(cls):
        info("*** End TestCase     : %s *** " % __file__)
