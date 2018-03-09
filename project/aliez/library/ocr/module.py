import os
import sys

try:
    import pyocr
    import pyocr.builders
except Exception as e:
    print(str(e))

from stve.log import Log

from aliez.exception import *

L = Log.get(__name__)


class Ocr(object):
    def __init__(self, _pic):
        self.pic = _pic
        tools = pyocr.get_available_tools()
        if len(tools) == 0:
            raise OcrError("No OCR tool found.")
        self.tool = tools[0]
        L.info("Will use tool '%s'" % (self.tool.get_name()))
        langs = self.tool.get_available_languages()
        L.info("Available languages: %s" % ", ".join(langs))
        lang = langs[0]
        L.info("Will use lang '%s'" % lang)

    def img_to_string(self, filename, _lang="eng"):
        txt = self.tool.image_to_string(
            self.pic.open(filename),
            lang=_lang,
            builder = pyocr.builders.TextBuilder(tesseract_layout=6)
        )
        L.info("%s -> %s" % (filename, txt))
        return txt
