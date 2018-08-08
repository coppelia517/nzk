import os
import re
import sys
import time
import glob
import importlib

PROFILE_PATH = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "profile"))
if not PROFILE_PATH in sys.path:
    sys.path.insert(0, PROFILE_PATH)

from stve.log import Log
from stve.cmd import run, run_bg
from stve.exception import *

TIMEOUT = 30
ADB_ROOT = os.path.normpath(os.path.dirname(__file__))
L = Log.get(__name__)

class AndroidBase(object):
    def __init__(self, profile, host=PROFILE_PATH):
        self.WIFI = False
        self._set_profile(profile, host)

    def _set_profile(self, name, host):
        self.profile = None
        class_name = "_" + name
        if not os.path.exists(host):
            L.warning("%s is not exists." % host)
            raise AndroidError("%s is not exists." % host)
        try:
            prof = None
            for fdn in os.listdir(host):
                if fdn.endswith(".py") and (name in fdn):
                    prof = fdn.replace(".py", "")
            if prof == None:
                L.warning("Not have a profile : %s " % name)
                class_name = "_0000000000000000"
                for fdn in os.listdir(PROFILE_PATH):
                    if fdn.endswith("_0000000000000000.py"):
                        prof = fdn.replace(".py", "")
            sys.path.append(host)
            module = importlib.import_module(str(prof))
            self.profile = getattr(module, class_name)
            self.profile.SERIAL = name
            self.profile.TMP_PICTURE = "%s_TMP.png" % name
            sys.path.remove(host)
        except Exception as e:
            sys.path.remove(host)
            L.debug('=== Error Exception ===')
            L.debug('type     : ' + str(type(e)))
            L.debug('args     : ' + str(e.args))
            L.debug('e        : ' + str(e))
            raise AndroidError(str(e))

    def get_profile(self):
        return self.profile

    def __exec(self, cmd, timeout=TIMEOUT, debug=False):
        L.debug(cmd)
        result = run(cmd, timeout=timeout, debug=debug)
        if result != None:
            try:
                if result[0] == 0:
                    result = result[1].replace("\r", "")
                else:
                    L.warning(result[2].replace("\r", ""))
                    raise AndroidError(
                        "Android Execute Failed. : %s" % result[2].replace("\r", ""))
            except Exception as e:
                L.warning(str(e))
                raise e
        return result

    def __exec_bg(self, cmd, timeout=TIMEOUT, debug=False):
        L.debug(cmd)
        run_bg(cmd, debug=debug)

    def _target(self):
        if not self.WIFI:
            return "-s %s" % (self.profile.SERIAL)
        else:
            return "-s %s:%s" % (self.profile.IP, self.profile.PORT)

    def _adb(self, cmd, _async=False, debug=False, timeout=TIMEOUT):
        if "adb" in cmd:
            L.debug("command include [adb]. : %s" % cmd)
        cmd = "adb %s" % cmd
        if _async: self.__exec_bg(cmd, timeout, debug)
        else: return self.__exec(cmd, timeout, debug)

    def kill(self):
        cmd = "kill-server"
        return self._adb(cmd)

    def adb(self, cmd, _async=False, debug=False, timeout=TIMEOUT):
        if "adb" in cmd:
            L.debug("command include [adb]. : %s" % cmd)
        cmd = "%s %s" % (self._target(), cmd)
        return self._adb(cmd, _async, debug, timeout)

    def push(self, src, dst, timeout=TIMEOUT):
        L.debug("[push] : %s -> %s" % (src, dst))
        cmd = "push %s %s" % (src, dst)
        return self.adb(cmd, timeout)

    def pull(self, src, dst, timeout=TIMEOUT):
        L.debug("[pull]. : %s -> %s" % (src, dst))
        cmd = "pull %s %s" % (src, dst)
        return self.adb(cmd, timeout)

    def shell(self, cmd, _async=False, debug=False, timeout=TIMEOUT):
        if "shell" in cmd:
            L.debug("command include [shell]. : %s" % cmd)
        cmd = "shell %s" % (cmd)
        return self.adb(cmd, _async, debug, timeout)

    def connect(self):
        if self.WIFI:
            cmd = "connect %s:%s" % (self.profile.IP, self.profile.PORT)
            return self._adb(cmd)

    def disconnect(self):
        if self.WIFI:
            cmd = "disconnect %s:%s" % (self.profile.IP, self.profile.PORT)
            return self._adb(cmd)

    def usb(self):
        if self.WIFI:
            self.disconnect()
            self.WIFI = False
        return self.adb("usb")

    def tcpip(self):
        if not self.WIFI:
            self.disconnect()
            self.WIFI = True
        cmd = "tcpip %s" % (self.profile.PORT)
        return self._adb(cmd)

    def root(self):
        L.debug(str(self.adb("root")))
        self.kill()
        if self.WIFI: self.tcpip()
        else: self.usb()
        self.connect()

    def remount(self):
        L.debug(self.adb("remount"))

    def restart(self):
        L.debug(self.adb("reboot"))

    def install(self, application, timeout=TIMEOUT):
        cmd = "install -r %s" % (application)
        L.debug(self.adb(cmd, timeout=timeout))

    def uninstall(self, application, timeout=TIMEOUT):
        cmd = "uninstall %s" % (application)
        L.debug(self.adb(cmd, timeout=timeout))

    def wait(self, timeout=TIMEOUT):
        return self.adb("wait-for-device", timeout=timeout)


