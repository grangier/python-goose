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


class AuthorsExtractor(BaseExtractor):

    def extract(self):
        authors = []
        author_nodes = self.parser.getElementsByTag(
                            self.article.doc,
                            attr='itemprop',
                            value='author')

        for author in author_nodes:
            name_nodes = self.parser.getElementsByTag(
                            author,
                            attr='itemprop',
                            value='name')

            if len(name_nodes) > 0:
                name = self.parser.getText(name_nodes[0])
                authors.append(name)

        return list(set(authors))
