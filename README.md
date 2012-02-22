#Python-Goose - Article Extractor

##Intro


Goose was originally an article extractor written in Java that has most recently (aug2011) converted to a scala project by Gravity.com

This is a complete rewrite in python. The aim of the software is is to take any news article or article type web page and not only extract what is the main body of the article but also all meta data and most probable image candidate.

Goose will try to extract the following information:

 - Main text of an article
 - Main image of article
 - Any Youtube/Vimeo movies embedded in article (TODO)
 - Meta Description
 - Meta tags


Originally, Goose was open sourced by Gravity.com in 2011

 - Lead Programmer: Jim Plush (Gravity.com)
 - Contributers: Robbie Coleman (Gravity.com)

The python version was rewrite by:

 - Xavier Grangier (Recrutae.com)

##Licensing
If you find Goose useful or have issues please drop me a line, I'd love to hear how you're using it or what features should be improved

Goose is licensed by Gravity.com under the Apache 2.0 license, see the LICENSE file for more details

##Setup
    mkvirtualenv --no-site-packages goose
    git clone https://github.com/xgdlm/python-goose.git
    cd python-goose
    pip install -r requirements.txt
    python setup.py install
    
    
    

##Take it for a spin
    >>> from goose.Goose import Goose
    >>> url = 'http://edition.cnn.com/2012/02/22/world/europe/uk-occupy-london/index.html?hpt=ieu_c2'
    >>> g = Goose()
    >>> article = g.extractContent(url=url)
    >>> print article.cleanedArticleText[:150]
    (CNN) -- Occupy London protesters who have been camped outside the landmark St. Paul's Cathedral for the past four months lost their court bid to avoi
    >>> print article.topImage.imageSrc
    http://i2.cdn.turner.com/cnn/dam/assets/111017024308-occupy-london-st-paul-s-cathedral-story-top.jpg


##TODO
  - Camel Case method and variables : We have used camelcase code to reflect the orginal scala code.
  - Move modules around.
    This should be changed to a more pythonic naming.
  - Video extraction
  - Ability to use localized stopwords
  - Fetch faveicon 

##Known issues
  - There is some issue with unicode URLs.