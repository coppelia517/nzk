import os
import sys

from android_base import Android

class _0000000000000000(Android):
    SERIAL = "0000000000000000"
    TMP_PICTURE="%s_TMP.png" % SERIAL
    IP = ""
    PORT = ""

    WIDTH = "1280"
    HEIGHT = "720"
    MINICAP_WIDTH = "1280"
    MINICAP_HEIGHT = "720"
    LOCATE = "V"
    ROTATE = "0"

if __name__ == "__main__":
    print(eval("_0000000000000000.%s" % "TMP_PICTURE"))
