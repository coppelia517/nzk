import os
import sys

try:
    import pyocr
except Exception as e:
    print(str(e))

from stve.log import Log

L = Log.get(__name__)
