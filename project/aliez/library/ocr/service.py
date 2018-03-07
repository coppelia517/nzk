__version__ = (0, 1, 0)
import os
import sys

LIB_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not LIB_PATH in sys.path:
    sys.path.insert(0, LIB_PATH)

from ocr import module
from ocr.module import Ocr

class Factory(object):
    def __init__(self):
        pass

    def version(self):
        return __version__

    def get(self):
        return Ocr()


NAME = "aliez.stve.ocr"
FACTORY = Factory()
