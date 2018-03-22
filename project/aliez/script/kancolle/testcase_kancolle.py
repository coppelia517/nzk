import os
import sys
import time
import pytest

from stve.log import Log
from aliez.utility import *
from aliez.script.kancolle import testcase_normal

L = Log.get(__name__)


class TestCase(testcase_normal.TestCase_Normal):

    def initialize(self, form=None, fleet_name=None):
        if self.adb.rotate() == 0 or (not self.exists("basic/home")):
            assert self.login()
            while self.expedition_result(): self.sleep(1)
            #return self.wait("basic/home")
        self.tap_check("home/formation")
        self.message(self.get("bot.formation"))
        if form == None: return self.home()
        else: return self.formation(form, fleet_name)

    def supply_all(self):
        if not self.exists("basic/home"): return False
        self.tap_check("home/supply"); self.sleep()
        fleets = []
        for fleet in range(2, 5):
            if not self.exists(self.fleet_focus(fleet)):
                self.tap_check(self.fleet(fleet))
            if self.exists("supply/vacant"):
                self.tap("supply")
                self.sleep()
                fleets.append(fleet)
        return self.home(), fleets

    def expedition_all(self, fleets):
        if not self.exists("basic/home"): return False
        self.tap_check("home/attack"); self.sleep()
        assert self.exists("expedition")
        self.message(self.get("bot.expedition"))
        self.tap("expedition"); self.sleep(4)
        for fleet in fleets:
            fleet = str(fleet)
            id = self.get("expedition.fleet_%s" % fleet)
            L.debug("fleet Number : %s." % fleet)

            self.expedition_stage(id)
            self.expedition_id(id); self.sleep()

            if self.exists("expedition/done"):
                self.message(self.get("bot.expedition_done") % fleet)
            else:
                self.tap_check("expedition/decide")
                if not self.exists("expedition/fleet_focus", _id=fleet):
                    self.tap("expedition/fleet", _id=fleet)
                    self.sleep()
                if self.exists("expedition/unable"):
                    self.message(self.get("bot.expedition_unable") % fleet)
                else:
                    if self.exists("expedition/rack"):
                        self.message(self.get("bot.expedition_unable") % fleet)
                    else:
                        self.tap("expedition/start"); self.sleep(5)
                        if self.exists("expedition/done"):
                            self.message(self.get("bot.expedition_start") % fleet); self.sleep(3)
                            assert self.wait("expedition/icon")
                            self.upload("expedition_%s.png" % self.adb.get().SERIAL)
                        else:
                            self.message(self.get("bot.expedition_unable") % fleet)
        return self.home()

    def quest_receipt(self, _id):
        assert self.quest_open()
        result = self.quest_search(_id)
        return result, self.quest_upload()

    def quest_receipt(self, _ids, _remove=False):
        assert self.quest_open()
        for _id in _ids:
            self.quest_search(_id, remove=_remove)
        return self.quest_upload()

    def quest_supply(self):
        assert self.quest_open()
        self.quest_search("DS01"); self.sleep(1)
        self.quest_search("DS02"); self.sleep(1)
        return self.quest_upload()

    def exercises(self):
        if not self.exists("basic/home"): return False
        self.tap_check("home/attack"); self.sleep()
        self.tap("exercises"); self.sleep(4)
        if not self.exists("exercises/select"):
            self.home(); return False
        p = POINT(self.conversion_w(int(self.adb.get().EXERCISES_X)),
                  self.conversion_h(int(self.adb.get().EXERCISES_Y)),
                  self.conversion_w(int(self.adb.get().EXERCISES_WIDTH)),
                  self.conversion_h(int(self.adb.get().EXERCISES_HEIGHT)))
        flag = True
        for _ in range(5):
            if self.exists("exercises/win", area=p):
                L.info("I'm already fighting. I won.")
            elif self.exists("exercises/lose", area=p):
                L.info("I'm already fighting. I lost.")
            else:
                L.info(p);
                self._tap(p, threshold=0.49); self.sleep(3)
                fname = self.capture("exercises_%s.png" % self.adb.get().SERIAL)
                if self.exists("exercises/x"):
                    self.tap("exercises/decide"); self.sleep()
                    if self.exists("exercises/unable"):
                        self.tap_check("exercises/return"); self.sleep()
                        self.tap_check("exercises/x"); self.sleep()
                        self.home(); return False
                    self.upload_file(fname)
                    if self.tap_check("exercises/start"):
                        self.message(self.get("bot.exercises_start")); self.sleep(5)
                        self.exercises_battle(); flag = False
                        break
            self.sleep(1)
            if self.adb.get().LOCATE == "V":
                p.x = int(p.x) - int(p.width); L.info("Point : %s" % str(p))
            else:
                p.y = int(p.y) + int(p.height); L.info("Point : %s" % str(p))
        if flag:
            self.message(self.get("bot.exercises_result"))
            self.upload()
            self.home(); return False
        self.sleep(3)
        return self.wait("basic/home")

    def exercises_battle(self):
        self.tap("attack/formation/1")
        while not self.exists("basic/next"):
            self.sleep(15)
            if self.tap("attack/night_battle/start", wait=False):
                self.message(self.get("bot.night_battle_start"))
                self.sleep()
        self.sleep(2)
        if self.exists("attack/result/d"): self.message(self.get("bot.result_d"))
        elif self.exists("attack/result/c"): self.message(self.get("bot.result_c"))
        elif self.exists("attack/result/b"): self.message(self.get("bot.result_b"))
        elif self.exists("attack/result/a"): self.message(self.get("bot.result_a"))
        else: self.message(self.get("bot.result_s"))
        self.sleep(5)
        while self.exists("basic/next"):
            self.tap("basic/next"); self.sleep(5)
        while not self.exists("basic/home"):
            self.tap("basic/next"); self.sleep(5)
        return True

    def attack(self, fleet, id):
        if not self.exists("basic/home"): return False
        self.tap_check("home/attack"); self.sleep()
        assert self.exists("attack")
        self.message(self.get("bot.attack"))
        self.tap("attack"); self.sleep(4)
        assert self.exists("attack/icon"); self.sleep(2)
        self.__attack_stage(id)
        self.__attack_extra(id)
        self.__attack_id(id)
        if not self.exists("attack/decide"):
            self.home(); return False
        self.tap_check("attack/decide"); self.sleep()
        if not self.exists(self.fleet_focus(fleet)):
            self.tap_check(self.fleet(fleet)); self.sleep(2)
        if self.exists("attack/rack"):
            self.message(self.get("bot.attack_rack")); self.home(); return True
        if self.exists("attack/damage"):
            self.message(self.get("bot.attack_damage")); self.home(); return True
        if not self.__leveling_status_check_leveling():
            L.critical("Not Enough.")
            return self.home()
        if self.tap_check("attack/start"): self.sleep(7)
        if self.exists("attack/unable"):
            self.message(self.get("bot.attack_failed"))
            self.home(); return False
        self.message(self.get("bot.attack_success"))
        return self.wait("attack/compass_b")

