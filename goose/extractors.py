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
from copy import deepcopy
from urlparse import urlparse, urljoin
from goose.utils import StringSplitter
from goose.utils import StringReplacement
from goose.utils import ReplaceSequence
from goose.parsers import Parser

MOTLEY_REPLACEMENT = StringReplacement("&#65533;", "")
ESCAPED_FRAGMENT_REPLACEMENT = StringReplacement(u"#!", u"?_escaped_fragment_=")
TITLE_REPLACEMENTS = ReplaceSequence().create(u"&raquo;").append(u"»")
PIPE_SPLITTER = StringSplitter("\\|")
DASH_SPLITTER = StringSplitter(" - ")
ARROWS_SPLITTER = StringSplitter("»")
COLON_SPLITTER = StringSplitter(":")
SPACE_SPLITTER = StringSplitter(' ')
NO_STRINGS = set()
# TODO
# A_REL_TAG_SELECTOR = "a[rel=tag], a[href*=/tag/]"
A_REL_TAG_SELECTOR = "a[rel=tag]"
RE_LANG = r'^[A-Za-z]{2}$'


class ContentExtractor(object):

    def __init__(self, config):
        self.config = config
        self.language = config.target_language
        self.stopwords_class = config.stopwords_class

    def get_language(self, article):
        """\
        Returns the language is by the article or
        the configuration language
        """
        # we don't want to force the target laguage
        # so we use the article.meta_lang
        if self.config.use_meta_language == True:
            if article.meta_lang:
                self.language = article.meta_lang[:2]
        self.language = self.config.target_language

    def get_title(self, article):
        """\
        Fetch the article title and analyze it
        """

        title = ''
        doc = article.doc

        titleElem = Parser.getElementsByTag(doc, tag='title')
        # no title found
        if titleElem is None or len(titleElem) == 0:
            return title

        # title elem found
        titleText = Parser.getText(titleElem[0])
        usedDelimeter = False

        # split title with |
        if '|' in titleText:
            titleText = self.split_title(titleText, PIPE_SPLITTER)
            usedDelimeter = True

        # split title with -
        if not usedDelimeter and '-' in titleText:
            titleText = self.split_title(titleText, DASH_SPLITTER)
            usedDelimeter = True

        # split title with »
        if not usedDelimeter and u'»' in titleText:
            titleText = self.split_title(titleText, ARROWS_SPLITTER)
            usedDelimeter = True

        # split title with :
        if not usedDelimeter and ':' in titleText:
            titleText = self.split_title(titleText, COLON_SPLITTER)
            usedDelimeter = True

        title = MOTLEY_REPLACEMENT.replaceAll(titleText)
        return title

    def split_title(self, title, splitter):
        """\
        Split the title to best part possible
        """
        largetTextLen = 0
        largeTextIndex = 0
        titlePieces = splitter.split(title)

        # find the largest title piece
        for i in range(len(titlePieces)):
            current = titlePieces[i]
            if len(current) > largetTextLen:
                largetTextLen = len(current)
                largeTextIndex = i

        # replace content
        title = titlePieces[largeTextIndex]
        return TITLE_REPLACEMENTS.replaceAll(title).strip()

    def get_favicon(self, article):
        """\
        Extract the favicon from a website
        http://en.wikipedia.org/wiki/Favicon
        <link rel="shortcut icon" type="image/png" href="favicon.png" />
        <link rel="icon" type="image/png" href="favicon.png" />
        """
        kwargs = {'tag': 'link', 'attr': 'rel', 'value': 'icon'}
        meta = Parser.getElementsByTag(article.doc, **kwargs)
        if meta:
            favicon = meta[0].attrib.get('href')
            return favicon
        return ''

    def get_meta_lang(self, article):
        """\
        Extract content language from meta
        """
        # we have a lang attribute in html
        attr = Parser.getAttribute(article.doc, attr='lang')
        if attr is None:
            # look up for a Content-Language in meta
            items = [
                {'tag': 'meta', 'attr': 'http-equiv', 'value': 'content-language'},
                {'tag': 'meta', 'attr': 'name', 'value': 'lang'}
            ]
            for item in items:
                meta = Parser.getElementsByTag(article.doc, **item)
                if meta:
                    attr = Parser.getAttribute(meta[0], attr='content')
                    break

        if attr:
            value = attr[:2]
            if re.search(RE_LANG, value):
                self.language = value.lower()
                return value.lower()

        return None

    def get_meta_content(self, doc, metaName):
        """\
        Extract a given meta content form document
        """
        meta = doc.cssselect(metaName)
        content = None

        if meta is not None and len(meta) > 0:
            content = meta[0].attrib.get('content')

        if content:
            return content.strip()

        return ''

    def get_meta_description(self, article):
        """\
        if the article has meta description set in the source, use that
        """
        return self.get_meta_content(article.doc, "meta[name=description]")

    def get_meta_keywords(self, article):
        """\
        if the article has meta keywords set in the source, use that
        """
        return self.get_meta_content(article.doc, "meta[name=keywords]")

    def get_canonical_link(self, article):
        """\
        if the article has meta canonical link set in the url
        """
        kwargs = {'tag': 'link', 'attr': 'rel', 'value': 'canonical'}
        meta = Parser.getElementsByTag(article.doc, **kwargs)
        if meta is not None and len(meta) > 0:
            href = meta[0].attrib.get('href')
            if href:
                href = href.strip()
                o = urlparse(href)
                if not o.hostname:
                    z = urlparse(article.final_url)
                    domain = '%s://%s' % (z.scheme, z.hostname)
                    href = urljoin(domain, href)
                return href
        return article.final_url

    def get_domain(self, url):
        o = urlparse(url)
        return o.hostname

    def extract_tags(self, article):
        node = article.doc

        # node doesn't have chidren
        if len(list(node)) == 0:
            return NO_STRINGS

        elements = node.cssselect(A_REL_TAG_SELECTOR)
        if elements is None:
            return NO_STRINGS

        tags = []
        for el in elements:
            tag = Parser.getText(el)
            if tag:
                tags.append(tag)

        return set(tags)

    def calculate_best_node(self, article):
        doc = article.doc
        topNode = None
        nodesToCheck = self.nodes_to_check(doc)

        startingBoost = float(1.0)
        cnt = 0
        i = 0
        parentNodes = []
        nodesWithText = []

        for node in nodesToCheck:
            nodeText = Parser.getText(node)
            wordStats = self.stopwords_class(language=self.language).getStopWordCount(nodeText)
            highLinkDensity = self.is_highlink_density(node)
            if wordStats.getStopWordCount() > 2 and not highLinkDensity:
                nodesWithText.append(node)

        numberOfNodes = len(nodesWithText)
        negativeScoring = 0
        bottomNodesForNegativeScore = float(numberOfNodes) * 0.25

        for node in nodesWithText:
            boostScore = float(0)
            # boost
            if(self.is_boostable(node)):
                if cnt >= 0:
                    boostScore = float((1.0 / startingBoost) * 50)
                    startingBoost += 1
            # numberOfNodes
            if numberOfNodes > 15:
                if (numberOfNodes - i) <= bottomNodesForNegativeScore:
                    booster = float(bottomNodesForNegativeScore - (numberOfNodes - i))
                    boostScore = float(-pow(booster, float(2)))
                    negscore = -abs(boostScore) + negativeScoring
                    if negscore > 40:
                        boostScore = float(5)

            nodeText = Parser.getText(node)
            wordStats = self.stopwords_class(language=self.language).getStopWordCount(nodeText)
            upscore = int(wordStats.getStopWordCount() + boostScore)

            # parent node
            parentNode = Parser.getParent(node)
            self.update_score(parentNode, upscore)
            self.update_node_count(node.getparent(), 1)

            if node.getparent() not in parentNodes:
                parentNodes.append(node.getparent())

            # parentparent node
            parentParentNode = Parser.getParent(parentNode)
            if parentParentNode is not None:
                self.update_node_count(parentParentNode, 1)
                self.update_score(parentParentNode, upscore / 2)
                if parentParentNode not in parentNodes:
                    parentNodes.append(parentParentNode)
            cnt += 1
            i += 1

        topNodeScore = 0
        for e in parentNodes:
            score = self.get_score(e)

            if score > topNodeScore:
                topNode = e
                topNodeScore = score

            if topNode is None:
                topNode = e

        return topNode

    def is_boostable(self, node):
        """\
        alot of times the first paragraph might be the caption under an image
        so we'll want to make sure if we're going to boost a parent node that
        it should be connected to other paragraphs,
        at least for the first n paragraphs so we'll want to make sure that
        the next sibling is a paragraph and has at
        least some substatial weight to it
        """
        para = "p"
        stepsAway = 0
        minimumStopWordCount = 5
        maxStepsAwayFromNode = 3

        nodes = self.walk_siblings(node)
        for currentNode in nodes:
            # p
            if currentNode.tag == para:
                if stepsAway >= maxStepsAwayFromNode:
                    return False
                paraText = Parser.getText(currentNode)
                wordStats = self.stopwords_class(language=self.language).getStopWordCount(paraText)
                if wordStats.getStopWordCount() > minimumStopWordCount:
                    return True
                stepsAway += 1
        return False

    def walk_siblings(self, node):
        currentSibling = Parser.previousSibling(node)
        b = []
        while currentSibling is not None:
            b.append(currentSibling)
            previousSibling = Parser.previousSibling(currentSibling)
            currentSibling = None if previousSibling is None else previousSibling
        return b

    def add_siblings(self, topNode):
        baselineScoreForSiblingParagraphs = self.get_siblings_score(topNode)
        results = self.walk_siblings(topNode)
        for currentNode in results:
            ps = self.get_siblings_content(currentNode, baselineScoreForSiblingParagraphs)
            for p in ps:
                topNode.insert(0, p)
        return topNode

    def get_siblings_content(self, currentSibling, baselineScoreForSiblingParagraphs):
        """\
        adds any siblings that may have a decent score to this node
        """
        if currentSibling.tag == 'p' and len(Parser.getText(currentSibling)) > 0:
            e0 = currentSibling
            if e0.tail:
                e0 = deepcopy(e0)
                e0.tail = ''
            return [e0]
        else:
            potentialParagraphs = Parser.getElementsByTag(currentSibling, tag='p')
            if potentialParagraphs is None:
                return None
            else:
                ps = []
                for firstParagraph in potentialParagraphs:
                    text = Parser.getText(firstParagraph)
                    if len(text) > 0:
                        wordStats = self.stopwords_class(language=self.language).getStopWordCount(text)
                        paragraphScore = wordStats.getStopWordCount()
                        siblingBaseLineScore = float(.30)
                        highLinkDensity = self.is_highlink_density(firstParagraph)
                        score = float(baselineScoreForSiblingParagraphs * siblingBaseLineScore)
                        if score < paragraphScore and not highLinkDensity:
                            p = Parser.createElement(tag='p', text=text, tail=None)
                            ps.append(p)
                return ps

    def get_siblings_score(self, topNode):
        """\
        we could have long articles that have tons of paragraphs
        so if we tried to calculate the base score against
        the total text score of those paragraphs it would be unfair.
        So we need to normalize the score based on the average scoring
        of the paragraphs within the top node.
        For example if our total score of 10 paragraphs was 1000
        but each had an average value of 100 then 100 should be our base.
        """
        base = 100000
        numberOfParagraphs = 0
        scoreOfParagraphs = 0
        nodesToCheck = Parser.getElementsByTag(topNode, tag='p')

        for node in nodesToCheck:
            nodeText = Parser.getText(node)
            wordStats = self.stopwords_class(language=self.language).getStopWordCount(nodeText)
            highLinkDensity = self.is_highlink_density(node)
            if wordStats.getStopWordCount() > 2 and not highLinkDensity:
                numberOfParagraphs += 1
                scoreOfParagraphs += wordStats.getStopWordCount()

        if numberOfParagraphs > 0:
            base = scoreOfParagraphs / numberOfParagraphs

        return base

    def update_score(self, node, addToScore):
        """\
        adds a score to the gravityScore Attribute we put on divs
        we'll get the current score then add the score
        we're passing in to the current
        """
        currentScore = 0
        scoreString = node.attrib.get('gravityScore')
        if scoreString:
            currentScore = int(scoreString)

        newScore = currentScore + addToScore
        node.set("gravityScore", str(newScore))

    def update_node_count(self, node, addToCount):
        """\
        stores how many decent nodes are under a parent node
        """
        currentScore = 0
        countString = node.attrib.get('gravityNodes')
        if countString:
            currentScore = int(countString)

        newScore = currentScore + addToCount
        node.set("gravityNodes", str(newScore))

    def is_highlink_density(self, e):
        """\
        checks the density of links within a node,
        is there not much text and most of it contains linky shit?
        if so it's no good
        """
        links = Parser.getElementsByTag(e, tag='a')
        if links is None or len(links) == 0:
            return False

        text = Parser.getText(e)
        words = text.split(' ')
        numberOfWords = float(len(words))
        sb = []
        for link in links:
            sb.append(Parser.getText(link))

        linkText = ''.join(sb)
        linkWords = linkText.split(' ')
        numberOfLinkWords = float(len(linkWords))
        numberOfLinks = float(len(links))
        linkDivisor = float(numberOfLinkWords / numberOfWords)
        score = float(linkDivisor * numberOfLinks)
        if score >= 1.0:
            return True
        return False
        # return True if score > 1.0 else False

    def get_score(self, node):
        """\
        returns the gravityScore as an integer from this node
        """
        return self.get_node_gravity_score(node) or 0

    def get_node_gravity_score(self, node):
        grvScoreString = node.attrib.get('gravityScore')
        if not grvScoreString:
            return None
        return int(grvScoreString)

    def nodes_to_check(self, doc):
        """\
        returns a list of nodes we want to search
        on like paragraphs and tables
        """
        nodesToCheck = []
        for tag in ['p', 'pre', 'td']:
            items = Parser.getElementsByTag(doc, tag=tag)
            nodesToCheck += items
        return nodesToCheck

    def is_table_and_no_para_exist(self, e):
        subParagraphs = Parser.getElementsByTag(e, tag='p')
        for p in subParagraphs:
            txt = Parser.getText(p)
            if len(txt) < 25:
                Parser.remove(p)

        subParagraphs2 = Parser.getElementsByTag(e, tag='p')
        if len(subParagraphs2) == 0 and e.tag is not "td":
            return True
        return False

    def is_nodescore_threshold_met(self, node, e):
        topNodeScore = self.get_score(node)
        currentNodeScore = self.get_score(e)
        thresholdScore = float(topNodeScore * .08)

        if (currentNodeScore < thresholdScore) and e.tag != 'td':
            return False
        return True

    def post_cleanup(self, targetNode):
        """\
        remove any divs that looks like non-content,
        clusters of links, or paras with no gusto
        """
        node = self.add_siblings(targetNode)
        for e in node.getchildren():
            if e.tag != 'p':
                if self.is_highlink_density(e) \
                    or self.is_table_and_no_para_exist(e) \
                    or not self.is_nodescore_threshold_met(node, e):
                    Parser.remove(e)
        return node


class StandardContentExtractor(ContentExtractor):
    pass
