import os
import sys

PATH = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if not PATH in sys.path:
    sys.path.insert(0, PATH)

import android_base

class _BH9037HP5U(android_base.Android):
    SERIAL = "BH9037HP5U"
    TMP_PICTURE="%s_TMP.png" % SERIAL
    IP = ""
    PORT = ""

    NAME = "Xperia X Compact"
    WIDTH = "1280"
    HEIGHT = "720"
    MINICAP_WIDTH = "1280"
    MINICAP_HEIGHT = "720"
    LOCATE = "H"
    ROTATE = "90"

    EXERCISES_X = "1060"
    EXERCISES_Y = "260"
    EXERCISES_WIDTH = "120"
    EXERCISES_HEIGHT = "80"

    DOCKING_X = "530"
    DOCKING_Y = "154"
    DOCKING_WIDTH = "330"
    DOCKING_HEIGHT = "66"

    LEVELING_X = "550"
    LEVELING_Y = "560"
    LEVELING_WIDTH = "260"
    LEVELING_HEIGHT = "70"

    FORMATION_X = "210"
    FORMATION_Y = "250"
    FORMATION_WIDTH = "305"
    FORMATION_HEIGHT = "75"

if __name__ == "__main__":
    print(eval("_BH9037HP5U.%s" % "TMP_PICTURE"))
