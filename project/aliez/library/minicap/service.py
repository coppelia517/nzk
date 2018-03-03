__version__ = (0, 1, 0)

import os
import sys

LIB_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not LIB_PATH in sys.path:
    sys.path.insert(0, LIB_PATH)

from minicap.stream import MinicapStream
from minicap.proc import MinicapService

class Factory(object):
    def __init__(self):
        pass

    def version(self):
        return __version__

    def get_stream(self, ip="127.0.0.1", port=1313):
        return MinicapStream.get_builder(ip, port)

    def get_process(self, log):
        return MinicapService("minicap", log)

NAME = "aliez.stve.minicap"
FACTORY = Factory()
