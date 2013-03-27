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
import os
from urlparse import urlparse, urljoin
from goose.utils import FileHelper
from goose.parsers import Parser
from goose.images.image import Image
from goose.images.utils import ImageUtils

KNOWN_IMG_DOM_NAMES = [
    "yn-story-related-media",
    "cnn_strylccimg300cntr",
    "big_photo",
    "ap-smallphoto-a",
]


class DepthTraversal(object):

    def __init__(self, node, parent_depth, sibling_depth):
        self.node = node
        self.parent_depth = parent_depth
        self.sibling_depth = sibling_depth


class ImageExtractor(object):
    pass


class UpgradedImageIExtractor(ImageExtractor):

    def __init__(self, http_client, article, config):
        self.custom_site_mapping = {}
        self.load_customesite_mapping()

        # article
        self.article = article

        # config
        self.config = config

        # What's the minimum bytes for an image we'd accept is
        self.images_min_bytes = 4000

        # the webpage url that we're extracting content from
        self.targetUrl = article.final_url

        # stores a hash of our url for
        # reference and image processing
        self.link_hash = article.link_hash

        # this lists all the known bad button names that we have
        self.matchBadImageNames = re.compile(
            ".html|.gif|.ico|button|twitter.jpg|facebook.jpg|ap_buy_photo"
            "|digg.jpg|digg.png|delicious.png|facebook.png|reddit.jpg"
            "|doubleclick|diggthis|diggThis|adserver|/ads/|ec.atdmt.com"
            "|mediaplex.com|adsatt|view.atdmt"
        )

    def get_best_image(self, doc, topNode):
        image = self.check_known_elements()
        if image:
            return image

        image = self.check_large_images(topNode, 0, 0)
        if image:
            return image

        image = self.check_meta_tag()
        if image:
            return image
        return Image()

    def check_meta_tag(self):
        image = self.check_link_tag()
        if image:
            return image
        image = self.check_opengraph_tag()
        if image:
            return image

    def check_large_images(self, node, parent_depthLevel, sibling_depthLevel):
        """\
        although slow the best way to determine the best image is to download
        them and check the actual dimensions of the image when on disk
        so we'll go through a phased approach...
        1. get a list of ALL images from the parent node
        2. filter out any bad image names that we know of (gifs, ads, etc..)
        3. do a head request on each file to make sure it meets
           our bare requirements
        4. any images left over let's do a full GET request,
           download em to disk and check their dimensions
        5. Score images based on different factors like height/width
           and possibly things like color density
        """
        goodImages = self.get_image_candidates(node)

        if goodImages:
            scoredImages = self.fetch_images(goodImages, parent_depthLevel)
            if scoredImages:
                highScoreImage = sorted(scoredImages.items(),
                                        key=lambda x: x[1], reverse=True)[0][0]
                mainImage = Image()
                mainImage.src = highScoreImage.src
                mainImage.extraction_type = "bigimage"
                mainImage.confidence_score = 100 / len(scoredImages) \
                                    if len(scoredImages) > 0 else 0
                return mainImage

        depthObj = self.get_depth_level(node, parent_depthLevel, sibling_depthLevel)
        if depthObj:
            return self.check_large_images(depthObj.node,
                            depthObj.parent_depth, depthObj.sibling_depth)

        return None

    def get_depth_level(self, node, parent_depth, sibling_depth):
        MAX_PARENT_DEPTH = 2
        if parent_depth > MAX_PARENT_DEPTH:
            return None
        else:
            siblingNode = Parser.previousSibling(node)
            if siblingNode is not None:
                return DepthTraversal(siblingNode, parent_depth, sibling_depth + 1)
            elif node is not None:
                parent = Parser.getParent(node)
                if parent is not None:
                    return DepthTraversal(parent, parent_depth + 1, 0)
        return None

    def fetch_images(self, images, depthLevel):
        """\
        download the images to temp disk and set their dimensions
        - we're going to score the images in the order in which
          they appear so images higher up will have more importance,
        - we'll count the area of the 1st image as a score
          of 1 and then calculate how much larger or small each image after it is
        - we'll also make sure to try and weed out banner
          type ad blocks that have big widths and small heights or vice versa
        - so if the image is 3rd found in the dom it's
          sequence score would be 1 / 3 = .33 * diff
          in area from the first image
        """
        imageResults = {}
        initialArea = float(0.0)
        totalScore = float(0.0)
        cnt = float(1.0)
        MIN_WIDTH = 50
        for image in images[:30]:
            src = Parser.getAttribute(image, attr='src')
            src = self.build_image_path(src)
            locallyStoredImage = self.get_local_image(src)
            width = locallyStoredImage.width
            height = locallyStoredImage.height
            src = locallyStoredImage.src
            file_extension = locallyStoredImage.file_extension

            if file_extension != '.gif' or file_extension != 'NA':
                if (depthLevel >= 1 and locallyStoredImage.width > 300) or depthLevel < 1:
                    if not self.is_banner_dimensions(width, height):
                        if width > MIN_WIDTH:
                            sequenceScore = float(1.0 / cnt)
                            area = float(width * height)
                            totalScore = float(0.0)

                            if initialArea == 0:
                                initialArea = area * float(1.48)
                                totalScore = 1
                            else:
                                areaDifference = float(area / initialArea)
                                totalScore = sequenceScore * areaDifference

                            imageResults.update({locallyStoredImage: totalScore})
                            cnt += 1
                            cnt += 1
        return imageResults

    def get_images(self):
        return None

    def is_banner_dimensions(self, width, height):
        """\
        returns true if we think this is kind of a bannery dimension
        like 600 / 100 = 6 may be a fishy dimension for a good image
        """
        if width == height:
            return False

        if width > height:
            diff = float(width / height)
            if diff > 5:
                return True

        if height > width:
            diff = float(height / width)
            if diff > 5:
                return True

        return False

    def get_node_images(self, node):
        images = Parser.getElementsByTag(node, tag='img')
        if images is not None and len(images) < 1:
            return None
        return images

    def filter_bad_names(self, images):
        """\
        takes a list of image elements
        and filters out the ones with bad names
        """
        goodImages = []
        for image in images:
            if self.is_valid_filename(image):
                goodImages.append(image)
        return goodImages if len(goodImages) > 0 else None

    def is_valid_filename(self, imageNode):
        """\
        will check the image src against a list
        of bad image files we know of like buttons, etc...
        """
        src = Parser.getAttribute(imageNode, attr='src')

        if not src:
            return False

        if self.matchBadImageNames.search(src):
            return False

        return True

    def get_image_candidates(self, node):
        goodImages = []
        filteredImages = []
        images = self.get_node_images(node)
        if images:
            filteredImages = self.filter_bad_names(images)
        if filteredImages:
            goodImages = self.get_images_bytesize_match(filteredImages)
        return goodImages

    def get_images_bytesize_match(self, images):
        """\
        loop through all the images and find the ones
        that have the best bytez to even make them a candidate
        """
        cnt = 0
        MAX_BYTES_SIZE = 15728640
        goodImages = []
        for image in images:
            if cnt > 30:
                return goodImages
            src = Parser.getAttribute(image, attr='src')
            src = self.build_image_path(src)
            locallyStoredImage = self.get_local_image(src)
            if locallyStoredImage:
                bytes = locallyStoredImage.bytes
                if (bytes == 0 or bytes > self.images_min_bytes) \
                        and bytes < MAX_BYTES_SIZE:
                    goodImages.append(image)
                else:
                    images.remove(image)
            cnt += 1
        return goodImages if len(goodImages) > 0 else None

    def get_node(self, node):
        return node if node else None

    def check_link_tag(self):
        """\
        checks to see if we were able to
        find open link_src on this page
        """
        node = self.article.raw_doc
        meta = Parser.getElementsByTag(node, tag='link', attr='rel', value='image_src')
        for item in meta:
            href = Parser.getAttribute(item, attr='href')
            if href:
                mainImage = Image()
                mainImage.src = href
                mainImage.extraction_type = "linktag"
                mainImage.confidence_score = 100
                locallyStoredImage = self.get_local_image(mainImage.src)
                if locallyStoredImage:
                    mainImage.bytes = locallyStoredImage.bytes
                    mainImage.height = locallyStoredImage.height
                    mainImage.width = locallyStoredImage.width
                    return mainImage
        return None

    def check_opengraph_tag(self):
        """\
        checks to see if we were able to
        find open graph tags on this page
        """
        node = self.article.raw_doc
        meta = Parser.getElementsByTag(node, tag='meta', attr='property', value='og:image')
        for item in meta:
            href = Parser.getAttribute(item, attr='content')
            if href:
                mainImage = Image()
                mainImage.src = href
                mainImage.extraction_type = "opengraph"
                mainImage.confidence_score = 100
                locallyStoredImage = self.get_local_image(mainImage.src)
                if locallyStoredImage:
                    mainImage.bytes = locallyStoredImage.bytes
                    mainImage.height = locallyStoredImage.height
                    mainImage.width = locallyStoredImage.width
                    return mainImage
        return None

    def get_local_image(self, src):
        """\
        returns the bytes of the image file on disk
        """
        locallyStoredImage = ImageUtils.store_image(None,
                                    self.link_hash, src, self.config)
        return locallyStoredImage

    def get_clean_domain(self):
        return self.article.domain.replace('www.', '')

    def check_known_elements(self):
        """\
        in here we check for known image contains from sites
        we've checked out like yahoo, techcrunch, etc... that have
        * known  places to look for good images.
        * TODO: enable this to use a series of settings files
          so people can define what the image ids/classes
          are on specific sites
        """
        domain = self.get_clean_domain()
        if domain in self.custom_site_mapping.keys():
            classes = self.custom_site_mapping.get(domain).split('|')
            for classname in classes:
                KNOWN_IMG_DOM_NAMES.append(classname)

        knownImage = None

        for knownName in KNOWN_IMG_DOM_NAMES:
            known = Parser.getElementById(self.article.raw_doc, knownName)
            if not known:
                known = Parser.getElementsByTag(self.article.raw_doc,
                                                attr='class', value=knownName)
                if known:
                    known = known[0]
            if known:
                mainImage = Parser.getElementsByTag(known, tag='img')
                if mainImage:
                    knownImage = mainImage[0]

        if knownImage is not None:
            knownImgSrc = Parser.getAttribute(knownImage, attr='src')
            mainImage = Image()
            mainImage.src = self.build_image_path(knownImgSrc)
            mainImage.extraction_type = "known"
            mainImage.confidence_score = 90
            locallyStoredImage = self.get_local_image(mainImage.src)
            if locallyStoredImage:
                mainImage.bytes = locallyStoredImage.bytes
                mainImage.height = locallyStoredImage.height
                mainImage.width = locallyStoredImage.width

            return mainImage

    def build_image_path(self, src):
        """\
        This method will take an image path and build
        out the absolute path to that image
        * using the initial url we crawled
          so we can find a link to the image
          if they use relative urls like ../myimage.jpg
        """
        o = urlparse(src)
        # we have a full url
        if o.hostname:
            return o.geturl()
        # we have a relative url
        return urljoin(self.targetUrl, src)

    def load_customesite_mapping(self):
        # TODO
        path = os.path.join('images', 'known-image-css.txt')
        dataFile = FileHelper.loadResourceFile(path)
        lines = dataFile.splitlines()
        for line in lines:
            domain, css = line.split('^')
            self.custom_site_mapping.update({domain: css})
