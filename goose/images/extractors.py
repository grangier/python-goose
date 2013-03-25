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
from goose.images.ImageUtils import ImageUtils

KNOWN_IMG_DOM_NAMES = [
    "yn-story-related-media",
    "cnn_strylccimg300cntr",
    "big_photo",
    "ap-smallphoto-a",
]




class DepthTraversal(object):

    def __init__(self, node, parentDepth, siblingDepth):
        self.node = node
        self.parentDepth = parentDepth
        self.siblingDepth = siblingDepth


class ImageExtractor(object):
    pass


class UpgradedImageIExtractor(ImageExtractor):

    def __init__(self, httpClient, article, config):
        self.customSiteMapping = {}
        self.loadCustomSiteMapping()

        # article
        self.article = article

        # config
        self.config = config

        # What's the minimum bytes for an image we'd accept is
        self.minBytesForImages = 4000

        # the webpage url that we're extracting content from
        self.targetUrl = article.finalUrl

        # stores a hash of our url for
        # reference and image processing
        self.linkhash = article.linkhash

        # this lists all the known bad button names that we have
        self.matchBadImageNames = re.compile(
            ".html|.gif|.ico|button|twitter.jpg|facebook.jpg|ap_buy_photo"
            "|digg.jpg|digg.png|delicious.png|facebook.png|reddit.jpg"
            "|doubleclick|diggthis|diggThis|adserver|/ads/|ec.atdmt.com"
            "|mediaplex.com|adsatt|view.atdmt"
        )

    def getBestImage(self, doc, topNode):
        image = self.checkForKnownElements()
        if image:
            return image

        image = self.checkForLargeImages(topNode, 0, 0)
        if image:
            return image

        image = self.checkForMetaTag()
        if image:
            return image
        return Image()

    def checkForMetaTag(self):
        image = self.checkForLinkTag()
        if image:
            return image
        image = self.checkForOpenGraphTag()
        if image:
            return image

    def checkForLargeImages(self, node, parentDepthLevel, siblingDepthLevel):
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
        goodImages = self.getImageCandidates(node)

        if goodImages:
            scoredImages = self.downloadImagesAndGetResults(goodImages, parentDepthLevel)
            if scoredImages:
                highScoreImage = sorted(scoredImages.items(),
                                        key=lambda x: x[1], reverse=True)[0][0]
                mainImage = Image()
                mainImage.imageSrc = highScoreImage.imgSrc
                mainImage.imageExtractionType = "bigimage"
                mainImage.confidenceScore = 100 / len(scoredImages) \
                                    if len(scoredImages) > 0 else 0
                return mainImage

        depthObj = self.getDepthLevel(node, parentDepthLevel, siblingDepthLevel)
        if depthObj:
            return self.checkForLargeImages(depthObj.node,
                            depthObj.parentDepth, depthObj.siblingDepth)

        return None

    def getDepthLevel(self, node, parentDepth, siblingDepth):
        MAX_PARENT_DEPTH = 2
        if parentDepth > MAX_PARENT_DEPTH:
            return None
        else:
            siblingNode = Parser.previousSibling(node)
            if siblingNode is not None:
                return DepthTraversal(siblingNode, parentDepth, siblingDepth + 1)
            elif node is not None:
                parent = Parser.getParent(node)
                if parent is not None:
                    return DepthTraversal(parent, parentDepth + 1, 0)
        return None

    def downloadImagesAndGetResults(self, images, depthLevel):
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
            imgSrc = Parser.getAttribute(image, attr='src')
            imgSrc = self.buildImagePath(imgSrc)
            locallyStoredImage = self.getLocallyStoredImage(imgSrc)
            width = locallyStoredImage.width
            height = locallyStoredImage.height
            imageSrc = locallyStoredImage.imgSrc
            fileExtension = locallyStoredImage.fileExtension

            if fileExtension != '.gif' or fileExtension != 'NA':
                if (depthLevel >= 1 and locallyStoredImage.width > 300) or depthLevel < 1:
                    if not self.isBannerDimensions(width, height):
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

    def getAllImages(self):
        return None

    def isBannerDimensions(self, width, height):
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

    def getImagesFromNode(self, node):
        images = Parser.getElementsByTag(node, tag='img')
        if images is not None and len(images) < 1:
            return None
        return images

    def filterBadNames(self, images):
        """\
        takes a list of image elements
        and filters out the ones with bad names
        """
        goodImages = []
        for image in images:
            if self.isOkImageFileName(image):
                goodImages.append(image)
        return goodImages if len(goodImages) > 0 else None

    def isOkImageFileName(self, imageNode):
        """\
        will check the image src against a list
        of bad image files we know of like buttons, etc...
        """
        imgSrc = Parser.getAttribute(imageNode, attr='src')

        if not imgSrc:
            return False

        if self.matchBadImageNames.search(imgSrc):
            return False

        return True

    def getImageCandidates(self, node):
        goodImages = []
        filteredImages = []
        images = self.getImagesFromNode(node)
        if images:
            filteredImages = self.filterBadNames(images)
        if filteredImages:
            goodImages = self.findImagesThatPassByteSizeTest(filteredImages)
        return goodImages

    def findImagesThatPassByteSizeTest(self, images):
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
            imgSrc = Parser.getAttribute(image, attr='src')
            imgSrc = self.buildImagePath(imgSrc)
            locallyStoredImage = self.getLocallyStoredImage(imgSrc)
            if locallyStoredImage:
                bytes = locallyStoredImage.bytes
                if (bytes == 0 or bytes > self.minBytesForImages) \
                        and bytes < MAX_BYTES_SIZE:
                    goodImages.append(image)
                else:
                    images.remove(image)
            cnt += 1
        return goodImages if len(goodImages) > 0 else None

    def getNode(self, node):
        return node if node else None

    def checkForLinkTag(self):
        """\
        checks to see if we were able to
        find open link_src on this page
        """
        node = self.article.rawDoc
        meta = Parser.getElementsByTag(node, tag='link', attr='rel', value='image_src')
        for item in meta:
            href = Parser.getAttribute(item, attr='href')
            if href:
                mainImage = Image()
                mainImage.imageSrc = href
                mainImage.imageExtractionType = "linktag"
                mainImage.confidenceScore = 100
                locallyStoredImage = self.getLocallyStoredImage(mainImage.imageSrc)
                if locallyStoredImage:
                    mainImage.bytes = locallyStoredImage.bytes
                    mainImage.height = locallyStoredImage.height
                    mainImage.width = locallyStoredImage.width
                    return mainImage
        return None

    def checkForOpenGraphTag(self):
        """\
        checks to see if we were able to
        find open graph tags on this page
        """
        node = self.article.rawDoc
        meta = Parser.getElementsByTag(node, tag='meta', attr='property', value='og:image')
        for item in meta:
            href = Parser.getAttribute(item, attr='content')
            if href:
                mainImage = Image()
                mainImage.imageSrc = href
                mainImage.imageExtractionType = "opengraph"
                mainImage.confidenceScore = 100
                locallyStoredImage = self.getLocallyStoredImage(mainImage.imageSrc)
                if locallyStoredImage:
                    mainImage.bytes = locallyStoredImage.bytes
                    mainImage.height = locallyStoredImage.height
                    mainImage.width = locallyStoredImage.width
                    return mainImage
        return None

    def getLocallyStoredImage(self, imageSrc):
        """\
        returns the bytes of the image file on disk
        """
        locallyStoredImage = ImageUtils.storeImageToLocalFile(None,
                                    self.linkhash, imageSrc, self.config)
        return locallyStoredImage

    def getCleanDomain(self):
        return self.article.domain.replace('www.', '')

    def checkForKnownElements(self):
        """\
        in here we check for known image contains from sites
        we've checked out like yahoo, techcrunch, etc... that have
        * known  places to look for good images.
        * TODO: enable this to use a series of settings files
          so people can define what the image ids/classes
          are on specific sites
        """
        domain = self.getCleanDomain()
        if domain in self.customSiteMapping.keys():
            classes = self.customSiteMapping.get(domain).split('|')
            for classname in classes:
                KNOWN_IMG_DOM_NAMES.append(classname)

        knownImage = None

        for knownName in KNOWN_IMG_DOM_NAMES:
            known = Parser.getElementById(self.article.rawDoc, knownName)
            if not known:
                known = Parser.getElementsByTag(self.article.rawDoc,
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
            mainImage.imageSrc = self.buildImagePath(knownImgSrc)
            mainImage.imageExtractionType = "known"
            mainImage.confidenceScore = 90
            locallyStoredImage = self.getLocallyStoredImage(mainImage.imageSrc)
            if locallyStoredImage:
                mainImage.bytes = locallyStoredImage.bytes
                mainImage.height = locallyStoredImage.height
                mainImage.width = locallyStoredImage.width

            return mainImage

    def buildImagePath(self, imageSrc):
        """\
        This method will take an image path and build
        out the absolute path to that image
        * using the initial url we crawled
          so we can find a link to the image
          if they use relative urls like ../myimage.jpg
        """
        o = urlparse(imageSrc)
        # we have a full url
        if o.hostname:
            return o.geturl()
        # we have a relative url
        return urljoin(self.targetUrl, imageSrc)

    def loadCustomSiteMapping(self):
        # TODO
        path = os.path.join('images', 'known-image-css.txt')
        dataFile = FileHelper.loadResourceFile(path)
        lines = dataFile.splitlines()
        for line in lines:
            domain, css = line.split('^')
            self.customSiteMapping.update({domain: css})
