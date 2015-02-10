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
import sys
# the default recursion limit is 1000
sys.setrecursionlimit(2000)
import os
import platform
from tempfile import mkstemp
import traceback

from goose.version import version_info, __version__
from goose.configuration import Configuration
from goose.crawler import CrawlCandidate
from goose.crawler import Crawler

class Goose(object):
    """\

    """
    def __init__(self, config=None):
        self.config = config or Configuration()
        self.extend_config()
        self.initialize()

    def extend_config(self):
        if isinstance(self.config, dict):
            config = Configuration()
            for k, v in self.config.items():
                if hasattr(config, k):
                    setattr(config, k, v)
            self.config = config

    def extract(self, url=None, raw_html=None):
        """
        Main method to extract an article object from a URL,
        pass in a url and get back a Article
        """
        cc = CrawlCandidate(self.config, url, raw_html)
        return self.crawl(cc)

    def shutdown_network(self):
        pass

    def crawl(self, crawl_candiate):
        parsers = list(self.config.available_parsers)
        parsers.remove(self.config.parser_class)
        article = None
        try:
            crawler = Crawler(self.config)
            article = crawler.crawl(crawl_candiate)
        except (UnicodeDecodeError, ValueError):
            self.config.parser_class = parsers[0]
            try:
                if isinstance(crawl_candiate, basestring):
                    return self.crawl(crawl_candiate)
            except exception as e:
                print >> sys.stderr, 'Article Crawl error: ', traceback.format_exec()
        return article

    def initialize(self):
        # we don't need to go further if image extractor or
        # local_storage is not set
        if not self.config.local_storage_path or \
           not self.config.enable_image_fetching:
            return
        # test if config.local_storage_path
        # is a directory
        if not os.path.isdir(self.config.local_storage_path):
            os.makedirs(self.config.local_storage_path)

        if not os.path.isdir(self.config.local_storage_path):
            raise Exception(self.config.local_storage_path +
                " directory does not seem to exist, "
                "you need to set this for image processing downloads"
            )

        # test to write a dummy file to the directory
        # to check is directory is writtable
        level, path = mkstemp(dir=self.config.local_storage_path)
        try:
            f = os.fdopen(level, "w")
            f.close()
            os.remove(path)
        except IOError:
            raise Exception(self.config.local_storage_path +
                " directory is not writeble, "
                "you need to set this for image processing downloads"
            )
