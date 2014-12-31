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
import os
import json
import urllib2
import unittest
import socket

from StringIO import StringIO

from goose import Goose
from goose.utils import FileHelper
from goose.configuration import Configuration


CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))


# Response
class MockResponse():
    """\
    Base mock response class
    """
    code = 200
    msg = "OK"

    def __init__(self, cls):
        self.cls = cls

    def content(self):
        return "response"

    def response(self, req):
        data = self.content(req)
        url = req.get_full_url()
        resp = urllib2.addinfourl(StringIO(data), data, url)
        resp.code = self.code
        resp.msg = self.msg
        return resp


class MockHTTPHandler(urllib2.HTTPHandler, urllib2.HTTPSHandler):
    """\
    Mocked HTTPHandler in order to query APIs locally
    """
    cls = None

    def https_open(self, req):
        return self.http_open(req)

    def http_open(self, req):
        r = self.cls.callback(self.cls)
        return r.response(req)

    @staticmethod
    def patch(cls):
        opener = urllib2.build_opener(MockHTTPHandler)
        urllib2.install_opener(opener)
        # dirty !
        for h in opener.handlers:
            if isinstance(h, MockHTTPHandler):
                h.cls = cls
        return [h for h in opener.handlers if isinstance(h, MockHTTPHandler)][0]

    @staticmethod
    def unpatch():
        # urllib2
        urllib2._opener = None


class BaseMockTests(unittest.TestCase):
    """\
    Base Mock test case
    """
    callback = MockResponse

    def setUp(self):
        # patch DNS
        self.original_getaddrinfo = socket.getaddrinfo
        socket.getaddrinfo = self.new_getaddrinfo
        MockHTTPHandler.patch(self)

    def tearDown(self):
        MockHTTPHandler.unpatch()
        # DNS
        socket.getaddrinfo = self.original_getaddrinfo

    def new_getaddrinfo(self, *args):
        return [(2, 1, 6, '', ('127.0.0.1', 0))]

    def _get_current_testname(self):
        return self.id().split('.')[-1:][0]


class MockResponseExtractors(MockResponse):
    def content(self, req):
        test, suite, module, cls, func = self.cls.id().split('.')
        path = os.path.join(
                os.path.dirname(CURRENT_PATH),
                "data",
                suite,
                module,
                "%s.html" % func)
        path = os.path.abspath(path)
        content = FileHelper.loadResourceFile(path)
        return content


class TestExtractionBase(BaseMockTests):
    """\
    Extraction test case
    """
    callback = MockResponseExtractors

    def getRawHtml(self):
        test, suite, module, cls, func = self.id().split('.')
        path = os.path.join(
                os.path.dirname(CURRENT_PATH),
                "data",
                suite,
                module,
                "%s.html" % func)
        path = os.path.abspath(path)
        content = FileHelper.loadResourceFile(path)
        return content

    def loadData(self):
        """\

        """
        test, suite, module, cls, func = self.id().split('.')
        path = os.path.join(
                os.path.dirname(CURRENT_PATH),
                "data",
                suite,
                module,
                "%s.json" % func)
        path = os.path.abspath(path)
        content = FileHelper.loadResourceFile(path)
        self.data = json.loads(content)

    def assert_cleaned_text(self, field, expected_value, result_value):
        """\

        """
        # # TODO : handle verbose level in tests
        # print "\n=======================::. ARTICLE REPORT %s .::======================\n" % self.id()
        # print 'expected_value (%s) \n' % len(expected_value)
        # print expected_value
        # print "-------"
        # print 'result_value (%s) \n' % len(result_value)
        # print result_value

        # cleaned_text is Null
        msg = u"Resulting article text was NULL!"
        self.assertNotEqual(result_value, None, msg=msg)

        # cleaned_text length
        msg = u"Article text was not as long as expected beginning!"
        self.assertTrue(len(expected_value) <= len(result_value), msg=msg)

        # clean_text value
        result_value = result_value[0:len(expected_value)]
        msg = u"The beginning of the article text was not as expected!"
        self.assertEqual(expected_value, result_value, msg=msg)

    def runArticleAssertions(self, article, fields):
        """\

        """
        for field in fields:
            expected_value = self.data['expected'][field]
            result_value = getattr(article, field, None)

            # custom assertion for a given field
            assertion = 'assert_%s' % field
            if hasattr(self, assertion):
                getattr(self, assertion)(field, expected_value, result_value)
                continue

            # default assertion
            msg = u"Error %s \nexpected: %s\nresult: %s" % (field, expected_value, result_value)
            self.assertEqual(expected_value, result_value, msg=msg)

    def extract(self, instance):
        article = instance.extract(url=self.data['url'])
        return article

    def getConfig(self):
        config = Configuration()
        config.enable_image_fetching = False
        return config

    def getArticle(self):
        """\

        """
        # load test case data
        self.loadData()

        # basic configuration
        # no image fetching
        config = self.getConfig()
        self.parser = config.get_parser()

        # target language
        # needed for non english language most of the time
        target_language = self.data.get('target_language')
        if target_language:
            config.target_language = target_language
            config.use_meta_language = False

        # run goose
        g = Goose(config=config)
        return self.extract(g)
