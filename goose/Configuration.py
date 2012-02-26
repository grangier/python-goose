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
class Configuration(object):
    
    def __init__(self):
        # this is the local storage path used to place 
        # images to inspect them, should be writable
        self.localStoragePath = "/tmp/goosetmp"
        
        # What's the minimum bytes for an image we'd accept is, 
        # alot of times we want to filter out the author's little images
        # in the beginning of the article
        self.minBytesForImages = 4500
        
        # set this guy to false if you don't care about getting images, 
        # otherwise you can either use the default
        # image extractor to implement the ImageExtractor 
        # interface to build your own
        self.enableImageFetching = True
        
        # path to your imagemagick convert executable, 
        # on the mac using mac ports this is the default listed
        self.imagemagickConvertPath = "/opt/local/bin/convert"
        
        # path to your imagemagick identify executable
        self.imagemagickIdentifyPath = "/opt/local/bin/identify"
        
        # used as the user agent that 
        # is sent with your web requests to extract an article
        # self.browserUserAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2)"\
        #                         " AppleWebKit/534.52.7 (KHTML, like Gecko) "\
        #                         "Version/5.1.2 Safari/534.52.7"
        self.browserUserAgent = 'Goose/1.0'
        
        # TODO
        self.publishDateExtractor = None
        
        # TODO
        self.additionalDataExtractor = None
    
    
    def getPublishDateExtractor(self):
        return self.publishDateExtractor
    
    def setPublishDateExtractor(self, extractor):
        """\
        Pass in to extract article publish dates.
        @param extractor a concrete instance of PublishDateExtractor
        """
        if not extractor:
            raise ValueError("extractor must not be null!")
        self.publishDateExtractor = extractor
        
    def getAdditionalDataExtractor(self):
        return self.additionalDataExtractor
        
    def setAdditionalDataExtractor(self, extractor):
        """\
        Pass in to extract any additional data not defined within
        @param extractor a concrete instance of AdditionalDataExtractor
        """
        if not extractor:
            raise ValueError("extractor must not be null!")
        self.additionalDataExtractor = extractor
        
    