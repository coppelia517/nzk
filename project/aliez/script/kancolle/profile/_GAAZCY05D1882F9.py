import os
import sys

PATH = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if not PATH in sys.path:
    sys.path.insert(0, PATH)

import android_base

class _GAAZCY05D1882F9(android_base.Android):
    SERIAL = "GAAZCY05D1882F9"
    TMP_PICTURE = "%s_TMP.png" % SERIAL
    IP = ""
    PORT = ""

    NAME = "ASUS ZenFone"
    WIDTH = "1920"
    HEIGHT = "1080"
    MINICAP_WIDTH = "1280"
    MINICAP_HEIGHT = "720"
    LOCATE = "H"
    ROTATE = "90"

    EXERCISES_X = "1590"
    EXERCISES_Y = "390"
    EXERCISES_WIDTH = "180"
    EXERCISES_HEIGHT = "120"

    FORMATION_X = "320"
    FORMATION_Y = "375"
    FORMATION_WIDTH = "445"
    FORMATION_HEIGHT = "115"

    DOCKING_X = "800"
    DOCKING_Y = "228"
    DOCKING_WIDTH = "300"
    DOCKING_HEIGHT = "100"


if __name__ == "__main__":
    print(eval("_GAAZCY05D1882F9.%s" % "TMP_PICTURE"))
