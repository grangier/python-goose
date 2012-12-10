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
from HTMLParser import HTMLParser
from goose.text import innerTrim
from goose.parsers import Parser


class OutputFormatter(object):

    def __init__(self, config):
        self.topNode = None
        self.config = config
        self.stopwordsCls = config.stopwordsCls

    def getLanguage(self, article):
        """\
        Returns the language is by the article or
        the configuration language
        """
        # we don't want to force the target laguage
        # so we use the article.metaLang
        if self.config.useMetaLanguge == True:
            if article.metaLang:
                return article.metaLang[:2]
        return self.config.targetLanguage

    def getTopNode(self):
        return self.topNode

    def getFormattedText(self, article):
        self.topNode = article.topNode
        self.removeNodesWithNegativeScores()
        self.convertLinksToText()
        self.replaceTagsWithText()
        self.removeParagraphsWithFewWords(article)
        return self.convertToText()

    def convertToText(self):
        txts = []
        for node in list(self.getTopNode()):
            txt = Parser.getText(node)
            if txt:
                txt = HTMLParser().unescape(txt)
                txts.append(innerTrim(txt))
        return '\n\n'.join(txts)

    def convertLinksToText(self):
        """\
        cleans up and converts any nodes that
        should be considered text into text
        """
        Parser.stripTags(self.getTopNode(), 'a')

    def removeNodesWithNegativeScores(self):
        """\
        if there are elements inside our top node
        that have a negative gravity score,
        let's give em the boot
        """
        gravityItems = self.topNode.cssselect("*[gravityScore]")
        for item in gravityItems:
            score = int(item.attrib.get('gravityScore'), 0)
            if score < 1:
                item.getparent().remove(item)

    def replaceTagsWithText(self):
        """\
        replace common tags with just
        text so we don't have any crazy formatting issues
        so replace <br>, <i>, <strong>, etc....
        with whatever text is inside them
        code : http://lxml.de/api/lxml.etree-module.html#strip_tags
        """
        Parser.stripTags(self.getTopNode(), 'b', 'strong', 'i', 'br')

    def removeParagraphsWithFewWords(self, article):
        """\
        remove paragraphs that have less than x number of words,
        would indicate that it's some sort of link
        """
        allNodes = Parser.getElementsByTags(self.getTopNode(), ['*'])  # .cssselect('*')
        allNodes.reverse()
        for el in allNodes:
            text = Parser.getText(el)
            stopWords = self.stopwordsCls(language=self.getLanguage(article)).getStopWordCount(text)
            if stopWords.getStopWordCount() < 3 \
                and len(Parser.getElementsByTag(el, tag='object')) == 0 \
                and len(Parser.getElementsByTag(el, tag='embed')) == 0:
                Parser.remove(el)
            # TODO
            # check if it is in the right place
            else:
                trimmed = Parser.getText(el)
                if trimmed.startswith("(") and trimmed.endswith(")"):
                    Parser.remove(el)


class StandardOutputFormatter(OutputFormatter):
    pass
