import sys

__version__ = "0.1.0.ALPHA"

try:
    PYTHON_VERSION = sys.version_info.major
except:
    PYTHON_VERSION = sys.version_info[0]

if PYTHON_VERSION == 3: STRING_SET = [bytes, str]
else: STRING_SET = [str, unicode]
