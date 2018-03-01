__version__ = (0, 1, 0)

import os
import sys

LIB_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not LIB_PATH in sys.path:
    sys.path.insert(0, LIB_PATH)

from jenkins import module
from jenkins.module import Jenkins

class Factory(object):
    def __init__(self):
        pass

    def version(self):
        return __version__

    def get(self, url, username, password):
        return Jenkins(url, username, password)

NAME = "stve.jenkins"
FACTORY = Factory()
