__version__ = (0, 1, 0)

import os
import sys

LIB_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not LIB_PATH in sys.path:
    sys.path.insert(0, LIB_PATH)

from minicap import stream
from minicap.stream import MinicapStream

class Factory(object):
    def __init__(self):
        pass

    def version(self):
        return __version__

    def get(self, ip="127.0.0.1", port=1313):
        return MinicapStream.get_builder(ip, port)

NAME = "aliez.stve.minicap"
FACTORY = Factory()
