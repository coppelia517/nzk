import os
import sys

try:
    from PIL import Image
    from PIL import ImageOps
    import cv2
    import numpy as np
except Exception as e:
    print(str(e))

from stve.log import Log
from stve.exception import *

PMC_THRESHOLD = 0.96
L = Log.get(__name__)

class POINT(object):
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __repr__(self):
        return "POINT()"

    def __str__(self):
        return "(X, Y) = (%s, %s), Width = %s, Height = %s" \
            % (self.x, self.y, self.width, self.height)

class Picture(object):
    @classmethod
    def exists(cls, filename):
        if os.path.exists(filename): return True
        else:
            L.warning("%s is not exists." % filename)
            raise PictureError("%s is not exists." % filename)

    @classmethod
    def open(cls, filename):
        if cls.exists(filename):
            try:
                return Image.open(filename, 'r')
            except IOError as e:
                L.warning("I/O Error %s" % str(e))
                raise PictureError("it is not success of loading picture %s" % filename)

    @classmethod
    def save(cls, pic, filepath, q=100, opt=True):
        #cls.exists(filepath)
        if not os.path.exists(os.path.dirname(filepath)):
            raise PictureError("it is not exists parents directory. : %s" % os.path.dirname(filepath))
        pic.save(filepath, quality=q, optimize=opt)
        return filepath


    @classmethod
    def to_opencv(cls, pic):
        if pic == None:
            raise PictureError("it is not create opencv_pic.")
        return np.asarray(pic)

    @classmethod
    def to_pil(cls, opencv_pic):
        try:
            return Image.fromarray(opencv_pic)
        except Exception as e:
            L.warning(str(e))
            raise PictureError("it is not exchange pic.")

    @classmethod
    def resize(cls, pic, size):
        if size =="240P": sz = 240
        elif size == "360P": sz = 360
        elif size == "480P": sz = 480
        elif size == "720P": sz = 720
        elif size == "1080P": sz = 1080
        else: return
        #L.info("Base : %s" % str(pic.size))
        width = float((float(pic.size[0]) * sz)) / float(pic.size[1])
        res = (int(width), sz)
        #L.info("Resize : %s" % str(res))
        return pic.resize(res)


    @classmethod
    def _patternmatch(cls, reference, target, box=None):
        if not os.path.exists(reference):
            raise PictureError("it is not exists reference file. : %s" % reference)
        if not os.path.exists(target):
            raise PictureError("it is not exists target file. : %s" % target)
        reference_cv = cv2.imread(reference)
        target_cv = cv2.imread(target, 0)
        return cls.__patternmatch(reference_cv, target_cv, box)

    @classmethod
    def __patternmatch(cls, reference, target, box=None, tmp=None):
        img_gray = cv2.cvtColor(reference, cv2.COLOR_BGR2GRAY)
        if len(img_gray.shape) == 3: height, width, channels = img_gray.shape[:3]
        else: height, width = img_gray.shape[:2]
        if box == None:
            box = POINT(0, 0, width, height)
        cv2.rectangle(reference,
                      (box.x, box.y),
                      (box.x + box.width, box.y + box.height), (0, 255, 0), 5)
        img_gray = img_gray[box.y:(box.y + box.height), box.x:(box.x + box.width)]
        if tmp != None:
            cv2.imwrite(os.path.join(tmp, "crop.png"), img_gray)
        template = target
        w, h = template.shape[::-1]
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where( res >= PMC_THRESHOLD)
        result = None
        for pt in zip(*loc[::-1]):
            x = pt[0] + box.x
            y = pt[1] + box.y
            result = POINT(x, y, w, h)
            cv2.rectangle(reference, (x, y), (x + w, y + h), (0, 0, 255), 5)
        return result, reference

    @classmethod
    def search_pattern(cls, reference, target, box=None, tmp=None):
        if not os.path.exists(target):
            raise PictureError("it is not exists target file. : %s" % target)
        target_cv = cv2.imread(target, 0)
        return cls.__patternmatch(reference, target_cv, box, tmp)
