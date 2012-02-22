


class LocallyStoredImage(object):
    
    def __init__(self, imgSrc='', localFileName='', 
        linkhash='', bytes=long(0), fileExtension='', height=0, width=0):
        self.imgSrc = imgSrc
        self.localFileName = localFileName
        self.linkhash = linkhash
        self.bytes = bytes
        self.fileExtension = fileExtension
        self.height = height
        self.width = width