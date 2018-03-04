import os
import sys
import logging

from stve.log import Log

WORK_DIR = os.path.normpath(os.path.dirname(__file__))
BIN_DIR = os.path.normpath(os.path.join(WORK_DIR, "binary"))
LIB_DIR = os.path.normpath(os.path.join(WORK_DIR, "library"))
LOG_DIR = os.path.normpath(os.path.join(WORK_DIR, "log"))
TMP_DIR = os.path.normpath(os.path.join(WORK_DIR, "tmp"))
SCRIPT_DIR = os.path.normpath(os.path.join(WORK_DIR, "script"))
REPORT_DIR = os.path.normpath(os.path.join(WORK_DIR, "report"))

TMP_REFERENCE_DIR = os.path.join(os.path.join(TMP_DIR, "reference"))
TMP_EVIDENCE_DIR = os.path.normpath(os.path.join(TMP_DIR, "evidence"))
TMP_VIDEO_DIR = os.path.normpath(os.path.join(TMP_DIR, "video"))

PROFILE_DIR = os.path.normpath(os.path.join(WORK_DIR, "conf", "profile"))
FFMPEG_BIN = os.path.normpath(os.path.join(BIN_DIR, "ffmpeg", "bin", "ffmpeg.exe"))

def desc(string, L, cr=True):
    if cr: print()
    L.info(string)
