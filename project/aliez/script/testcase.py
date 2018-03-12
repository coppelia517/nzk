import os
import sys
import glob
import time
import random

from stve.log import Log
from stve.exception import *

from aliez.capture import MinicapProc
from aliez.utility import *
from aliez.script import testcase_base
from aliez.resource import Parser as P
from aliez.exception import *

L = Log.get(__name__)


class TestCase_Base(testcase_base.TestCase_Unit):
    def __init__(self, *args, **kwargs):
        super(TestCase_Base, self).__init__(*args, **kwargs)
        self.get_config(self.get("args.config"))
        self.get_service()

    def arg_parse(self, parser):
        super(TestCase_Base, self).arg_parse(parser)
        parser.add_argument("-s", "--serial", action='store', dest="serial", help="Android Serial.")
        parser.add_argument("-c", "--config", action='store', dest="config", help="Config File Name.")
        return parser

    @classmethod
    def get_service(cls):
        if cls.get("args.package") != None:
            prof = os.path.join(SCRIPT_DIR, cls.get("args.package"), "profile")
            cls.adb = cls.service["stve.android"].get(cls.get("args.serial"), prof)
        else:
            cls.adb = cls.service["stve.android"].get(cls.get("args.serial"))
        cls.pic = cls.service["stve.picture"].get()

        stream = cls.service["aliez.stve.minicap"].get_stream(cls.get("minicap.ip"), cls.get("minicap.port"))
        proc = cls.service["aliez.stve.minicap"].get_process(LOG_DIR)
        cls.minicap = MinicapProc(stream, proc, debug=cls.get("args.debug"))

        cls.ocr = cls.service["aliez.stve.ocr"].get(cls.pic)

    def minicap_start(self):
        L.info(" === Open Minicap Process. === ")
        self.minicap.start(self.adb, self.pic, self.ocr)

    def minicap_finish(self):
        L.info(" === Close Minicap Process. === ")
        self.minicap.finish()

    def minicap_screenshot(self, filename=None):
        if filename == None: filename = "capture.png"
        path = self.minicap.capture_image(filename)
        L.info("Get ScreenShot : %s" % path)
        return path

    def minicap_create_video(self):
        self.minicap.create_video(TMP_EVIDENCE_DIR, TMP_VIDEO_DIR)

    def minicap_search_pattern(self, reference, box=None, count=30):
        return self.minicap.search_pattern(reference, box, count)

    def minicap_search_ocr(self, box=None, count=30):
        return self.minicap.search_ocr(box, count)

    def sleep(self, base=3):
        sleep_time = (base - 0.5 * random.random())
        time.sleep(sleep_time)

    def debug(self):
        return self.get("args.debug")

    def __get_cv(self, target):
        try:
            if self.get("args.package") == None: return "cv://%s" % target
            else: return "cv://%s/%s" % (self.get("args.package"), target)
        except Exception as e:
            L.warning(e);
            raise ResourceError("Can't found Resource File. %s" % str(e))

    def __get_ocr(self, target):
        try:
            if self.get("args.package") == None: return "ocr://%s" % target
            else: return "ocr://%s/%s" % (self.get("args.package"), target)
        except Exception as e:
            L.warning(e);
            raise ResourceError("Can't found Resource File. %s" % str(e))

    def __validate(self, location, _id=None, area=None):
        path, name, bounds = P.search(self.__get_cv(location))
        if _id != None: name = name % str(_id)
        if path == None:
            raise ResourceError("Can't found Resource File. %s" % location)
        if self.adb.get().ROTATE == "0":
            w = int(self.adb.get().MINICAP_HEIGHT)
            h = int(self.adb.get().MINICAP_WIDTH)
        else:
            w = int(self.adb.get().MINICAP_WIDTH)
            h = int(self.adb.get().MINICAP_HEIGHT)
        if area == None: area = self.__area(w, h, bounds)
        L.info("Search Pattern : %s" % (location))
        return path, name, area

    def __area(self, width, height, bounds):
        x = int((width * int(bounds["s_x"])) / 100.00)
        y = int((height * int(bounds["s_y"])) / 100.00)
        width = int((width * int(bounds["f_x"])) / 100.00) - x
        height = int((height * int(bounds["f_y"])) / 100.00) - y
        return POINT(x, y, width, height)

    def exists(self, location, _id=None, area=None, threshold=5):
        path, name, area = self.__validate(location, _id, area)
        for f in glob.glob(os.path.join(path, name)):
            L.debug("File : %s" % (f))
            result = self.minicap.search_pattern(
                os.path.join(os.path.join(path, f)), area, threshold)
            if result != None: return True
        return False

    def match(self, location, _id=None, area=None, multiple=False, threshold=5):
        path, name, area = self.__validate(location, _id, area)
        if multiple:
            res = []
            for f in glob.glob(os.path.join(path,name)):
                result = self.minicap.search_pattern(os.path.join(os.path.join(path, f)), area, threshold)
                if result != None: res.append(result)
            return res
        else:
            for f in glob.glob(os.path.join(path,name)):
                result = self.minicap.search_pattern(os.path.join(os.path.join(path, f)), area, threshold)
                if result != None: return result
            return None

    def wait(self, location, _id=None, area=None, threshold=1, loop=TIMEOUT_LOOP):
        try:
            start = time.time()
            for _ in range(int(loop)):
                if self.exists(location, _id, area, threshold): return True
                self.sleep(base=3)
            self.minicap_screenshot('wait_failed.png')
            return False
        finally:
            L.debug("Elapsed Time : %s" % str(time.time() - start))

    def tap(self, location, _id=None, area=None, wait=True, threshold=TAP_THRESHOLD, loop=TIMEOUT_LOOP):
        if wait:
            if not self.wait(location, _id, area, threshold=10, loop=loop):
                L.warning("Can't Find Target : %s" % location)
        result = self.match(location, _id, area)
        if result != None:
            self._tap(result, TAP_THRESHOLD); self.sleep(1)
            return True
        else: return False

    def _tap(self, result, random=True, threshold=0.3):
        if random:
            x = self.normalize_w(result.x) + self.randomize(result.width, threshold)
            y = self.normalize_h(result.y) + self.randomize(result.height, threshold)
        else:
            x = self.normalize_w(result.x)
            y = self.normalize_h(result.y)
        self.adb.tap(x, y)

    def normalize(self, base, real, virtual):
        return int(base * real / virtual)

    def normalize_w(self, base):
        return self.normalize(base, int(self.adb.get().WIDTH), int(self.adb.get().MINICAP_WIDTH))

    def conversion_w(self, base):
        return self.normalize(base, int(self.adb.get().MINICAP_WIDTH), int(self.adb.get().WIDTH))

    def normalize_h(self, base):
        return self.normalize(base, int(self.adb.get().HEIGHT), int(self.adb.get().MINICAP_HEIGHT))

    def conversion_h(self, base):
        return self.normalize(base, int(self.adb.get().MINICAP_HEIGHT), int(self.adb.get().HEIGHT))

    def randomize(self, base, threshold):
        return random.randint(int(int(base) * threshold) , int(int(base) * (1.0 - threshold)))
