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
import re
import string
from goose.utils import FileHelper

from goose.utils.encoding import smart_unicode
from goose.utils.encoding import smart_str
from goose.utils.encoding import DjangoUnicodeDecodeError

TABSSPACE = re.compile(r'[\s\t]+')

def innerTrim(string):
    if isinstance(string, (unicode, str)):
        # remove tab and white space
        string = re.sub(TABSSPACE, ' ',string)
        string = ''.join(string.splitlines())
        return string.strip()
    return ''


def encodeValue(string):
    string_org = string
    try:
        string = smart_unicode(string)
    except (UnicodeEncodeError, DjangoUnicodeDecodeError):
        string = smart_str(string)
    except:
        string = string_org
    return string


class WordStats(object):
    
    def __init__(self):
        # total number of stopwords or
        # good words that we can calculate
        self.stopWordCount = 0
        
        # total number of words on a node
        self.wordCount = 0
        
        # holds an actual list
        # of the stop words we found
        self.stopWords = []
    
    
    def getStopWords(self):
        return self.stopWords
    
    
    def setStopWords(self, words):
        self.stopWords = words
    
    
    def getStopWordCount(self):
        return self.stopWordCount
    
    
    def setStopWordCount(self, wordcount):
        self.stopWordCount = wordcount
    
    
    def getWordCount(self):
        return self.wordCount
    
    
    def setWordCount(self, cnt):
        self.wordCount = cnt
    



class StopWords(object):
    
    def __init__(self, language='en'):
        self.PUNCTUATION = re.compile("[^\\p{Ll}\\p{Lu}\\p{Lt}\\p{Lo}\\p{Nd}\\p{Pc}\\s]")
        # TODO replace 'x' with class
        # to generate dynamic path for file to load
        path = 'text/stopwords-%s.txt' % language
        self.STOP_WORDS = set(FileHelper.loadResourceFile(path).splitlines())
    
    
    def removePunctuation(self, content):
        # code taken form
        # http://stackoverflow.com/questions/265960/best-way-to-strip-punctuation-from-a-string-in-python
        if isinstance(content, unicode):
            content = content.encode('utf-8')
        table = string.maketrans("","")
        return content.translate(table, string.punctuation)
    
    
    def getStopWordCount(self, content):
        if not content:
            return WordStats()
        ws = WordStats()
        strippedInput = self.removePunctuation(content)
        candidateWords = strippedInput.split(' ')
        overlappingStopWords = []
        for w in candidateWords:
            if w.lower() in self.STOP_WORDS:
                overlappingStopWords.append(w.lower())
        
        ws.setWordCount(len(candidateWords))
        ws.setStopWordCount(len(overlappingStopWords))
        ws.setStopWords(overlappingStopWords)
        return ws
        
