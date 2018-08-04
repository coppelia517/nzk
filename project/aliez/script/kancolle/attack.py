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

    def test_quest(self):
        q = self.get("args.quest")
        info("*** Quest '%s' ***" % self.get("%s.name" % q))
        self.message(self.get("%s.name" % q))

        try:
            self.minicap_start(); self.sleep()

            info("*** Test SetUp. ***", cr=False)
            assert self.initialize(self.get("%s.composition" % q), self.get("%s.fleet_name" % q))
            
            info("*** select Attack Stage. ***", cr=False)
            while self.expedition_result(): self.sleep()
            assert self.attack(self.get("%s.fleet" % q),
                                self.get("%s.stage" % q),
                                self.get("%s.status" % q))

            info(" *** Attack. *** ", cr=False)
            if self.get("%s.stage" % q) == "14":
                assert self.battle_leveling(self.get("%s.formation" % q))
            else:
                assert self.battle_quest(self.get("%s.formation" % q), self.get("%s.status" % q))

            info("*** Supply & Docking Start. ***", cr=False)
            while self.expedition_result(): self.sleep()
            assert self.supply_and_docking(self.get("%s.fleet" % q))

            info("*** Test TearDown. ***", cr=False)
            while self.expedition_result(): self.sleep()
            assert False

        except Exception as e:
            while self.expedition_result(): self.sleep()
            self.minicap_finish(); self.sleep()
            L.warning(type(e).__name__ + ": " + str(e))
            assert False

    @classmethod
    def tearDownClass(cls):
        info("*** End TestCase     : %s *** " % __name__)
