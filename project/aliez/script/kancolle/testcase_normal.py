import os
import sys
import time
import pytest

from stve.log import Log

from aliez.utility import *
from aliez.resource import Parser as P
from aliez.script.kancolle import testcase_base

L = Log.get(__name__)

def find_all_files(directory):
    for root, dirs, files in os.walk(directory):
        yield root
        for f in files:
            yield os.path.join(root, f)


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
            assert self.wait("basic/next")
            if self.exists("basic/expedition/success"):
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
        self.tap_check("home/attack"); self.sleep()
        assert self.exists("expedition")
        self.message(self.get("bot.expedition"))
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

    def supply_and_docking(self, fleet):
        #supply.
        if not self.exists("basic/home"): return False
        self.tap_check("home/supply"); self.sleep()
        if not self.exists(self.fleet_focus(fleet)):
            self.tap_check(self.fleet(fleet))
        self.message(self.get("bot.supply") % fleet)
        if self.exists("supply/vacant"):
            self.tap("supply"); self.sleep()
        # docking.
        self.tap_check("basic/menu/docking")
        self.wait("docking/select"); self.sleep()
        self.message(self.get("bot.docking"))
        for _ in range(3):
            position = self.match("docking/room")
            if position == None: break
            self.tap_check("docking/room")
            result = self.__docking()
            self._tap(position, threshold=0.49); self.sleep()
            if not result: break
        self.sleep()
        self.upload("docking_%s.png" % self.adb.get().SERIAL)
        return self.home()

    def __docking(self):
        if not self.exists("docking/next"):
            return False
        p = POINT(self.conversion_w(int(self.adb.get().DOCKING_X)),
                  self.conversion_h(int(self.adb.get().DOCKING_Y)),
                  self.conversion_w(int(self.adb.get().DOCKING_WIDTH)),
                  self.conversion_h(int(self.adb.get().DOCKING_HEIGHT)))
        for po in range(7):
            L.info(p);
            self._tap(p, threshold=0.49); self.sleep()
            if self.exists("docking/unable"):
                self._tap(p, threshold=0.49); self.sleep()
            elif self.exists("docking/start"):
                if not self.exists("docking/time"):
                    self.tap_check("docking/bucket")
                self.tap_check("docking/start")
                if self.tap_check("docking/yes"):
                    return True
            if self.adb.get().LOCATE == "V":
                p.x = int(p.x) - int(p.width)
                if int(p.x) < 0: return False
            else:
                p.y = int(p.y) + int(p.height)
                if int(p.y) > int(self.adb.get().HEIGHT): return False
        return False

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


    def __get_path(self, target):
        try:
            if self.get("args.package") == None:
                return os.path.join(TMP_REFERENCE_DIR, target)
            else:
                return os.path.join(
                    TMP_REFERENCE_DIR, self.get("args.package"), target)
        except Exception as e:
            L.warning(e); raise e

    def quest_search_id(self, _id):
        path = None
        for f in find_all_files(self.__get_path("quest")):
            if _id in str(f):
                if "daily" in f: path = "quest/daily"
                elif "weekly" in f: path = "quest/weekly"

                if "attack" in f: _id = "attack/%s" % _id
                elif "exercises" in f: _id = "exercises/%s" % _id
                elif "expedition" in f: _id = "expedition/%s" % _id
                elif "supply" in f: _id = "supply/%s" % _id

                L.debug("%s -> %s/id/%s" % (str(f), path, _id))
                return path, _id

    def quest_done(self):
        if not self.exists("quest/mission"): return False
        self.tap("quest/perform"); self.sleep(3)
        while self.exists("quest/done"):
            self.tap("quest/done")
            self.sleep()
            self.tap("quest/close"); time.sleep(4)
        return True

    def quest_check(self, target, crop_target, _id, threshold=0.2, count=5):
        box_result = self.match_quest(
            crop_target, _id, area=None, timeout=count)
        L.info(box_result)
        if box_result == None: return False
        result = self.match(
            target, _id=None, area=box_result, timeout=count, multiple=False)
        if result == None:
            self._tap(box_result, threshold); self.sleep()
        return True

    def quest_remove(self, target, crop_target, _id, threshold=0.2, count=5):
        box_result = self.match_quest(
            crop_target, _id, area=None, timeout=count)
        if box_result == None: return False
        result = self.match(
            target, _id=None, area=box_result, timeout=count, multiple=False)
        if result != None:
            self._tap(box_result, threshold); self.sleep()
        return True

    def quest_open(self):
        if not self.exists("basic/home"): return False
        self.tap("home/quest"); self.sleep(base=4)
        while not self.exists("quest"):
            self.tap("home/quest"); self.sleep(base=4)
        assert self.exists("quest")
        self.message(self.get("bot.quest"))
        self.tap_check("quest"); self.sleep()
        self.quest_done(); self.sleep()
        if not self.exists("quest/mission"):
            self.tap("quest/return"); self.sleep()
            assert self.wait("basic/home")
            return False
        return True

    def quest_search(self, _id, remove=False):
        q_path, _id = self.quest_search_id(_id)
        if "daily" in q_path:
            if not self.exists("quest/daily/focus"):
                while not self.exists("quest/daily/focus"):
                    self.tap("quest/daily"); self.sleep()
        elif "weekly" in q_path:
            if not self.exists("quest/weekly/focus"):
                while not self.exists("quest/weekly/focus"):
                    self.tap("quest/weekly"); self.sleep()
        if remove:
            if not self.quest_remove("quest/acceptance", q_path, _id):
                return False
        else:
            if not self.quest_check("quest/acceptance", q_path, _id):
                return False
        return True

    def quest_upload(self):
        if not self.exists("quest/mission"):
            self.tap("quest/return"); self.sleep()
            assert self.wait("basic/home")
            return False
        if not self.exists("quest/perform_select"):
            self.tap("quest/perform"); self.sleep(4)
        self.upload("quest_%s" % self.adb.get().TMP_PICTURE)
        self.tap_check("quest/return"); self.sleep()
        return self.wait("basic/home")

    def quest_attack(self, _id):
        assert self.quest_open()
        result = self.quest_search(_id); self.sleep(1)
        return result, self.quest_upload()
