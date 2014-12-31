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


class ImageExtractionTests(TestExtractionBase):
    """\
    Base Mock test case
    """
    def assert_movies(self, field, expected_value, result_value):
        # check if result_value is a list
        self.assertTrue(isinstance(result_value, list))
        # check number of videos
        self.assertEqual(len(expected_value), len(result_value))

        # check values
        for c, video in enumerate(result_value):
            expected = expected_value[c]
            for k, v in expected.items():
                r = getattr(video, k)
                self.assertEqual(r, v)

    def test_embed(self):
        article = self.getArticle()
        fields = ['movies']
        self.runArticleAssertions(article=article, fields=fields)

    def test_iframe(self):
        article = self.getArticle()
        fields = ['movies']
        self.runArticleAssertions(article=article, fields=fields)

    def test_object(self):
        article = self.getArticle()
        fields = ['movies']
        self.runArticleAssertions(article=article, fields=fields)
