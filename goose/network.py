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
import urllib2


class HtmlFetcher(object):

    def __init__(self, config):
        # set header
        self.headers = {'User-agent': config.browser_user_agent}

    def get_url(self):
        # if we have a result
        # get the final_url
        if self.result is not None:
            return self.result.geturl()
        return None

    def get_html(self, url):
        # utf-8 encode unicode url
        if isinstance(url, unicode):
            url = url.encode('utf-8')

        # set request
        self.request = urllib2.Request(url, headers=self.headers)

        # do request
        try:
            self.result = urllib2.urlopen(self.request)
        except:
            self.result = None

        # read the result content
        if self.result is not None:
            return self.result.read()
        return None
