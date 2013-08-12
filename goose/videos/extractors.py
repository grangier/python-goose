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

from goose.videos.videos import Video

VIDEOS_TAGS = ['iframe', 'embed', 'object']
VIDEO_PROVIDERS = ['youtube', 'vimeo', 'dailymotion', 'kewego']


class VideoExtractor(object):
    """\
    Extracts a list of video from Article top node
    """
    def __init__(self, article, config):
        # article
        self.article = article

        # config
        self.config = config

        # parser
        self.parser = self.config.get_parser()

    def get_video(self, node, provider):
        """
        Create a video object from a video embed
        """
        video = Video()
        video.provider = provider
        video.embed_code = self.parser.nodeToString(node)
        video.embed_type = self.parser.getTag(node)
        video.width = self.parser.getAttribute(node, 'width')
        video.height = self.parser.getAttribute(node, 'height')
        video.src = self.parser.getAttribute(node, 'src')
        return video


    def get_videos(self):
        # movies
        movies = []

        # candidates node
        candidates = self.parser.getElementsByTags(self.article.top_node, VIDEOS_TAGS)
        
        # loop all candidates 
        # and check if src attribute belongs to a video provider
        for candidate in candidates:
            src = self.parser.getAttribute(candidate, 'src')
            if src:
                for provider in VIDEO_PROVIDERS:
                    if provider in src:
                        movies.append(self.get_video(candidate, provider))
        self.article.movies = movies

        

