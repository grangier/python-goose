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

from base import TestExtractionBase


class TestArticleTags(TestExtractionBase):

    def assert_tags(self, field, expected_value, result_value):
        """\

        """
        # as we have a set in expected_value and a list in result_value
        # make result_value a set
        expected_value = set(expected_value)

        # check if both have the same number of items
        msg = (u"expected tags set and result tags set"
                u"don't have the same number of items")
        self.assertEqual(len(result_value), len(expected_value), msg=msg)

        # check if each tag in result_value is in expected_value
        for tag in result_value:
            self.assertTrue(tag in expected_value)

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
