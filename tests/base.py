# -*- coding: utf-8 -*-
"""\
This is a python port of "Goose" orignialy licensed to Gravity.com
under one or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.

Python port was written by Xavier Grangier for Recrutae

Gravity.com licenses this file
to you under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import urllib2
import unittest

from StringIO import StringIO


class MockResponse():
    """\
    Base mock response class
    """
    code = 200
    msg = "OK"

    def content(self):
        return "response"

    def response(self, req):
        data = self.content()
        url = req.get_full_url()
        resp = urllib2.addinfourl(StringIO(data), data, url)
        resp.code = self.code
        resp.msg = self.msg
        return resp


class MockHTTPHandler(urllib2.HTTPHandler, urllib2.HTTPSHandler):
    """\
    Mocked HTTPHandler in order to query APIs locally
    """
    def __init__(self, debuglevel=0):
        urllib2.HTTPHandler.__init__(self, debuglevel)

    def https_open(self, req):
        return self.http_open(req)

    def http_open(self, req):
        r = self.cls.callback()
        return r.response(req)

    @staticmethod
    def patch(cls):     #def patch(func_name, callback):
        opener = urllib2.build_opener(MockHTTPHandler)
        urllib2.install_opener(opener)
        # dirty !
        for h in opener.handlers:
            if isinstance(h, MockHTTPHandler):
                h.cls = cls
        return [h for h in opener.handlers if isinstance(h, MockHTTPHandler)][0]

    @staticmethod
    def unpatch():
        urllib2._opener = None


class BaseMockTests(unittest.TestCase):
    """\
    Base Mock test case
    """
    callback = MockResponse

    def setUp(self):
        #MockHTTPHandler.patch(self._get_current_testname(), self.callback)
        MockHTTPHandler.patch(self)

    def tearDown(self):
        MockHTTPHandler.unpatch()

    def _get_current_testname(self):
        return self.id().split('.')[-1:][0]
