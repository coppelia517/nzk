import os
import sys
import time
import pytest

from stve.log import Log

from aliez.utility import *
from aliez.resource import Parser as P
from aliez.script.kancolle import testcase_base

L = Log.get(__name__)


class TestCase_Normal(testcase_base.TestCase_Basic):
    def __init__(self, *args, **kwargs):
        super(TestCase_Normal, self).__init__(*args, **kwargs)

    def home(self):
        self.tap_check("menu/home"); self.sleep(base=5)
        return self.wait("basic/home")

    def login(self):
        self.adb.stop(self.get("kancolle.app")); self.sleep()
        self.adb.invoke(self.get("kancolle.app")); self.sleep()
        self.tap("basic/login/music"); self.sleep()
        self.wait("basic/login"); self.sleep(4)
        self.tap_check("basic/login"); self.sleep(5)
        return self.wait("basic/home")

    def expedition_result(self):
        if self.exists("basic/expedition"):
            self.tap_check("basic/expedition"); time.sleep(9)
            if self.wait("basic/expedition/success"):
                self.message(self.get("bot.expedition_success"))
            elif self.exists("basic/expedition/failed"):
                self.message(self.get("bot.expedition_failed"))
            self.tap("basic/next"); self.sleep()
            self.upload()
            self.tap("basic/next"); self.sleep(3)
            #self.invoke_quest_job("expedition", 60)
            return self.exists("basic/expedition")
        else:
            return False

    def initialize(self, form=None, fleet_name=None):
        if self.adb.rotate() == 0 or (not self.exists("basic/home")):
            assert self.login()
            while self.expedition_result(): self.sleep(1)
            #return self.wait("basic/home")
        self.tap_check("home/formation")
        self.message(self.get("bot.formation"))
        if form == None: return self.home()
        else: return self.formation(form, fleet_name)

    def formation(self, formation, fleet_name=None):
        self.tap_check("formation/change")
        if not self.exists("formation/deploy"): return False
        if formation == None: return False
        fleet = int(formation)
        if self.adb.get().ROTATE == "0":
            p = POINT(self.conversion_w(int(self.adb.get().FORMATION_X)) - (self.conversion_w(int(self.adb.get().FORMATION_WIDTH)) * fleet),
                      self.conversion_h(int(self.adb.get().FORMATION_Y)),
                      self.conversion_w(int(self.adb.get().FORMATION_WIDTH)),
                      self.conversion_h(int(self.adb.get().FORMATION_HEIGHT)))
        else:
            p = POINT(self.conversion_w(int(self.adb.get().FORMATION_X)),
                      self.conversion_h(int(self.adb.get().FORMATION_Y)) + (self.conversion_h(int(self.adb.get().FORMATION_HEIGHT)) * fleet),
                      self.conversion_w(int(self.adb.get().FORMATION_WIDTH)),
                      self.conversion_h(int(self.adb.get().FORMATION_HEIGHT)))
        L.info(p);
        if not self.exists("formation/fleet_1_focus"):
            self.tap_check("formation/fleet_1")
        self.tap_check("formation/select", area=p)
        assert self.exists("formation/fleet_name")
        if fleet_name != None:
            try:
                assert self.text("formation/fleet_name", fleet_name)
            except Exception as e:
                L.warning(str(e))
                return not self.home()
        self.upload("formation_%s.png" % self.adb.get().SERIAL)
        return self.home()

    def supply(self, fleet="1"):
        if not self.exists("basic/home"): return False
        self.tap_check("home/supply"); self.sleep()
        if not self.exists(self.fleet_focus(fleet)):
            self.tap(self.fleet(fleet)); self.sleep()
        if self.exists("supply/vacant"):
            self.tap("supply"); self.sleep(4)
        return self.home()

    def fleet(self, fleet):
        return "basic/fleet/%s" % fleet

    def fleet_focus(self, fleet):
        return "basic/fleet_focus/%s" % fleet

    def expedition(self, fleet, id):
        if not self.exists("basic/home"): return False
        self.sleep(2)
        self.tap_check("home/attack"); self.sleep()
        self.tap("expedition"); self.sleep(4)
        self.expedition_stage(id); self.sleep()
        self.expedition_id(id); self.sleep()
        if self.exists("expedition/done"):
            self.message(self.get("bot.expedition_done") % fleet)
            self.home(); return False
        self.tap("expedition/decide")
        if not self.exists("expedition/fleet_focus", _id=fleet):
            self.tap("expedition/fleet", _id=fleet)
        self.sleep()
        if self.exists("expedition/unable"):
            self.message(self.get("bot.expedition_unable") % fleet)
            self.home(); return False
        if self.exists("expedition/rack"):
            self.message(self.get("bot.expedition_unable") % fleet)
            self.home(); return False
        self.tap("expedition/start"); self.sleep()
        if self.exists("expedition/done"):
            self.message(self.get("bot.expedition_start") % fleet)
            self.sleep(3)
            assert self.exists("expedition/icon")
            self.upload("expedition_%s.png" % self.adb.get().SERIAL)
            return True
        else:
            self.message(self.get("bot.expedition_unable") % fleet)
            self.home(); return False

    def expedition_stage(self, id):
        if int(id) > 32:
            if not self.exists("expedition/stage/focus", _id="5"):
                self.tap("expedition/stage", _id="5")
        elif int(id) > 24:
            if not self.exists("expedition/stage/focus", _id="4"):
                self.tap("expedition/stage", _id="4")
        elif int(id) > 16:
            if not self.exists("expedition/stage/focus", _id="3"):
                self.tap("expedition/stage", _id="3")
        elif int(id) > 8:
            if not self.exists("expedition/stage/focus", _id="2"):
                self.tap("expedition/stage", _id="2")
        else:
            if not self.exists("expedition/stage/focus", _id="1"):
                self.tap("expedition/stage", _id="1")

    def expedition_id(self, id):
        self.tap("expedition/id", _id=id)

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
        return self.home()
        """
        if self.tap_check("attack/start"): self.sleep(7)
        if self.exists("attack/unable"):
            self.message(self.get("bot.attack_failed"))
            self.home(); return False
        self.message(self.get("bot.attack_success"))
        return self.wait("attack/compass_b")
        """

    def __attack_stage(self, id):
        if int(id) > 30: self.tap("attack/stage", _id="6"); self.sleep()
        elif int(id) > 24: self.tap("attack/stage", _id="5"); self.sleep()
        elif int(id) > 18: self.tap("attack/stage", _id="4"); self.sleep()
        elif int(id) > 12: self.tap("attack/stage", _id="3"); self.sleep()
        elif int(id) > 6: self.tap("attack/stage", _id="2"); self.sleep()
        else: pass

    def __attack_extra(self, id):
        if id in ["5", "6", "11", "12", "17", "18"]:
            self.tap("attack/extra"); self.sleep()


    def __attack_id(self, id):
        self.tap("attack/id", _id=id); self.sleep()

    def battle_all_stage(self, formation, withdrawal=False):
        if not self.exists("attack/compass_b"):
            if self.exists("basic/home"): return True
            else: return False
        while not self.exists("basic/home"):
            while not self.exists("basic/next"):
                if self.tap("attack/compass", wait=False): self.sleep(10)
                if self.tap("attack/formation/%s" % formation, wait=False): self.sleep(10)
                if self.tap("attack/night_battle/start", wait=False): self.sleep(15)
                #if self.exists("home"):
                #    self.message(self.get("bot.attack_return"))
                #    return self.exists("home")
                if self.exists("attack/get"):
                    self.tap("attack/return"); self.sleep(5)
                    return self.exists("basic/home")
                self.sleep(10)
            if self.tap("basic/next", wait=False): self.sleep(5)
            nextstage = "attack/charge"
            if withdrawal or self.exists("attack/result_damage"):
                nextstage = "attack/withdrawal"
            while self.tap("basic/next", wait=False): self.sleep(5)
            if self.exists("basic/home"): break
            while not self.exists(nextstage):
                if self.exists("basic/next"):
                    self.upload("drop_%s.png" % self.adb.get().SERIAL)
                    self.tap("basic/next"); self.sleep(5)
                if self.exists("basic/home"):
                    self.message(self.get("bot.attack_return"))
                    return True
            self.tap(nextstage); time.sleep(5)
        self.message(self.get("bot.attack_return"))
        return self.exists("basic/home")
