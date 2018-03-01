import sys
import traceback

from stve import STRING_SET
from stve.exception import *

class ResourceError(StveError):
    def __init__(self, details):
        if type(details) in STRING_SET:
            details = {
                'message' : details
            }
        StveError.__init__(self, details)

class TestRunnerError(StveError):
        def __init__(self, details):
            if type(details) in STRING_SET:
                details = {
                    'message' : details
                }
            StveError.__init__(self, details)
