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

import six

from goose.utils import FileHelper
from goose.utils.encoding import smart_unicode
from goose.utils.encoding import smart_str
from goose.utils.encoding import DjangoUnicodeDecodeError

TABSSPACE = re.compile(r'[\s\t]+')


def get_encodings_from_content(content):
    """
    Code from:
    https://github.com/sigmavirus24/requests-toolbelt/blob/master/requests_toolbelt/utils/deprecated.py
    Return encodings from given content string.
    :param content: string to extract encodings from.
    """
    if isinstance(content, six.binary_type) and six.PY3:
        find_charset = re.compile(
            br'<meta.*?charset=["\']*(.+?)["\'>]', flags=re.I
        ).findall

        find_pragma = re.compile(
            br'<meta.*?content=["\']*;?charset=(.+?)["\'>]', flags=re.I
        ).findall

        find_xml = re.compile(
            br'^<\?xml.*?encoding=["\']*(.+?)["\'>]'
        ).findall
    else:
        find_charset = re.compile(
            r'<meta.*?charset=["\']*(.+?)["\'>]', flags=re.I
        ).findall

        find_pragma = re.compile(
            r'<meta.*?content=["\']*;?charset=(.+?)["\'>]', flags=re.I
        ).findall

        find_xml = re.compile(
            r'^<\?xml.*?encoding=["\']*(.+?)["\'>]'
        ).findall
    return find_charset(content) + find_pragma(content) + find_xml(content)


def innerTrim(value):
    if isinstance(value, (six.text_type, six.string_types)):
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
    except Exception:
        value = string_org
    return value


class WordStats(object):

    def __init__(self):
        # total number of stopwords or
        # good words that we can calculate
        self.stop_word_count = 0

        # total number of words on a node
        self.word_count = 0

        # holds an actual list
        # of the stop words we found
        self.stop_words = []

    def get_stop_words(self):
        return self.stop_words

    def set_stop_words(self, words):
        self.stop_words = words

    def get_stopword_count(self):
        return self.stop_word_count

    def set_stopword_count(self, wordcount):
        self.stop_word_count = wordcount

    def get_word_count(self):
        return self.word_count

    def set_word_count(self, cnt):
        self.word_count = cnt


class StopWords(object):

    PUNCTUATION = re.compile("[^\\p{Ll}\\p{Lu}\\p{Lt}\\p{Lo}\\p{Nd}\\p{Pc}\\s]")
    _cached_stop_words = {}

    def __init__(self, language='en'):
        # TODO replace 'x' with class
        # to generate dynamic path for file to load
        if not language in self._cached_stop_words:
            path = os.path.join('text', 'stopwords-%s.txt' % language)
            try:
                content = FileHelper.loadResourceFile(path)
                word_list = content.splitlines()
            except IOError:
                word_list = []
            self._cached_stop_words[language] = set(word_list)
        self.STOP_WORDS = self._cached_stop_words[language]

    def remove_punctuation(self, content):
        # code taken form
        # http://stackoverflow.com/questions/265960/best-way-to-strip-punctuation-from-a-string-in-python
        if not isinstance(content, six.text_type):
            content = content.decode('utf-8')
        tbl = dict.fromkeys(ord(x) for x in string.punctuation)
        return content.translate(tbl)

    def candiate_words(self, stripped_input):
        return stripped_input.split(' ')

    def get_stopword_count(self, content):
        if not content:
            return WordStats()
        ws = WordStats()
        stripped_input = self.remove_punctuation(content)
        candiate_words = self.candiate_words(stripped_input)
        overlapping_stopwords = []
        c = 0
        for w in candiate_words:
            c += 1
            if w.lower() in self.STOP_WORDS:
                overlapping_stopwords.append(w.lower())

        ws.set_word_count(c)
        ws.set_stopword_count(len(overlapping_stopwords))
        ws.set_stop_words(overlapping_stopwords)
        return ws


class StopWordsChinese(StopWords):
    """
    Chinese segmentation
    """
    def __init__(self, language='zh'):
        # force zh languahe code
        super(StopWordsChinese, self).__init__(language='zh')

    def candiate_words(self, stripped_input):
        # jieba build a tree that takes sometime
        # avoid building the tree if we don't use
        # chinese language
        import jieba
        return jieba.cut(stripped_input, cut_all=True)


class StopWordsArabic(StopWords):
    """
    Arabic segmentation
    """
    def __init__(self, language='ar'):
        # force ar languahe code
        super(StopWordsArabic, self).__init__(language='ar')

    def remove_punctuation(self, content):
        return content

    def candiate_words(self, stripped_input):
        import nltk
        s = nltk.stem.isri.ISRIStemmer()
        words = []
        for word in nltk.tokenize.wordpunct_tokenize(stripped_input):
            words.append(s.stem(word))
        return words


class StopWordsKorean(StopWords):
    """
    Korean segmentation
    """
    def __init__(self, language='ko'):
        super(StopWordsKorean, self).__init__(language='ko')

    def get_stopword_count(self, content):
        if not content:
            return WordStats()
        ws = WordStats()
        stripped_input = self.remove_punctuation(content)
        candiate_words = self.candiate_words(stripped_input)
        overlapping_stopwords = []
        c = 0
        for w in candiate_words:
            c += 1
            for stop_word in self.STOP_WORDS:
                overlapping_stopwords.append(stop_word)

        ws.set_word_count(c)
        ws.set_stopword_count(len(overlapping_stopwords))
        ws.set_stop_words(overlapping_stopwords)
        return ws
