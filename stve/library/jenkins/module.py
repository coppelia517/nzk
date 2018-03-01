import os
import sys
import time
import requests

from stve.log import Log
from stve.exception import *

L = Log.get(__name__)

class Jenkins(object):
    def __init__(self, _url, _username, _password):
        self.url = _url
        self.username = _username
        self.password = _password

    def invoke_job(self, job, token, timeout=300):
        params = {
            'token': token,
            'delay': "%dsec" % timeout
        }
        url = "%s/job/%s/build" % (self.url, job)
        s = requests.Session(); s.auth = (self.username, self.password)
        L.info(str(s))
        result = s.get(url, params=params)
        L.debug("HTTP Status Code : %d" % result.status_code)
        status = result.status_code == 201
        return status

    def invoke_job_with_params(self, job, params):
        url = "%s/job/%s/buildWithParameters" % (self.url, job)
        s = requests.Session(); s.auth = (self.username, self.password)
        L.info(str(s))
        result = s.get(url, params=params)
        L.debug("HTTP Status Code : %d" % result.status_code)
        status = result.status_code == 201
        return status
