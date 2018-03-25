import os
import sys

try:
    import cv2
    import numpy as np
    import pyocr
    import pyocr.builders
except Exception as e:
    print(str(e))

from stve.log import Log
from stve.exception import *

from aliez.utility import *
from aliez.exception import *

L = Log.get(__name__)


class Ocr(object):
    def __init__(self, _pic):
        self.pic = _pic
        tools = pyocr.get_available_tools()
        L.info(tools)
        if len(tools) == 0:
            raise OcrError("No OCR tool found.")
        self.tool = tools[0]
        L.info("Will use tool '%s'" % (self.tool.get_name()))
        langs = self.tool.get_available_languages()
        L.info("Available languages: %s" % ", ".join(langs))
        lang = langs[0]
        L.info("Will use lang '%s'" % lang)

    def __img_to_string(self, reference, box=None, tmp=None, _lang="eng"):
        if len(reference.shape) == 3: height, width, channels = reference.shape[:3]
        else: height, width = reference.shape[:2]

        if box == None:
            box = POINT(0, 0, width, height)
        cv2.rectangle(reference,
                      (box.x, box.y),
                      (box.x + box.width, box.y + box.height), (255, 0, 0), 5)

        img_gray = cv2.cvtColor(reference, cv2.COLOR_BGR2GRAY)
        img_gray = img_gray[box.y:(box.y + box.height), box.x:(box.x + box.width)]
        if tmp != None:
            cv2.imwrite(os.path.join(tmp, "crop_ocr.png"), img_gray)
        txt = self.tool.image_to_string(
            self.pic.to_pil(img_gray),
            lang=_lang,
            builder = pyocr.builders.TextBuilder(tesseract_layout=6)
        )
        return txt, reference

    def img_to_string(self, reference, box=None, tmp=None, _lang="eng"):
        txt, ref = self.__img_to_string(reference, box, tmp, _lang)
        L.debug("Get Text -> %s" % (txt))
        return txt, reference

    def file_to_string(self, filename, box=None, tmp=None, _lang="eng"):
        if not os.path.exists(filename):
            raise PictureError("it is not exists reference file. : %s" % filename)
        ref_cv = cv2.imread(filename)
        txt, ref = self.__img_to_string(ref_cv, box, tmp, _lang)
        L.info("%s -> %s" % (filename, txt))
        return txt
