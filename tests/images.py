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

from goose import Goose
from goose.configuration import Configuration
from goose.utils import FileHelper
from base import BaseMockTests, MockResponse

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))

FILE_PATH = {
    'test_1': 'extractors/businessweek2.txt',
    'test_2': 'extractors/cnn1.txt'
}


class MockResponseImage(MockResponse):
    def content(self):
        filename = FILE_PATH[self.cls._get_current_testname()]
        path = os.path.join(CURRENT_PATH, 'data', filename)
        path = os.path.abspath(path)
        return FileHelper.loadResourceFile(path)


class ImageTests(BaseMockTests):
    """\
    Base Mock test case
    """
    callback = MockResponseImage

    def getArticle(self, url, language=None):
        config = Configuration()
        if language:
            config.target_language = language
            config.use_meta_language = False
        config.enable_image_fetching = False
        g = Goose(config=config)
        article = g.extract(url=url)
        return article

    def test_1(self):
        url = "http://www.businessweek.com/management/five-social-media-lessons-for-business-09202011.html"
        article = self.getArticle(url)

    def test_2(self):
        url = "http://www.cnn.com/2010/POLITICS/08/13/democrats.social.security/index.html"
        article = self.getArticle(url)
