import os
import sys
import importlib

from stve.define import SYLV_LIBRARY

from stve.exception import *
from stve.log import Log

L = Log.get(__name__)

def register(host=SYLV_LIBRARY):
    service = {}
    if not os.path.exists(host):
        raise LibraryError("%s is not exists." % (host))
    sys.path.append(host)
    for fdn in os.listdir(host):
        try:
            if fdn.endswith(".pyc") or fdn.endswith(".py"): pass
            elif fdn.endswith("__pycache__"): pass
            else:
                module = importlib.import_module("%s.service" % fdn)
                service[module.NAME] = module.FACTORY
        except Exception as e:
            L.warning(traceback.print_exc())
            L.warning(type(e).__name__ + ": " + str(e))
    return service
