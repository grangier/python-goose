# -*- coding: utf-8 -*-

class Image(object):
    
    def __init__(self):
        # holds the Element node of the image we think is top dog
        self.topImageNode = None
        
        # holds the src of the image
        self.imageSrc = ""
        
        # how confident are we in this image extraction? 
        # the most images generally the less confident
        self.confidenceScore = float(0.0)
        
        # Height of the image in pixels
        self.height = 0
        
        # width of the image in pixels
        self.width = 0
        
        # what kind of image extraction was used for this? 
        # bestGuess, linkTag, openGraph tags?
        self.imageExtractionType = "NA"
        
        # stores how many bytes this image is.
        self.bytes = long(0)
    
    
    def getImageSrc(self):
        return self.imageSrc
    
    


        