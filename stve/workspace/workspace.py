mport os
import sys
import shutil
import tempfile
import datetime

from stve import STRING_SET
from stve.exception import *
from stve.log import Log

L = Log.get(__name__)

class Workspace(object):
    def __init__(self, path, clear=False):
        if not type(path) in STRING_SET:
            raise WorkspaceError("path must be strings.")
        self.default_path = os.path.abspath(path)
        if os.path.exists(path):
            if len(os.listdir(path)) > 0:
                L.warning("It is not vacant folder in the path.")
                if clear:
                    try:
                        for f in os.listdir(path):
                            shutil.rmtree(os.path.join(path, f))
                    except Exception as e:
                        L.traceback()
                        raise WorkspaceError("it must be vacant folder in the path.")
        else:
            self._mkdir_recursive(self.default_path)

    def _mkdir_recursive(self, path):
        sub_path = os.path.dirname(path)
        if not os.path.exists(sub_path):
            self._mkdir_recursive(sub_path)
        if not os.path.exists(path):
            os.mkdir(path)

    def root(self):
        return self.default_path

    def mkdir(self, folder, host="", clear=False):
        if not type(folder) in STRING_SET:
            raise WorkspaceError("folder must be strings.")
        if host == "":
            path = os.path.join(self.root(), folder)
        else:
            if not os.path.exists(host): self._mkdir_recursive(host)
            path = os.path.join(host, folder)

        if os.path.exists(path):
            if len(os.listdir(path)) > 0:
                L.warning("It is not vacant folder in the path.")
                if clear:
                    try:
                        for f in os.listdir(path):
                            shutil.rmtree(os.path.join(path, f))
                    except Exception as e:
                        L.traceback()
                        raise WorkspaceError("it must be vacant folder in the path.")
        else:
            self._mkdir_recursive(path)
        return path

    def rmdir(self, folder, host=""):
        if not type(folder) in STRING_SET:
            raise WorkspaceError("folder must be strings.")

        if host == "":
            path = os.path.join(self.root(), folder)
        else:
            if not os.path.exists(host):
                L.warning("it is not exists %s" % host)
                return host
            path = os.path.join(host, folder)

        if not os.path.exists(path):
            L.warning("it is not exists %s" % path)
            return path
        else:
            try:
                shutil.rmtree(path); return path
            except Exception as e:
                L.traceback()
                raise WorkspaceError("Can't remove file %s. Please Check File Permission." % path)

    def touch(self, filename, host=""):
        if not type(filename) in STRING_SET:
            raise WorkspaceError("filename must be strings.")

        if host == "":
            filepath = os.path.join(self.root(), filename)
        else:
            host = self.mkdir(host)
            filepath = os.path.join(host, filename)

        if os.path.exists(filepath):
            raise WorkspaceError("it is exists %s" % filepath)
        with open(filepath, 'a'):
            os.utime(filepath, None)
        return filepath

    def unique(self, host=""):
        d = datetime.datetime.today()
        dstr = d.strftime("%Y%m%d_%H%M%S")
        return self.touch(dstr, host=host)

    def rm(self, filepath):
        if not type(filepath) in STRING_SET:
            raise WorkspaceError("filepath must be strings.")
        if not os.path.exists(filepath):
            L.warning("it is not exists %s" % filepath)
        else:
            try:
                os.remove(filepath)
                return filepath
            except Exception as e:
                L.traceback()
                raise WorkspaceError("Can't remove file %s. Please Check File Permission." % filepath)
