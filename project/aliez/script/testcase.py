import os
import glob
import time
import random
import threading

from stve import PYTHON_VERSION
from stve.log import Log
from stve.exception import *

if PYTHON_VERSION == 3:
    from queue import Queue
else:
    from Queue import Queue

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
        self._wait_loop_flag = False
    
    def jenkins(self):
        return self.get("args.jenkins")

    def arg_parse(self, parser):
        super(TestCase_Base, self).arg_parse(parser)
        parser.add_argument("-s", "--serial", action='store', dest="serial", help="Android Serial.")
        parser.add_argument("-c", "--config", action='store', dest="config", help="Config File Name.")
        return parser

    @classmethod
    def get_service(cls):
        if cls.get("args.package") is not None:
            prof = os.path.join(SCRIPT_DIR, cls.get("args.package"), "profile")
            cls.adb = cls.service["stve.android"].get(cls.get("args.serial"), prof)
        else:
            cls.adb = cls.service["stve.android"].get(cls.get("args.serial"))
        cls.pic = cls.service["stve.picture"].get()

        stream = cls.service["aliez.stve.minicap"].get_stream(cls.get("minicap.ip"), cls.get("minicap.port"))
        proc = cls.service["aliez.stve.minicap"].get_process(LOG_DIR)
        cls.minicap = MinicapProc(stream, proc, debug=cls.get("args.debug"))

        if not cls.jenkins():
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

    def __get_path(self, target, func="cv"):
        try:
            if self.get("args.package") == None:
                return "%s://%s" % (func, target)
            else:
                return "%s://%s/%s" % (func, self.get("args.package"), target)
        except Exception as e:
            L.warning(e);
            raise ResourceError("Can't found Resource File. %s" % str(e))

    def validate(self, location, _id=None, area=None, _num=None, func="cv"):
        path, name, bounds = P.search(self.__get_path(location, func), _num)
        if _id is not None:
            name = name % str(_id)
        if path is None:
            raise ResourceError("Can't found Resource File. %s" % location)
        if self.adb.get().ROTATE == "0":
            w = int(self.adb.get().MINICAP_HEIGHT)
            h = int(self.adb.get().MINICAP_WIDTH)
        else:
            w = int(self.adb.get().MINICAP_WIDTH)
            h = int(self.adb.get().MINICAP_HEIGHT)
        if area == None:
            area = self.__area(w, h, bounds, func)
        L.info("Search : %s://%s" % (func, location))
        return path, name, area

    def __area(self, width, height, bounds, func="cv"):
        if func == "ocr":
            return self.__area_ocr(width, height, bounds)
        else:
            return self.__area_cv(width, height, bounds)

    def __area_cv(self, width, height, bounds):
        x = int((width * int(bounds["s_x"])) / 100.00)
        y = int((height * int(bounds["s_y"])) / 100.00)
        width = int((width * int(bounds["f_x"])) / 100.00) - x
        height = int((height * int(bounds["f_y"])) / 100.00) - y
        return POINT(x, y, width, height)

    def __area_ocr(self, width, height, bounds):
        x = int(bounds["s_x"])
        y = int(bounds["s_y"])
        width = int(bounds["f_x"]) - x
        height = int(bounds["f_y"]) - y
        return POINT(x, y, width, height)

    def text(self, location, text=None, area=None, timeout=TIMEOUT):
        if not self.jenkins():
            return True
        L.debug("OCR Test Check: Location %s, Text %s, Area %s, Timeout %s." % (location, text, area, timeout))
        path, name, area = self.validate(location, None, area, func="ocr")
        if text is not None:
            name = text
        result = self.minicap.search_ocr(area, _timeout=timeout)
        L.info("target : %s <-> %s : reference" % (result, name))
        return result == name

    def exists(self, location, _id=None, area=None, timeout=TIMEOUT):
        L.debug("Exists Check: Location %s, ID %s, Area %s, Timeout %s." % (location, _id, area, timeout))
        path, name, area = self.validate(location, _id, area, func="cv")
        for f in glob.glob(os.path.join(path, name)):
            L.debug("File : %s - %s" % (location, os.path.basename(f)))
            result = self.minicap.search_pattern(
                os.path.join(os.path.join(path, f)), area, timeout)
            if result != None: 
                L.debug("Exists : Location %s/%s, %s." % (location, os.path.basename(f), result))
                return True
        return False

    def match(self, location, _id=None, area=None, timeout=TIMEOUT, multiple=False):
        L.debug("Match Check: Location %s, ID %s, Area %s, Timeout %s." % (location, _id, area, timeout))
        path, name, area = self.validate(location, _id, area, func="cv")
        if multiple:
            res = []
            for f in glob.glob(os.path.join(path,name)):
                result = self.minicap.search_pattern(
                    os.path.join(os.path.join(path, f)), area, timeout)
                if result != None: res.append(result)
            return res
        else:
            for f in glob.glob(os.path.join(path,name)):
                result = self.minicap.search_pattern(
                    os.path.join(os.path.join(path, f)), area, timeout)
                if result != None: return result
            return None

    def __wait_loop(self, location, _id=None, area=None, timeout=TIMEOUT):
        while self._wait_loop_flag:
            if self.exists(location, _id, area, timeout):
                self.wait_queue.put(True); break
        #L.info("Wait Loop Stop.")

    def wait(self, location, _id=None, area=None, timeout=TIMEOUT, _wait=WAIT_TIMEOUT):
        L.debug("Wait Start : %s / Timeout : %s" % (location, timeout))
        try:
            self._wait_loop_flag = True
            start = time.time()
            self.wait_queue = Queue()
            self.loop = threading.Thread(
                target=self.__wait_loop, args=(location, _id, area, timeout, ))
            self.loop.start()
            result = self.wait_queue.get(timeout=_wait)
            if result is not None:
                return result
            else:
                self.minicap_screenshot('wait_failed.png')
                return False
        except Exception as e:
            L.warning("Wait Timeout : %s" % str(e))
        finally:
            self._wait_loop_flag = False
            self.loop.join()
            L.debug("Wait Loop End. Elapsed Time : %s" % str(time.time() - start))

    def tap(self, location, _id=None, area=None, threshold=TAP_THRESHOLD, timeout=TIMEOUT, wait=True, _wait=WAIT_TIMEOUT):
        L.debug("Tap : Location %s, ID %s, Area %s, Wait %s, Wait Timeout %s." % (location, _id, area, wait, timeout) )
        if wait:
            if not self.wait(location, _id, area, timeout, _wait):
                L.warning("Can't Find Target : %s" % location)
                return False
        result = self.match(location, _id, area)
        if result != None:
            self._tap(result, threshold)
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
