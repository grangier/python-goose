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
import re
import string
from goose.utils import FileHelper
from goose.utils.encoding import smart_unicode
from goose.utils.encoding import smart_str
from goose.utils.encoding import DjangoUnicodeDecodeError

TABSSPACE = re.compile(r'[\s\t]+')


def innerTrim(value):
    if isinstance(value, (unicode, str)):
        # remove tab and white space
        value = re.sub(TABSSPACE, ' ', value)
        value = ''.join(value.splitlines())
        return value.strip()
    return ''


def encodeValue(value):
    string_org = value
    try:
        value = smart_unicode(value)
    except (UnicodeEncodeError, DjangoUnicodeDecodeError):
        value = smart_str(value)
    except:
        value = string_org
    return value


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

    PUNCTUATION = re.compile("[^\\p{Ll}\\p{Lu}\\p{Lt}\\p{Lo}\\p{Nd}\\p{Pc}\\s]")
    TRANS_TABLE = string.maketrans('', '')
    _cached_stop_words = {}

    def __init__(self, language='en'):
        # TODO replace 'x' with class
        # to generate dynamic path for file to load
        if not language in self._cached_stop_words:
            path = os.path.join('text', 'stopwords-%s.txt' % language)
            self._cached_stop_words[language] = set(FileHelper.loadResourceFile(path).splitlines())
        self.STOP_WORDS = self._cached_stop_words[language]

    def removePunctuation(self, content):
        # code taken form
        # http://stackoverflow.com/questions/265960/best-way-to-strip-punctuation-from-a-string-in-python
        if isinstance(content, unicode):
            content = content.encode('utf-8')
        return content.translate(self.TRANS_TABLE, string.punctuation)

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


class StopWordsChinese(StopWords):
    """

    """
    def __init__(self, language='zh'):
        # force zh languahe code
        language = 'zh'
        if not language in self._cached_stop_words:
            path = os.path.join('text', 'stopwords-%s.txt' % language)
            self._cached_stop_words[language] = set(FileHelper.loadResourceFile(path).splitlines())
        self.STOP_WORDS = self._cached_stop_words[language]

    def getStopWordCount(self, content):
        # jieba build a tree that takes sometime
        # avoid building the tree if we don't use
        # chinese language
        import jieba

        if not content:
            return WordStats()
        ws = WordStats()
        strippedInput = self.removePunctuation(content)
        candidateWords = jieba.cut(strippedInput, cut_all=True)
        overlappingStopWords = []
        c = 0
        for w in candidateWords:
            c += 1
            if w.lower() in self.STOP_WORDS:
                overlappingStopWords.append(w.lower())

        ws.setWordCount(c)
        ws.setStopWordCount(len(overlappingStopWords))
        ws.setStopWords(overlappingStopWords)
        return ws
