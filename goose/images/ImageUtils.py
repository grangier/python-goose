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
import hashlib
import os
import urllib2
from PIL import Image
from goose.utils.encoding import smart_str
from goose.images.ImageDetails import ImageDetails
from goose.images.ImageExtractor import LocallyStoredImage


class ImageUtils(object):

    @classmethod
    def getImageDimensions(self, identifyProgram, filePath):
        image = Image.open(filePath)
        imageDetails = ImageDetails()
        imageDetails.setMimeType(image.format)
        width, height = image.size
        imageDetails.setWidth(width)
        imageDetails.setHeight(height)
        return imageDetails

    @classmethod
    def storeImageToLocalFile(self, httpClient, linkhash, imageSrc, config):
        """\
        Writes an image src http string to disk as a temporary file
        and returns the LocallyStoredImage object
        that has the info you should need on the image
        """
        # check for a cache hit already on disk
        image = self.readExistingFileInfo(linkhash, imageSrc, config)
        if image:
            return image

        # no cache found download the image
        data = self.fetchEntity(httpClient, imageSrc)
        if data:
            image = self.writeEntityContentsToDisk(data, linkhash, imageSrc, config)
            if image:
                return image

        return None

    @classmethod
    def getFileExtensionName(self, imageDetails):
        mimeType = imageDetails.getMimeType().lower()
        mimes = {
            'png': '.png',
            'jpg': '.jpg',
            'jpeg': '.jpg',
            'gif': '.gif',
        }
        return mimes.get(mimeType, 'NA')

    @classmethod
    def readExistingFileInfo(self, linkhash, imageSrc, config):
        localImageName = self.getLocalFileName(linkhash, imageSrc, config)
        if os.path.isfile(localImageName):
            identify = config.imagemagickIdentifyPath
            imageDetails = self.getImageDimensions(identify, localImageName)
            fileExtension = self.getFileExtensionName(imageDetails)
            bytes = os.path.getsize(localImageName)
            return LocallyStoredImage(
                imgSrc=imageSrc,
                localFileName=localImageName,
                linkhash=linkhash,
                bytes=bytes,
                fileExtension=fileExtension,
                height=imageDetails.getHeight(),
                width=imageDetails.getWidth()
            )
        return None

    @classmethod
    def writeEntityContentsToDisk(self, entity, linkhash, imageSrc, config):
        localSrcPath = self.getLocalFileName(linkhash, imageSrc, config)
        f = open(localSrcPath, 'w')
        f.write(entity)
        f.close()
        return self.readExistingFileInfo(linkhash, imageSrc, config)

    @classmethod
    def getLocalFileName(self, linkhash, imageSrc, config):
        imageHash = hashlib.md5(smart_str(imageSrc)).hexdigest()
        return config.localStoragePath + "/" + linkhash + "_py_" + imageHash

    @classmethod
    def cleanImageSrcString(self, imgSrc):
        return imgSrc.replace(" ", "%20")

    @classmethod
    def fetchEntity(self, httpClient, imageSrc):
        try:
            req = urllib2.Request(imageSrc)
            f = urllib2.urlopen(req)
            data = f.read()
            return data
        except:
            return None
