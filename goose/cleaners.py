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
from goose.parsers import Parser
from goose.utils import ReplaceSequence


class DocumentCleaner(object):

    def __init__(self):

        self.remove_nodes_re = (
        "^side$|combx|retweet|mediaarticlerelated|menucontainer|navbar"
        "|comment|PopularQuestions|contact|foot|footer|Footer|footnote"
        "|cnn_strycaptiontxt|links|meta$|scroll|shoutbox|sponsor"
        "|tags|socialnetworking|socialNetworking|cnnStryHghLght"
        "|cnn_stryspcvbx|^inset$|pagetools|post-attributes"
        "|welcome_form|contentTools2|the_answers"
        "|communitypromo|runaroundLeft|subscribe|vcard|articleheadings"
        "|date|^print$|popup|author-dropdown|tools|socialtools|byline"
        "|konafilter|KonaFilter|breadcrumbs|^fn$|wp-caption-text"
        "|source|legende|ajoutVideo|timestamp"
        )
        self.regexp_namespace = "http://exslt.org/regular-expressions"
        self.nauthy_ids_re = "//*[re:test(@id, '%s', 'i')]" % self.remove_nodes_re
        self.nauthy_classes_re = "//*[re:test(@class, '%s', 'i')]" % self.remove_nodes_re
        self.nauthy_names_re = "//*[re:test(@name, '%s', 'i')]" % self.remove_nodes_re
        self.div_to_p_re = r"<(a|blockquote|dl|div|img|ol|p|pre|table|ul)"
        self.caption_re = "^caption$"
        self.google_re = " google "
        self.entries_re = "^[^entry-]more.*$"
        self.facebook_re = "[^-]facebook"
        self.facebook_braodcasting_re = "facebook-broadcasting"
        self.twitter_re = "[^-]twitter"
        self.tablines_replacements = ReplaceSequence()\
                                            .create("\n", "\n\n")\
                                            .append("\t")\
                                            .append("^\\s+$")

    def clean(self, article):

        doc_to_clean = article.doc
        doc_to_clean = self.clean_em_tags(doc_to_clean)
        doc_to_clean = self.remove_drop_caps(doc_to_clean)
        doc_to_clean = self.remove_scripts_styles(doc_to_clean)
        doc_to_clean = self.clean_bad_tags(doc_to_clean)
        doc_to_clean = self.remove_nodes_regex(doc_to_clean, self.caption_re)
        doc_to_clean = self.remove_nodes_regex(doc_to_clean, self.google_re)
        doc_to_clean = self.remove_nodes_regex(doc_to_clean, self.entries_re)
        doc_to_clean = self.remove_nodes_regex(doc_to_clean, self.facebook_re)
        doc_to_clean = self.remove_nodes_regex(doc_to_clean, self.facebook_braodcasting_re)
        doc_to_clean = self.remove_nodes_regex(doc_to_clean, self.twitter_re)
        doc_to_clean = self.clean_para_spans(doc_to_clean)
        doc_to_clean = self.div_to_para(doc_to_clean, 'div')
        doc_to_clean = self.div_to_para(doc_to_clean, 'span')
        return doc_to_clean

    def clean_em_tags(self, doc):
        ems = Parser.getElementsByTag(doc, tag='em')
        for node in ems:
            images = Parser.getElementsByTag(node, tag='img')
            if len(images) == 0:
                node.drop_tag()
        return doc

    def remove_drop_caps(self, doc):
        items = doc.cssselect("span[class~=dropcap], span[class~=drop_cap]")
        for item in items:
            item.drop_tag()

        return doc

    def remove_scripts_styles(self, doc):
        # remove scripts
        scripts = Parser.getElementsByTag(doc, tag='script')
        for item in scripts:
            Parser.remove(item)

        # remove styles
        styles = Parser.getElementsByTag(doc, tag='style')
        for item in styles:
            Parser.remove(item)

        # remove comments
        comments = Parser.getComments(doc)
        for item in comments:
            Parser.remove(item)

        return doc

    def clean_bad_tags(self, doc):

        # ids
        naughtyList = doc.xpath(self.nauthy_ids_re,
                                        namespaces={'re': self.regexp_namespace})
        for node in naughtyList:
            Parser.remove(node)

        # class
        naughtyClasses = doc.xpath(self.nauthy_classes_re,
                                        namespaces={'re': self.regexp_namespace})
        for node in naughtyClasses:
            Parser.remove(node)

        # name
        naughtyNames = doc.xpath(self.nauthy_names_re,
                                        namespaces={'re': self.regexp_namespace})
        for node in naughtyNames:
            Parser.remove(node)

        return doc

    def remove_nodes_regex(self, doc, pattern):
        for selector in ['id', 'class']:
            reg = "//*[re:test(@%s, '%s', 'i')]" % (selector, pattern)
            naughtyList = doc.xpath(reg, namespaces={'re': self.regexp_namespace})
            for node in naughtyList:
                Parser.remove(node)
        return doc

    def clean_para_spans(self, doc):
        spans = doc.cssselect('p > span')
        for item in spans:
            item.drop_tag()
        return doc

    def get_flushed_buffer(self, replacementText, doc):
        return Parser.textToPara(replacementText)

    def get_replacement_nodes(self, doc, div):
        replacementText = []
        nodesToReturn = []
        nodesToRemove = []
        childs = Parser.childNodesWithText(div)

        for kid in childs:
            # node is a p
            # and already have some replacement text
            if Parser.getTag(kid) == 'p' and len(replacementText) > 0:
                newNode = self.get_flushed_buffer(''.join(replacementText), doc)
                nodesToReturn.append(newNode)
                replacementText = []
                nodesToReturn.append(kid)
            # node is a text node
            elif Parser.isTextNode(kid):
                kidTextNode = kid
                kidText = Parser.getText(kid)
                replaceText = self.tablines_replacements.replaceAll(kidText)
                if(len(replaceText)) > 1:
                    prevSibNode = Parser.previousSibling(kidTextNode)
                    while prevSibNode is not None \
                        and Parser.getTag(prevSibNode) == "a" \
                        and Parser.getAttribute(prevSibNode, 'grv-usedalready') != 'yes':
                        outer = " " + Parser.outerHtml(prevSibNode) + " "
                        replacementText.append(outer)
                        nodesToRemove.append(prevSibNode)
                        Parser.setAttribute(prevSibNode,
                                    attr='grv-usedalready', value='yes')
                        prev = Parser.previousSibling(prevSibNode)
                        prevSibNode = prev if prev is not None else None
                    # append replaceText
                    replacementText.append(replaceText)
                    #
                    nextSibNode = Parser.nextSibling(kidTextNode)
                    while nextSibNode is not None \
                        and Parser.getTag(nextSibNode) == "a" \
                        and Parser.getAttribute(nextSibNode, 'grv-usedalready') != 'yes':
                        outer = " " + Parser.outerHtml(nextSibNode) + " "
                        replacementText.append(outer)
                        nodesToRemove.append(nextSibNode)
                        Parser.setAttribute(nextSibNode,
                                    attr='grv-usedalready', value='yes')
                        next = Parser.nextSibling(nextSibNode)
                        prevSibNode = next if next is not None else None

            # otherwise
            else:
                nodesToReturn.append(kid)

        # flush out anything still remaining
        if(len(replacementText) > 0):
            newNode = self.get_flushed_buffer(''.join(replacementText), doc)
            nodesToReturn.append(newNode)
            replacementText = []

        for n in nodesToRemove:
            Parser.remove(n)

        return nodesToReturn

    def replace_with_para(self, doc, div):
        Parser.replaceTag(div, 'p')

    def div_to_para(self, doc, domType):
        badDivs = 0
        elseDivs = 0
        divs = Parser.getElementsByTag(doc, tag=domType)
        tags = ['a', 'blockquote', 'dl', 'div', 'img', 'ol', 'p', 'pre', 'table', 'ul']

        for div in divs:
            items = Parser.getElementsByTags(div, tags)
            if div is not None and len(items) == 0:
                self.replace_with_para(doc, div)
                badDivs += 1
            elif div is not None:
                replaceNodes = self.get_replacement_nodes(doc, div)
                div.clear()

                for c, n in enumerate(replaceNodes):
                    div.insert(c, n)

                elseDivs += 1

        return doc


class StandardDocumentCleaner(DocumentCleaner):
    pass
