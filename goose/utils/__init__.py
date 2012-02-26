# -*- coding: utf-8 -*-
import hashlib
import re
import os
import goose
import codecs
import urlparse


class BuildURL(object):
    def __init__(self, url, finalurl=None):
        self.url = url
        self.finalurl = finalurl
    
    
    def getHostname(self, o):
        if o.hostname:
            return o.hotname
        elif self.finalurl:
            oo = urlparse(self.finalurl)
            if oo.hostname:
                return oo.hostname
        return None
    
    
    def getScheme(self, o):
        if o.scheme:
            return o.scheme
        elif self.finalurl:
            oo = urlparse(self.finalurl)
            if oo.scheme:
                return oo.scheme
        return 'http'
        
    
    def getUrl(self):
        """\
        
        """
        url_obj = urlparse(self.url)
        scheme = self.getScheme(url_obj)
        hostname = self.getHostname(url_obj)
    


class FileHelper(object):
    
    @classmethod
    def loadResourceFile(self, filename):
        dirpath =  os.path.dirname(goose.__file__)
        path = '%s/resources/%s' % (dirpath, filename)
        try:
            f = codecs.open(path, 'r', 'utf-8')
            content = f.read()
            f.close()
            return content
        except IOError:
            raise IOError("Couldn't open file %s" % path)


class ParsingCandidate(object):
    
    def __init__(self, urlString, linkhash, url):
        self.urlString = urlString
        self.linkhash = linkhash
        self.url = url
    


class URLHelper(object):
    
    @classmethod
    def getCleanedUrl(self, urlToCrawl):
        
        # replace shebang is urls
        finalUrl = urlToCrawl.replace('#!', '?_escaped_fragment_=') \
                    if '#!' in urlToCrawl else urlToCrawl
        
        linkhash = hashlib.md5(finalUrl).hexdigest()
        
        return ParsingCandidate(finalUrl, linkhash, finalUrl)


class StringSplitter(object):
    """\
    
    """
    def __init__(self, pattern):
        self.pattern = re.compile(pattern)
        
    def split(self, string):
        if not string:
            return []
        return self.pattern.split(string)


class StringReplacement(object):
    
    def __init__(self, pattern, replaceWith):
        self.pattern = pattern
        self.replaceWith = replaceWith
        
    def replaceAll(self, string):
        if not string:
            return u''
        return string.replace(self.pattern, self.replaceWith)
        

class ReplaceSequence(object):
    
    def __init__(self):
        self.replacements = []
    
    #@classmethod    
    def create(self, firstPattern, replaceWith=None):
        result = StringReplacement(firstPattern, replaceWith or u'')
        self.replacements.append(result)
        return self
        
    def append(self, pattern, replaceWith=None):
        return self.create(pattern, replaceWith)
        
    def replaceAll(self, string):
        if not string: 
            return u''
        
        mutatedString = string
        
        for rp in self.replacements:
            mutatedString = rp.replaceAll(mutatedString)
        return mutatedString


