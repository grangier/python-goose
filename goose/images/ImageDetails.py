

class ImageDetails(object):
    
    def __init__(self):
        
        # the width of the image
        self.width = 0
        
        # height of the image
        self.height = 0
        
        # the mimeType of the image JPEG / PNG
        self.mimeType = None
    
    
    def getWidth(self):
        return self.width
    
    
    def setWidth(self, width):
        self.width = width
    
    
    def getHeight(self):
        return self.height
    
    
    def setHeight(self, height):
        self.height = height
    
    
    def getMimeType(self):
        return self.mimeType
    
    
    def setMimeType(self, mimeType):
        self.mimeType = mimeType
    



        