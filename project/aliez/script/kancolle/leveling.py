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

    def test_leveling(self):
        try:
            self.minicap_start(); self.sleep()

            info("*** Test SetUp. ***", cr=False)
            assert self.initialize(
                self.get("leveling.composition"), fleet_name=self.get("leveling.fleet_name"))

            info("*** Quest Check. ***", cr=False)
            while self.expedition_result(): self.sleep()
            assert self.quest_supply()

            info("*** select Attack Stage. 3-2 ***", cr=False)
            while self.expedition_result(): self.sleep()
            assert self.leveling(self.get("leveling.fleet"), self.get("leveling.stage"))

            info("*** Attack Stage. 3-2 ***", cr=False)
            assert self.battle_leveling(self.get("leveling.fleet"))

            info("*** Supply & Docking Start. ***", cr=False)
            while self.expedition_result(): self.sleep(1)
            assert self.supply_and_docking(self.get("leveling.fleet"))

            info("*** Test TearDown. ***", cr=False)
            while self.expedition_result(): self.sleep()


            self.minicap_finish(); self.sleep()

        except Exception as e:
            self.minicap_finish(); self.sleep()
            L.warning(type(e).__name__ + ": " + str(e))
            self.minicap_create_video()
            assert False

    @classmethod
    def tearDownClass(cls):
        info("*** End TestCase     : %s *** " % __name__)
