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
from goose.Configuration import Configuration
from goose.Crawler import CrawlCandidate
from goose.Crawler import Crawler

class Goose(object):
    """\
    
    """
    def __init__(self, config=None):
        self.config = config or Configuration()
        self.initializeEnvironment()
    
    
    def extractContent(self, url=None, rawHTML=None):
        """\
        Main method to extract an article object from a URL,
        pass in a url and get back a Article
        """
        cc = CrawlCandidate(self.config, url, rawHTML)
        return self.sendToActor(cc)
    
    
    def shutdownNetwork(self):
        pass
    
    
    def sendToActor(self, crawlCandiate):
        crawler = Crawler(self.config)
        article = crawler.crawl(crawlCandiate)
        return article
    
    
    def initializeEnvironment(self):
        # test if config.localStoragePath
        # is a directory
        if not os.path.isdir(self.config.localStoragePath):
            os.makedirs(self.config.localStoragePath)
        
        if not os.path.isdir(self.config.localStoragePath):
            raise Exception(self.config.localStoragePath +
                " directory does not seem to exist, "
                "you need to set this for image processing downloads"
            )
        
        # test to write a dummy file to the directory
        # to check is directory is writtable
        path = '%s/test.txt' % self.config.localStoragePath
        try:
            f = open(path, 'w')
            f.close()
            os.remove(path)
        except IOError:
            raise Exception(self.config.localStoragePath +
                " directory is not writeble, "
                "you need to set this for image processing downloads"
            )
        
        
    
    