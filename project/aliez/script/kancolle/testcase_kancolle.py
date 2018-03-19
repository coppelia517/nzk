import os
import sys
import time
import pytest

from stve.log import Log
from aliez.utility import *
from aliez.script.kancolle import testcase_normal

L = Log.get(__name__)

def find_all_files(directory):
    for root, dirs, files in os.walk(directory):
        yield root
        for f in files:
            yield os.path.join(root, f)


class TestCase(testcase_normal.TestCase_Normal):

    def supply_all(self):
        if not self.exists("basic/home"): return False
        self.tap_check("home/supply"); self.sleep()
        for fleet in range(2, 5):
            if not self.exists(self.fleet_focus(fleet)):
                self.tap_check(self.fleet(fleet))
            if self.exists("supply/vacant"):
                self.tap("supply"); self.sleep(2)
        return self.home()

    def expedition_all(self):
        if not self.exists("basic/home"): return False
        self.tap_check("home/attack"); self.sleep()
        assert self.exists("expedition")
        self.message(self.get("bot.expedition"))
        self.tap("expedition"); self.sleep(4)
        flag = True
        for fleet in range(2, 5):
            fleet = str(fleet); id = self.get("expedition.fleet_%s" % fleet)
            self.expedition_stage(id)
            self.expedition_id(id); self.sleep()
            if not self.exists("expedition/done"):
                self.tap_check("expedition/decide"); self.sleep(4)
                if not self.exists("expedition/fleet_focus", _id=fleet):
                    self.tap("expedition/fleet", _id=fleet); self.sleep()
                if not self.exists("expedition/unable"):
                    if not self.exists("expedition/rack"):
                        self.tap("expedition/start"); self.sleep(5)
                        if self.exists("expedition/done"):
                            self.message(self.get("bot.expedition_start") % fleet)
                            self.sleep(3)
                            assert self.wait("expedition/icon")
                            self.upload("expedition_%s.png" % self.adb.get().SERIAL)
                    else:
                        self.message(self.get("bot.expedition_unable") % fleet)
                else:
                    self.message(self.get("bot.expedition_unable") % fleet)
            else:
                self.message(self.get("bot.expedition_done") % fleet)
        return self.home()

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

    def quest_expedition(self):
        assert self.quest_open()
        self.quest_search("DP01"); self.sleep(1)
        self.quest_search("DP02"); self.sleep(1)
        self.quest_search("WP01"); self.sleep(1)
        self.quest_search("WP02"); self.sleep(1)
        self.quest_search("WP03"); self.sleep(1)
        return self.quest_upload()

    def quest_supply(self):
        assert self.quest_open()
        self.quest_search("DS01"); self.sleep(1)
        self.quest_search("DS02"); self.sleep(1)
        return self.quest_upload()

    def quest_exercises(self):
        assert self.quest_open()
        self.quest_search("DX01"); self.sleep(1)
        self.quest_search("DX02"); self.sleep(1)
        self.quest_search("WX01"); self.sleep(1)
        return self.quest_upload()

    def quest_exercises_remove(self):
        assert self.quest_open()
        self.quest_search("DX01", remove=True); self.sleep(1)
        self.quest_search("DX02", remove=True); self.sleep(1)
        self.quest_search("WX01", remove=True); self.sleep(1)
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
        return True
