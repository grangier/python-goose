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
import unittest

from goose import Goose
from goose.utils import FileHelper
from goose.configuration import Configuration

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))


class TestArticleTags(unittest.TestCase):
    def get_html(self, filename):
        path = os.path.join(CURRENT_PATH, 'data', filename)
        return FileHelper.loadResourceFile(path)

    def getArticle(self, url, raw_html, language=None):
        config = Configuration()
        config.enable_image_fetching = False
        g = Goose(config=config)
        article = g.extract(url=url, raw_html=raw_html)
        return article

    def test_kexp(self):
        html = self.get_html('article_tags/kusp.txt')
        url = "http://blogs.kusp.org/filmgang/2013/02/08/stand-up-guys/"
        expected_tags = set([u'kusp film review', u'Stand Up Guys', u'film', u'Dennis Morton'])
        article = self.getArticle(url, html)
        self.assertEquals(article.tags, expected_tags)

    def test_deadline(self):
        html = self.get_html('article_tags/deadline.txt')
        url = "http://www.deadline.com/2013/06/deadline-big-media-with-david-lieberman-episode-38/"
        expected_tags = set([u'Deadline Big Media', u'TiVo', u'Amazon Prime', u'Steve Ballmer'])
        article = self.getArticle(url, html)
        self.assertEquals(article.tags, expected_tags)

    def test_wnyc(self):
        html = self.get_html('article_tags/wnyc.txt')
        url = "http://www.wnyc.org/shows/heresthething/2013/may/27/"
        expected_tags = set([u'Life', u'alec baldwin', u'other desert cities', u'News', u'Music', u'stacy keach'])
        article = self.getArticle(url, html)
        self.assertEquals(article.tags, expected_tags)

    def test_cnet(self):
        html = self.get_html('article_tags/cnet.txt')
        url = "http://www.cnet.com/8301-13952_1-57596170-81/the-404-1310-where-its-love-at-first-swipe-podcast/"
        expected_tags = set([u'purgatory', u'USDATE', u'Pope', u'online dating', u'leftovers', u'app', u'Yahoo', u'OKCupid', u'romance', u'Pontifex', u'Tinder', u'Leftover Swap', u'Match.com', u'Twitter', u'Marc Maron'])
        article = self.getArticle(url, html)
        self.assertEquals(article.tags, expected_tags)

    def test_abcau(self):
        """
        Test ABC Australia page with "topics" tags
        """
        html = self.get_html('article_tags/abcau.txt')
        url = "http://www.abc.net.au/news/2013-04-22/swimming-greats-say-cuts-a-shame/4644544"
        expected_tags = set([u'olympics-summer', u'australia', u'swimming'])
        article = self.getArticle(url, html)
        self.assertEquals(article.tags, expected_tags)
