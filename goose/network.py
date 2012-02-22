# -*- coding: utf-8 -*-
import urllib2


class HtmlFetcher(object):
    
    def __init__(self):
        pass
    
    
    def getHttpClient(self):
        pass
        
    
    
    def getHtml(self, config, url):
        """\
        
        """
        if isinstance(url, unicode):
            url = url.encode('utf-8')
        headers = {}# 'User-Agent' : config.browserUserAgent }
        request = urllib2.Request(url, None, headers)
        opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=1))
        opener.addheaders = [('User-agent', config.browserUserAgent)]
        try:
            htmlResult = opener.open(request).read()
        except:
            return None
        # urllib2.HTTPError
        # ValueError
        return htmlResult

