import os
import logging
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from nose.tools import with_setup, raises, ok_, eq_

from stve import log
from stve.exception import *

class TestLog(object):
    @classmethod
    def setup(cls):
        cls.LOG = log.Log("TEST.STVE")
        cls.original_logger = cls.LOG.logger
        cls.stream = StringIO()
        cls.log_handler = logging.StreamHandler(cls.stream)
        for handler in cls.original_logger.handlers:
            cls.original_logger.removeHandler(handler)
        cls.original_logger.addHandler(cls.log_handler)

    @classmethod
    def teardown(cls):
        cls.original_logger.removeHandler(cls.log_handler)
        cls.log_handler.close()

    @with_setup(setup, teardown)
    def test_log_success(self):
        self.LOG.debug("test sentence.")
        self.log_handler.flush()
        ok_("test sentence." in self.stream.getvalue())
