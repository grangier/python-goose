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
import glob
from copy import deepcopy
from goose.article import Article
from goose.utils import URLHelper, RawHelper
from goose.extractors import StandardContentExtractor
from goose.cleaners import StandardDocumentCleaner
from goose.outputformatters import StandardOutputFormatter
from goose.images.extractors import UpgradedImageIExtractor
from goose.videos.extractors import VideoExtractor
from goose.network import HtmlFetcher


class CrawlCandidate(object):

    def __init__(self, config, url, raw_html):
        self.config = config
        # parser
        self.parser = self.config.get_parser()
        self.url = url
        self.raw_html = raw_html


class Crawler(object):

    def __init__(self, config):
        # config
        self.config = config
        # parser
        self.parser = self.config.get_parser()

        # article
        self.article = Article()

        # init the extractor
        self.extractor = self.get_extractor()

        # init the document cleaner
        self.cleaner = self.get_cleaner()

        # init the output formatter
        self.formatter = self.get_formatter()

        # video extractor
        self.video_extractor = self.get_video_extractor()

        # image extrator
        self.image_extractor = self.get_image_extractor()

        # TODO : log prefix
        self.logPrefix = "crawler:"

    def crawl(self, crawl_candidate):

        # parser candidate
        parse_candidate = self.get_parse_candidate(crawl_candidate)

        # raw html
        raw_html = self.get_html(crawl_candidate, parse_candidate)

        if raw_html is None:
            return self.article

        # create document
        doc = self.get_document(raw_html)

        # article
        self.article.final_url = parse_candidate.url
        self.article.link_hash = parse_candidate.link_hash
        self.article.raw_html = raw_html
        self.article.doc = doc
        self.article.raw_doc = deepcopy(doc)
        # TODO
        # self.article.publish_date = config.publishDateExtractor.extract(doc)
        # self.article.additional_data = config.get_additionaldata_extractor.extract(doc)
        self.article.title = self.extractor.get_title()
        self.article.meta_lang = self.extractor.get_meta_lang()
        self.article.meta_favicon = self.extractor.get_favicon()
        self.article.meta_description = self.extractor.get_meta_description()
        self.article.meta_keywords = self.extractor.get_meta_keywords()
        self.article.canonical_link = self.extractor.get_canonical_link()
        self.article.domain = self.extractor.get_domain()
        self.article.tags = self.extractor.extract_tags()

        # before we do any calcs on the body itself let's clean up the document
        self.article.doc = self.cleaner.clean()

        # big stuff
        self.article.top_node = self.extractor.calculate_best_node()

        # if we have a top node
        # let's process it
        if self.article.top_node is not None:

            # video handeling
            self.video_extractor.get_videos()

            # image handeling
            if self.config.enable_image_fetching:
                self.get_image()

            # post cleanup
            self.article.top_node = self.extractor.post_cleanup()

            # clean_text
            self.article.cleaned_text = self.formatter.get_formatted_text()

        # cleanup tmp file
        self.relase_resources()

        # return the article
        return self.article

    def get_parse_candidate(self, crawl_candidate):
        if crawl_candidate.raw_html:
            return RawHelper.get_parsing_candidate(crawl_candidate.url, crawl_candidate.raw_html)
        return URLHelper.get_parsing_candidate(crawl_candidate.url)

    def get_image(self):
        doc = self.article.raw_doc
        top_node = self.article.top_node
        self.article.top_image = self.image_extractor.get_best_image(doc, top_node)

    def get_html(self, crawl_candidate, parsing_candidate):
        # we got a raw_tml
        # no need to fetch remote content
        if crawl_candidate.raw_html:
            return crawl_candidate.raw_html

        # fetch HTML
        fetcher = HtmlFetcher(self.config, parsing_candidate.url)
        html = fetcher.get_html()
        #html = HtmlFetcher().get_html(self.config, parsing_candidate.url)
        return html

    def get_image_extractor(self):
        return UpgradedImageIExtractor(self.config, self.article)

    def get_video_extractor(self):
        return VideoExtractor(self.config, self.article)

    def get_formatter(self):
        return StandardOutputFormatter(self.config, self.article)

    def get_cleaner(self):
        return StandardDocumentCleaner(self.config, self.article)

    def get_document(self, raw_html):
        doc = self.parser.fromstring(raw_html)
        return doc

    def get_extractor(self):
        return StandardContentExtractor(self.config, self.article)

    def relase_resources(self):
        path = os.path.join(self.config.local_storage_path, '%s_*' % self.article.link_hash)
        for fname in glob.glob(path):
            try:
                os.remove(fname)
            except OSError:
                # TODO better log handeling
                pass
