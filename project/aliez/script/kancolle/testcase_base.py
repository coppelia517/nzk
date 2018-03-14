import os
import sys
import pytest

from stve.log import Log

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

    def tap_check(self, location, _id=None, area=None, wait=True, timeout=5):
        if wait:
            if not self.wait(location, _id, area, threshold=10, _timeout=TIMEOUT_LOOP):
                L.warning("Can't Find Target : %s" % location)
        for _ in range(timeout):
            if self.tap(location, _id, area, False):
                self.sleep(2)
                if not self.exists(location, _id, area): return True
        return False
