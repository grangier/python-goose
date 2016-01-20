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
import six
import requests


class NetworkFetcher(object):

    def __init__(self, config):
        self.config = config
        self._connection = requests.Session()
        self._connection.headers = {'User-agent': self.config.browser_user_agent}

        self._url = None

    def get_url(self):
        return self._url

    def fetch(self, url):
        # utf-8 encode unicode url
        if isinstance(url, six.text_type) and six.PY2:
            url = url.encode('utf-8')

        response = self._connection.get(url)
        if response.ok:
            self._url = response.url
            text = response.content
        else:
            self._url = None
            text = None

        return text
