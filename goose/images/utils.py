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
from goose.images.image import ImageDetails
from goose.images.image import LocallyStoredImage


class ImageUtils(object):

    @classmethod
    def getImageDimensions(self, identifyProgram, filePath):
        image = Image.open(filePath)
        imageDetails = ImageDetails()
        imageDetails.set_mime_type(image.format)
        width, height = image.size
        imageDetails.set_width(width)
        imageDetails.set_height(height)
        return imageDetails

    @classmethod
    def storeImageToLocalFile(self, httpClient, link_hash, src, config):
        """\
        Writes an image src http string to disk as a temporary file
        and returns the LocallyStoredImage object
        that has the info you should need on the image
        """
        # check for a cache hit already on disk
        image = self.readExistingFileInfo(link_hash, src, config)
        if image:
            return image

        # no cache found download the image
        data = self.fetchEntity(httpClient, src)
        if data:
            image = self.writeEntityContentsToDisk(data, link_hash, src, config)
            if image:
                return image

        return None

    @classmethod
    def getFileExtensionName(self, imageDetails):
        mime_type = imageDetails.get_mime_type().lower()
        mimes = {
            'png': '.png',
            'jpg': '.jpg',
            'jpeg': '.jpg',
            'gif': '.gif',
        }
        return mimes.get(mime_type, 'NA')

    @classmethod
    def readExistingFileInfo(self, link_hash, src, config):
        localImageName = self.getLocalFileName(link_hash, src, config)
        if os.path.isfile(localImageName):
            identify = config.imagemagick_identify_path
            imageDetails = self.getImageDimensions(identify, localImageName)
            file_extension = self.getFileExtensionName(imageDetails)
            bytes = os.path.getsize(localImageName)
            return LocallyStoredImage(
                src=src,
                local_filename=localImageName,
                link_hash=link_hash,
                bytes=bytes,
                file_extension=file_extension,
                height=imageDetails.get_height(),
                width=imageDetails.get_width()
            )
        return None

    @classmethod
    def writeEntityContentsToDisk(self, entity, link_hash, src, config):
        localSrcPath = self.getLocalFileName(link_hash, src, config)
        f = open(localSrcPath, 'w')
        f.write(entity)
        f.close()
        return self.readExistingFileInfo(link_hash, src, config)

    @classmethod
    def getLocalFileName(self, link_hash, src, config):
        imageHash = hashlib.md5(smart_str(src)).hexdigest()
        return config.local_storage_path + "/" + link_hash + "_py_" + imageHash

    @classmethod
    def cleanImageSrcString(self, src):
        return src.replace(" ", "%20")

    @classmethod
    def fetchEntity(self, httpClient, src):
        try:
            req = urllib2.Request(src)
            f = urllib2.urlopen(req)
            data = f.read()
            return data
        except:
            return None
