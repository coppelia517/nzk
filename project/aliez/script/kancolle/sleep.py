import pytest
import time

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
        info("*** Debug Flag : %s ***" % str(cls.get("args.debug")))

    def test_maintenance(self):
        info("*** Test SetUp. ***", cr=False)
        self.message(self.get("bot.sleep"))
        timeout = int(self.get("args.timeout"))
        L.debug("Timeout : %d " % (timeout * 1800))
        self.adb.stop(self.get("kancolle.app"))
        time.sleep(timeout * 1800)
        self.message(self.get("bot.sleep_out"))

    @classmethod
    def tearDownClass(cls):
        info("*** End TestCase     : %s *** " % __file__)
