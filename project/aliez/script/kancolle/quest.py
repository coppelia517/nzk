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

            info(" *** Quest. *** ", cr=False)
            while self.expedition_result(): self.sleep()
            find, result = self.quest_receipt(q)
            if find:
                assert result

                info("*** select Attack Stage. 3-2 ***", cr=False)
                while self.expedition_result(): self.sleep()
                assert self.leveling(self.get("leveling.fleet"), self.get("leveling.stage"))

                info("*** Test TearDown. ***", cr=False)
                while self.expedition_result(): self.sleep()
                assert False
            else:
                while self.expedition_result(): self.sleep()
                # self.call_job_tree(q)
                self.minicap_finish(); self.sleep()

        except Exception as e:
            while self.expedition_result(): self.sleep()
            # self.invoke_quest_job(q)
            self.minicap_finish(); self.sleep()
            L.warning(type(e).__name__ + ": " + str(e))
            assert False

    @classmethod
    def tearDownClass(cls):
        info("*** End TestCase     : %s *** " % __name__)
