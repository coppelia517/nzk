import os
import sys
import glob
import pytest

from stve.log import Log
from stve.exception import *

from aliez.utility import *
from aliez.script import testcase
from aliez.resource import Parser as P

L = Log.get(__name__)


class TestCase_Basic(testcase.TestCase_Base):
    def __init__(self, *args, **kwargs):
        super(TestCase_Basic, self).__init__(*args, **kwargs)

    def arg_parse(self, parser):
        super(TestCase_Basic, self).arg_parse(parser)
        parser.add_argument("-i", "--slack", action='store', dest="slack", help="Slack Serial.")
        parser.add_argument("-u", "--user", action='store', dest="user", help="Jenkins User Name.")
        parser.add_argument("-p", "--password", action='store', dest="password", help="Jenkins User Password.")
        parser.add_argument("-q", "--quest", action='store', dest="quest", help="Quest ID Number.")
        parser.add_argument("-t", "--timeout", action='store', dest="timeout", help="Timeout.")

        parser.add_argument("-e", "--expedition", action='store', dest="expedition", help="Expedition ID.")
        parser.add_argument("-f", "--fleet", action='store', dest="fleet", help="Fleet Number.")
        return parser

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
        else: self.__upload(self.__capture(filename, size))

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

    def tap_check(self, location, _id=None, area=None, threshold=TAP_THRESHOLD, timeout=TIMEOUT, wait=True, _wait=WAIT_TIMEOUT):
        L.info("Tap Check : %s " % (location) )
        for _ in range(timeout):
            if self.tap(location, _id, area, wait=wait):
                self.sleep()
                if not self.exists(location, _id, area, timeout=10): return True
        return False

    def match_quest(self, location, _num, area=None, timeout=TIMEOUT):
        L.info("Match Request : %s " % (location) )
        path, name, area = self.validate(location, None, area, _num)
        for f in glob.glob(os.path.join(path,name)):
            result = self.minicap.search_pattern(
                os.path.join(os.path.join(path, f)), area, timeout)
            if result != None: return result
        return None

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

    def __call_job_tree(self, _ids, timeout=60):
        for _id in _ids:
            self.invoke_quest_job(_id, timeout)

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
