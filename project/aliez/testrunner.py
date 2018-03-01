import os
import sys
import importlib
import traceback
import pytest

import stve

PATH = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if not PATH in sys.path:
    sys.path.insert(0, PATH)

if stve.__version__ < "0.1.0":
    sys.exit("stve version over 0.1.0. : %s " % (stve.__version__))

from stve.log import Log
from stve.workspace import Workspace

from aliez.utility import *
from aliez.exception import *
from aliez.script.testcase_base import TestCase_Unit

L = Log.get(__name__)

class TestRunner(object):

    def __init__(self):
        self.workspace = Workspace(WORK_DIR)
        self.tmp = self.workspace.mkdir("tmp")
        self.log = self.workspace.mkdir("log")
        self.report = self.workspace.mkdir("report")

    def load(self, testcase, host):
        if testcase.find(".py") != -1: script = testcase
        else: script = testcase + ".py"
        path = os.path.join(host, script)

        if not os.path.exists(path):
            raise TestRunnerError("%s is not exists." % (path))
        name = script[:script.find(".")]
        L.debug("TestCase : %s" % path)
        try:
            if os.path.exists(path):
                return path
            else:
                return False
        except ImportError as e:
            L.warning(traceback.print_exc())
            L.warning(type(e).__name__ + ": " + str(e))
            return False

    def execute(self, script, package, host=SCRIPT_DIR):
        if not os.path.exists(host):
            raise TestRunnerError("%s is not exists." % (host))
        if not package == None: host = os.path.join(host, package)
        sys.path.append(host)

        module = self.load(script, host)
        L.debug("Module Name : " + str(module))
        report_filename = os.path.join(REPORT_DIR, "output.xml")
        if not module:
            L.warning("Not loaded module : %s" % script)
            raise TestRunnerError("%s is not extended unittest.TestCase." % script)
        else: pytest.main(['-q', '-s', '-vv', '--junitxml=%s' % report_filename, '%s' % module])
        sys.path.remove(host)

if __name__ == "__main__":
    if len(sys.argv[1:]) < 1:
        sys.exit("Usage: %s <filename>" % sys.argv[0])
    test = sys.argv[1]
    runner = TestRunner()
    result = os.path.normpath(test)
    testcase = os.path.basename(result)
    package = os.path.dirname(result)
    if package != None:
        TestCase_Unit.set("args.package", package)
        runner.execute(testcase, package)
    else:
        runner.execute(testcase, None)
