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

from base import MockResponse
from extractors import TestExtractionBase
from goose.utils import FileHelper

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))


class MockResponseTags(MockResponse):
    def content(self):
        current_test = self.cls._get_current_testname()
        path = os.path.join(CURRENT_PATH, "data", "tags", "%s.html" % current_test)
        path = os.path.abspath(path)
        content = FileHelper.loadResourceFile(path)
        return content


class TestArticleTags(TestExtractionBase):

    callback = MockResponseTags

    def test_tags_kexp(self):
        article = self.getArticle()
        fields = ['tags']
        self.runArticleAssertions(article=article, fields=fields)

    def test_tags_deadline(self):
        article = self.getArticle()
        fields = ['tags']
        self.runArticleAssertions(article=article, fields=fields)

    def test_tags_wnyc(self):
        article = self.getArticle()
        fields = ['tags']
        self.runArticleAssertions(article=article, fields=fields)

    def test_tags_cnet(self):
        article = self.getArticle()
        fields = ['tags']
        self.runArticleAssertions(article=article, fields=fields)

    def test_tags_abcau(self):
        """
        Test ABC Australia page with "topics" tags
        """
        article = self.getArticle()
        fields = ['tags']
        self.runArticleAssertions(article=article, fields=fields)