class Android(object):
    def __init__(self, profile, host=PROFILE_PATH):
        self._adb = AndroidBase(profile, host)

    def get(self):
        return self._adb.get_profile()

    def shell(self, cmd, _async=False, debug=False, timeout=TIMEOUT):
        return self._adb.shell(cmd, _async, debug, timeout)

    def dumpsys(self, category):
        cmd = "dumpsys %s" % category
        return self.shell(cmd)

    def snapshot(self, filename, host):
        self._adb.shell('screencap -p /sdcard/%s' % (filename))
        self._adb.pull('/sdcard/%s' % (filename), host)
        self._adb.shell('rm /sdcard/%s' % (filename))
        return os.path.join(host, filename)

    def start(self, intent):
        return self._adb.shell("am start -n %s" % (intent))

    def push(self, src, dst):
        return self._adb.push(src, dst)

    def pull(self, src, dst):
        return self._adb.pull(src, dst)

    def install(self, application):
        return self._adb.install(application)

    def uninstall(self, application):
        return self._adb.uninstall(application)

    def forward(self, cmd):
        if "forward" in cmd:
            L.debug("command include [forward]. : %s" % cmd)
        cmd = "forward %s" % cmd
        return self._adb.adb(cmd)

    def input(self, cmd, _async=False, debug=False):
        if "input" in cmd:
            L.debug("command include [input]. : %s" % cmd)
        cmd = "input %s" % cmd
        return self._adb.shell(cmd, _async, debug)

    def am(self, cmd):
        if "am" in cmd:
            L.debug("command include [am]. : %s" % cmd)
        cmd = "am %s" % cmd
        return self._adb.shell(cmd)

    def tap(self, x, y):
        cmd = "tap %d %d" % (x, y)
        return self.input(cmd, _async=True)

    def invoke(self, app):
        cmd = "start -n %s" % (app)
        return self.am(cmd)

    def keyevent(self, code):
        cmd = "keyevent %s " % (code)
        return self.input(cmd, _async=True)

    def text(self, cmd):
        args = cmd.split(" ")
        for arg in args:
            self._text(arg)
            self.keyevent(self.get().KEYCODE_SPACE)

    def _text(self, cmd):
        if "text" in cmd:
            L.debug("command include [text]. : %s" % cmd)
        cmd = "text %s" % cmd
        return self.input(cmd)

    def stop(self, app):
        package = app.split("/")[0]
        cmd = "force-stop %s " % (package)
        return self.am(cmd)

    def getprop(self, prop):
        if "getprop" in prop:
            L.debug("command include [getprop]. : %s" % prop)
        cmd = "getprop %s" % prop
        return self._adb.shell(cmd)

    def setprop(self, prop, value):
        if "setprop" in prop:
            L.debug("command include [setprop]. : %s" % prop)
        cmd = "setprop %s %s" % (prop, value)
        return self._adb.shell(cmd)

    def power(self):
        self.keyevent(self.get().KEYCODE_POWER)

    def boot_completed(self):
        return self.getprop(self.get().PROP_BOOT_COMPLETED)

    def reboot(self):
        self._adb.restart()
        time.sleep(20)
        while self.boot_completed() != "1":
            time.sleep(5)

    def rotate(self):
        result = self.dumpsys('input')
        if type(result) == "unicode":
            result = result.encode()
        result = result.split("\n")
        for line in result:
            if line.find('SurfaceOrientation') >= 0:
                return int(line.split(":")[1])

if __name__ == '__main__':
    a = Android("BH9037HP5U")
    print(a.get().SERIAL)
    #print(a.rotate())
    #a.tap(527, 804)
    #a.invoke("com.dmm.dmmlabo.kancolle/.AppEntry")
    try:
        a.snapshot("screen.png", os.path.dirname(os.path.abspath(__file__)))
    except Exception as e:
        print(str(e))
    #a.stop("com.dmm.dmmlabo.kancolle/.AppEntry")
    #print a.exec_application(a.get().AURA_DEBUGON, {})
