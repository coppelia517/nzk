import os
import sys
import time
import pytest

from stve.log import Log

from aliez.utility import *
from aliez.script import testcase
from aliez.resource import Parser as P

L = Log.get(__name__)


class TestCase_Normal(testcase.TestCase_Base):
    def __init__(self, *args, **kwargs):
        super(TestCase_Normal, self).__init__(*args, **kwargs)

    def arg_parse(self, parser):
        super(TestCase_Normal, self).arg_parse(parser)
        parser.add_argument("-i", "--slack", action='store', dest="slack", help="Slack Serial.")

        parser.add_argument("-e", "--expedition", action='store', dest="expedition", help="Expedition ID.")
        parser.add_argument("-f", "--fleet", action='store', dest="fleet", help="Fleet Number.")
        return parser

    def tap_check(self, location, _id=None, area=None, wait=True, timeout=5):
        if wait:
            if not self.wait(location, _id, area, threshold=10, _timeout=TIMEOUT_LOOP):
                L.warning("Can't Find Target : %s" % location)
        for _ in range(timeout):
            if self.tap(location, _id, area, False):
                self.sleep(2)
                if not self.exists(location, _id, area): return True
        return False

    def debug(self):
        return self.get("args.debug")

    def message(self, msg, channel=None):
        if self.debug(): pass
        else:
            if channel == None: channel = self.get("slack.channel")
            try:
                self.slack.message(msg, channel)
            except SlackError as e:
                L.warning(str(e))
                raise e

    def upload(self, filename=None, size="360P", channel=None):
        if self.debug(): pass
        else:
            self.__upload(self.__capture(filename, size))

    def capture(self, filename=None, size="360P"):
        return self.__capture(filename, size)

    def upload_file(self, fname, channel=None):
        self.__upload(fname, channel)

    def __capture(self, filename=None, size="360P"):
        if filename == None: filename = self.adb.get().TMP_PICTURE
        fname = self.minicap_screenshot(filename)
        if self.adb.get().LOCATE == "V": self._rotate(fname, "90")
        self._resize(fname, size)
        return fname

    def __upload(self, fname, channel=None):
        if self.debug(): pass
        else:
            if channel == None: channel = self.get("slack.channel")
            try:
                assert os.path.exists(fname)
                self.slack.upload(fname, channel, filetype="image/png")
            except SlackError as e:
                L.warning(str(e))
                raise e

    def _rotate(self, filepath, rotate, rename=""):
        try:
            pic = self.pic.open(filepath)
            rotate_pic = self.pic.rotate(pic, rotate)
            if rename == "": rename = filepath
            return self.pic.save(rotate_pic, rename)
        except Exception as e:
            L.warning(e)

    def _resize(self, filepath, resize, rename=""):
        try:
            pic = self.pic.open(filepath)
            resize_pic = self.pic.resize(pic, resize)
            if rename == "": rename = filepath
            return self.pic.save(resize_pic, rename)
        except Exception as e:
            L.warning(e)

    def invoke_job(self, job, token, timeout=300):
        L.info("Call %s : %s" % (job, self.jenkins.invoke_job(job, token, timeout)))

    def invoke_quest_job(self, _id, timeout=None):
        job = self.get("%s.jenkins" % _id)
        if timeout == None:
            timeout = int(self.get("%s.timeout" % _id))
        params = {
            'token': self.get("jenkins.token"),
            'android_id': self.get("args.serial"),
            'slack_id': self.get("args.slack"),
            'delay': "%dsec" % timeout
        }
        L.info("Call %s : %s" % (job, self.jenkins.invoke_job_with_params(job, params)))

    def call_job_tree(self, _id, timeout=60):
        if _id == "DB01":
            self.invoke_quest_job("DB02", timeout)
        elif _id == "DB02":
            self.invoke_quest_job("DB03", timeout); self.invoke_quest_job("DB04", timeout)
            self.invoke_quest_job("WB01", timeout); self.invoke_quest_job("WB02", timeout)
        elif _id == "DB04":
            self.invoke_quest_job("DB05", timeout); self.invoke_quest_job("WB03", timeout)
        elif _id == "DB05":
            self.invoke_quest_job("DB06", timeout)
        elif _id == "WB01":
            self.invoke_quest_job("WB04", timeout)
        elif _id == "WB03":
            self.invoke_quest_job("WB05", timeout)
        elif _id == "WB04":
            self.invoke_quest_job("WB06", timeout)
        else:
            L.info("Not Call.")

    def __validate_quest(self, location, _id, area=None):
        path, name, bounds = P.search(self.get_cv(location), _id)
        if path == None:
            raise ResourceError("Can't found Resource File. %s" % location)
        if self.adb.get().ROTATE == "0":
            w = int(self.adb.get().MINICAP_HEIGHT)
            h = int(self.adb.get().MINICAP_WIDTH)
        else:
            w = int(self.adb.get().MINICAP_WIDTH)
            h = int(self.adb.get().MINICAP_HEIGHT)
        if area == None: area = self.__area(w, h, bounds)
        L.info("Search : cv://%s" % (location))
        return path, name, area

    def match_quest(self, location, _id, area=None, threshold=5):
        path, name, area = self.__validate_quest(location, _id, area)
        for f in glob.glob(os.path.join(path,name)):
            result = self.minicap.search_pattern(os.path.join(os.path.join(path, f)), area, threshold)
            if result != None: return result
        return None

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
                assert self.search_ocr("formation/fleet_name", fleet_name)
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
        if int(id) > 32: self.tap("expedition/stage", _id="5")
        elif int(id) > 24: self.tap("expedition/stage", _id="4")
        elif int(id) > 16: self.tap("expedition/stage", _id="3")
        elif int(id) > 8: self.tap("expedition/stage", _id="2")
        else: self.tap("expedition/stage", _id="1")

    def expedition_id(self, id):
        self.tap("expedition/id", _id=id)
