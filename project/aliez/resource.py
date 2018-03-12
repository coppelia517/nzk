import os
import sys
import json
from urllib.parse import urlparse

PATH = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if not PATH in sys.path:
    sys.path.insert(0, PATH)

from stve.log import Log
from aliez.utility import *
from aliez.exception import *

L = Log.get(__name__)


class Parser(object):

    @classmethod
    def search(cls, target, _id=None):
        if _id != None:
            target = "%s/id" % target
        info = urlparse(target)
        base_folder = os.path.join(TMP_REFERENCE_DIR, info.netloc)
        if not os.path.exists(base_folder):
            raise ResourceError("Can't find base directory : %s" % info.netloc)
        for f in os.listdir(base_folder):
            if f.find("%s.json" % info.scheme) != -1:
                with open(os.path.join(base_folder, f), 'r') as jf:
                    data = json.load(jf)
                    result = Parser.query(data, info.path)
                    if result == None:
                        ResourceError("Can't find target Infomation : %s" % info.path)
                    return Parser.path(base_folder, info.path, _id), result["name"], result["bounds"]
        L.warning("Can't Found Resource.")
        return None, None, None

    @classmethod
    def path(cls, base_folder, path, _id=None):
        for i in path.split('/'):
            base_folder = os.path.join(base_folder, i)
        if _id != None:
            for j in _id.split('/'):
                base_folder = os.path.join(base_folder, j)
        return base_folder

    @classmethod
    def query(cls, d, q):
        keys = q.split('/'); nd = d
        for k in keys:
            if k == '': continue
            if k in nd: nd = nd[k]
            else: return None
        return nd


if __name__ == "__main__":
    print(Parser.search("cv://kancolle/basic/login"))
