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
import unittest
import socket
import requests_mock

try:
    import urllib2
except ImportError:
    import urllib.request as urllib2

import six
from six import StringIO, BytesIO

from goose import Goose
from goose.utils import FileHelper
from goose.configuration import Configuration


CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))


# Response
class MockResponse:
    """\
    Base mock response class
    """
    code = 200
    msg = "OK"

    def __init__(self, cls):
        self.cls = cls

    def contents(self):
        pass


class BaseMockTests(unittest.TestCase):
    """\
    Base Mock test case
    """
    callback = MockResponse

    def setUp(self):
        # patch DNS
        self.original_getaddrinfo = socket.getaddrinfo
        socket.getaddrinfo = self.new_getaddrinfo

    def tearDown(self):
        # DNS
        socket.getaddrinfo = self.original_getaddrinfo

    def new_getaddrinfo(self, *args):
        return [(2, 1, 6, '', ('127.0.0.1', 0))]

    def _get_current_testname(self):
        return self.id().split('.')[-1:][0]


class MockResponseExtractors(MockResponse):
    def contents(self):
        test, suite, module, cls, func = self.cls.id().split('.')
        path = os.path.join(
                os.path.dirname(CURRENT_PATH),
                "data",
                suite,
                module,
                "%s.html" % func)
        path = os.path.abspath(path)
        content = FileHelper.loadResourceFile(path)
        yield self.cls.data['url'], content.encode('utf-8')


class TestExtractionBase(BaseMockTests):
    """\
    Extraction test case
    """
    callback = MockResponseExtractors

    def setUp(self):
        # patch DNS
        self.original_getaddrinfo = socket.getaddrinfo
        socket.getaddrinfo = self.new_getaddrinfo

    def tearDown(self):
        socket.getaddrinfo = self.original_getaddrinfo

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
        article_url = self.data['url']
        with requests_mock.mock() as m:
            for url, content in self.callback(self).contents():
                m.get(url, content=content)
            article = instance.extract(url=article_url)
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
