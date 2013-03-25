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
class Article(object):
    
    def __init__(self):
        # title of the article
        self.title = None
        
        # stores the lovely, pure text from the article,
        # stripped of html, formatting, etc...
        # just raw text with paragraphs separated by newlines.
        # This is probably what you want to use.
        self.cleanedArticleText = u""
        
        # meta description field in HTML source
        self.metaDescription = u""
        
        # meta lang field in HTML source
        self.metaLang = u""
        
        # meta favicon field in HTML source
        self.metaFavicon = u""
        
        # meta keywords field in the HTML source
        self.metaKeywords = u""
        
        # The canonical link of this article if found in the meta data
        self.canonicalLink  = u""
        
        # holds the domain of this article we're parsing
        self.domain = u""
        
        # holds the top Element we think
        # is a candidate for the main body of the article
        self.topNode = None
        
        # holds the top Image object that
        # we think represents this article
        self.topImage = None
        
        # holds a set of tags that may have
        # been in the artcle, these are not meta keywords
        self.tags = set()
        
        # holds a list of any movies
        # we found on the page like youtube, vimeo
        self.movies = []
        
        # stores the final URL that we're going to try
        # and fetch content against, this would be expanded if any
        self.finalUrl = u""
        
        # stores the MD5 hash of the url
        # to use for various identification tasks
        self.linkhash = ""
        
        # stores the RAW HTML
        # straight from the network connection
        self.rawHtml = u""
        
        # the lxml Document object
        self.doc = None
        
        # this is the original JSoup document that contains
        # a pure object from the original HTML without any cleaning
        # options done on it
        self.rawDoc = None
        
        # Sometimes useful to try and know when
        # the publish date of an article was
        self.publishDate = None
        
        # A property bucket for consumers of goose to store custom data extractions.
        self.additionalData = {}

