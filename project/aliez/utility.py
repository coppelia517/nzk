import os
import sys
import logging

from stve.log import Log

WORK_DIR = os.path.normpath(os.path.dirname(__file__))
LIB_DIR = os.path.normpath(os.path.join(WORK_DIR, "library"))
LOG_DIR = os.path.normpath(os.path.join(WORK_DIR, "log"))
TMP_DIR = os.path.normpath(os.path.join(WORK_DIR, "tmp"))
SCRIPT_DIR = os.path.normpath(os.path.join(WORK_DIR, "script"))
REPORT_DIR = os.path.normpath(os.path.join(WORK_DIR, "report"))

def desc(string, L, cr=True):
    if cr: print()
    L.info(string)
