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

from goose.extractors import BaseExtractor

A_REL_TAG_SELECTOR = "a[rel=tag]"
A_HREF_TAG_SELECTOR = "a[href*='/tag/'], a[href*='/tags/'], a[href*='/topic/'], a[href*='?keyword=']"


class TagsExtractor(BaseExtractor):

    def extract(self):
        node = self.article.doc
        tags = []

        # node doesn't have chidren
        if len(list(node)) == 0:
            return tags

        elements = self.parser.css_select(node, A_REL_TAG_SELECTOR)
        if not elements:
            elements = self.parser.css_select(node, A_HREF_TAG_SELECTOR)
            if not elements:
                return tags

        for el in elements:
            tag = self.parser.getText(el)
            if tag:
                tags.append(tag)

        return list(set(tags))
