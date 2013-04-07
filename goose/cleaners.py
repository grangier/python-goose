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
        items = Parser.css_select(doc, "span[class~=dropcap], span[class~=drop_cap]")
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
        naughty_list = doc.xpath(self.nauthy_ids_re,
                                        namespaces={'re': self.regexp_namespace})
        for node in naughty_list:
            Parser.remove(node)

        # class
        naughty_classes = doc.xpath(self.nauthy_classes_re,
                                        namespaces={'re': self.regexp_namespace})
        for node in naughty_classes:
            Parser.remove(node)

        # name
        naughty_names = doc.xpath(self.nauthy_names_re,
                                        namespaces={'re': self.regexp_namespace})
        for node in naughty_names:
            Parser.remove(node)

        return doc

    def remove_nodes_regex(self, doc, pattern):
        for selector in ['id', 'class']:
            reg = "//*[re:test(@%s, '%s', 'i')]" % (selector, pattern)
            naughty_list = doc.xpath(reg, namespaces={'re': self.regexp_namespace})
            for node in naughty_list:
                Parser.remove(node)
        return doc

    def clean_para_spans(self, doc):
        spans = Parser.css_select(doc, 'p > span')
        for item in spans:
            item.drop_tag()
        return doc

    def get_flushed_buffer(self, replacement_text, doc):
        return Parser.textToPara(replacement_text)

    def get_replacement_nodes(self, doc, div):
        replacement_text = []
        nodes_to_return = []
        nodes_to_remove = []
        childs = Parser.childNodesWithText(div)

        for kid in childs:
            # node is a p
            # and already have some replacement text
            if Parser.getTag(kid) == 'p' and len(replacement_text) > 0:
                newNode = self.get_flushed_buffer(''.join(replacement_text), doc)
                nodes_to_return.append(newNode)
                replacement_text = []
                nodes_to_return.append(kid)
            # node is a text node
            elif Parser.isTextNode(kid):
                kid_text_node = kid
                kid_text = Parser.getText(kid)
                replace_text = self.tablines_replacements.replaceAll(kid_text)
                if(len(replace_text)) > 1:
                    previous_sibling_node = Parser.previousSibling(kid_text_node)
                    while previous_sibling_node is not None \
                        and Parser.getTag(previous_sibling_node) == "a" \
                        and Parser.getAttribute(previous_sibling_node, 'grv-usedalready') != 'yes':
                        outer = " " + Parser.outerHtml(previous_sibling_node) + " "
                        replacement_text.append(outer)
                        nodes_to_remove.append(previous_sibling_node)
                        Parser.setAttribute(previous_sibling_node,
                                    attr='grv-usedalready', value='yes')
                        prev = Parser.previousSibling(previous_sibling_node)
                        previous_sibling_node = prev if prev is not None else None
                    # append replace_text
                    replacement_text.append(replace_text)
                    #
                    next_sibling_node = Parser.nextSibling(kid_text_node)
                    while next_sibling_node is not None \
                        and Parser.getTag(next_sibling_node) == "a" \
                        and Parser.getAttribute(next_sibling_node, 'grv-usedalready') != 'yes':
                        outer = " " + Parser.outerHtml(next_sibling_node) + " "
                        replacement_text.append(outer)
                        nodes_to_remove.append(next_sibling_node)
                        Parser.setAttribute(next_sibling_node,
                                    attr='grv-usedalready', value='yes')
                        next = Parser.nextSibling(next_sibling_node)
                        previous_sibling_node = next if next is not None else None

            # otherwise
            else:
                nodes_to_return.append(kid)

        # flush out anything still remaining
        if(len(replacement_text) > 0):
            new_node = self.get_flushed_buffer(''.join(replacement_text), doc)
            nodes_to_return.append(new_node)
            replacement_text = []

        for n in nodes_to_remove:
            Parser.remove(n)

        return nodes_to_return

    def replace_with_para(self, doc, div):
        Parser.replaceTag(div, 'p')

    def div_to_para(self, doc, dom_type):
        bad_divs = 0
        else_divs = 0
        divs = Parser.getElementsByTag(doc, tag=dom_type)
        tags = ['a', 'blockquote', 'dl', 'div', 'img', 'ol', 'p', 'pre', 'table', 'ul']

        for div in divs:
            items = Parser.getElementsByTags(div, tags)
            if div is not None and len(items) == 0:
                self.replace_with_para(doc, div)
                bad_divs += 1
            elif div is not None:
                replaceNodes = self.get_replacement_nodes(doc, div)
                div.clear()

                for c, n in enumerate(replaceNodes):
                    div.insert(c, n)

                else_divs += 1

        return doc


class StandardDocumentCleaner(DocumentCleaner):
    pass
