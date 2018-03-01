import pytest
import unittest


from stve.log import Log
from aliez.utility import *
from aliez.script import testcase_base

L = Log.get(__name__)
def info(string, cr=True):
    desc(string, L, cr)

class TestCase(testcase_base.TestCase_Unit):
    def __init__(self, *args, **kwargs):
        super(TestCase, self).__init__(*args, **kwargs)

    @classmethod
    def setUpClass(cls):
        info("*** Start TestCase   : %s *** " % __name__)

    def test_1(self):
        info("*** Test Original. ***", cr=False)
        assert True

    def test_2(self):
        info("*** Test Original. ***")
        assert True

    @classmethod
    def tearDownClass(cls):
        info("*** End TestCase     : %s *** " % __name__)
