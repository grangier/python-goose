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
import os
import unittest
import pprint

from goose import Goose
from goose.utils import FileHelper
from goose.configuration import Configuration
from goose.text import StopWordsChinese, StopWordsArabic

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))


class TestExtractionBase(unittest.TestCase):

    def setUp(self):
        self.articleReport = ["=======================::. ARTICLE REPORT .::======================\n"]

    def get_html(self, filename):
        path = os.path.join(CURRENT_PATH, 'data', filename)
        path = os.path.abspath(path)
        return FileHelper.loadResourceFile(path)

    def getArticle(self, url, raw_html, language=None):
        config = Configuration()
        if language:
            config.target_language = language
            config.use_meta_language = False
        config.enable_image_fetching = False
        g = Goose(config=config)
        article = g.extract(url=url, raw_html=raw_html)
        return article

    def runArticleAssertions(self, article=None, expectedTitle=None,
            expectedStart=None, expectedImage=None,
            expectedDescription=None, expectedKeywords=None, expectedCanonicalLink=None):

        self.articleReport.append("URL:         ")
        self.articleReport.append(article.final_url)
        self.articleReport.append('\n')
        self.articleReport.append("TITLE:       ")
        self.articleReport.append(article.title)
        self.articleReport.append('\n')
        # self.articleReport.append("IMAGE:       ")
        # self.articleReport.append(article.top_image)
        # self.articleReport.append('\n')
        # self.articleReport.append("IMGKIND:     ")
        # self.articleReport.append(article.top_image)
        # self.articleReport.append('\n')
        self.articleReport.append("CONTENT:     ")
        self.articleReport.append(article.cleaned_text.replace("\n", "    "))
        self.articleReport.append('\n')
        self.articleReport.append("METAKW:      ")
        self.articleReport.append(article.meta_keywords)
        self.articleReport.append('\n')
        self.articleReport.append("METADESC:    ")
        self.articleReport.append(article.meta_description)
        self.articleReport.append('\n')
        self.articleReport.append("DOMAIN:      ")
        self.articleReport.append(article.domain)
        self.articleReport.append('\n')
        self.articleReport.append("LINKHASH:    ")
        self.articleReport.append(article.link_hash)
        self.articleReport.append('\n')
        # self.articleReport.append("MOVIES:      ")
        # self.articleReport.append(article.movies)
        # self.articleReport.append('\n')
        # self.articleReport.append("TAGS:        ")
        # self.articleReport.append(article.tags)
        # self.articleReport.append('\n')
        self.assertNotEqual(article, None, msg=u"Resulting article was NULL!")

        if expectedTitle:
            title = article.title
            self.assertNotEqual(title, None, msg=u"Title was NULL!")
            self.assertEqual(title, expectedTitle)

        if expectedStart:
            articleText = article.cleaned_text
            self.assertNotEqual(articleText, None,
                    msg=u"Resulting article text was NULL!")

            self.assertTrue(len(expectedStart) <= len(articleText),
                    msg=u"Article text was not as long as expected beginning!")

            actual = articleText[0:len(expectedStart)]
            try:
                msg = u"The beginning of the article text was not as expected!\nEXPECTED:%s\nGOT:%s" \
                            % (expectedStart, actual)
            except UnicodeDecodeError:
                msg = u"The beginning of the article text was not as expected!"
            self.assertEqual(expectedStart, actual, msg=msg)

        if expectedImage:
            pass

        if expectedDescription:
            description = article.meta_description
            self.assertNotEqual(description, None,
                    msg="Meta Description was NULL!")
            msg = u"Meta Description was not as expected!\nEXPECTED:%s\nGOT:%s" \
                        % (expectedDescription, description)
            self.assertEqual(expectedDescription, description, msg=msg)

        if expectedKeywords:
            pass

        if expectedCanonicalLink:
            link = article.canonical_link
            self.assertNotEqual(link, None, msg=u"Canonical Link was NULL!")
            msg = u"Canonical link was not as expected!\nEXPECTED:%s\nGOT:%s" \
                        % (expectedCanonicalLink, link)
            self.assertEqual(link, expectedCanonicalLink)

    def printReport(self):
        pprint.pprint(self.articleReport)


class TestExtractions(TestExtractionBase):

    def test_allnewlyrics1(self):
        html = self.get_html('statichtml/allnewlyrics1.txt')
        url = "http://allnewlyrics.com/only-one-lyrics-pj-morton-ft-stevie-wonder.html"
        title = "PJ Morton (Ft. Stevie Wonder)"
        content = u"PJ Morton – Only One Lyrics (Ft. Stevie Wonder)\n\nI’m pretty sure I don’t need anything else\n\n This is the best feeling I’ve ever felt"
        article = self.getArticle(url, html)
        self.runArticleAssertions(article=article, expectedTitle=title, expectedStart=content)
        self.printReport()

    def test_cnn1(self):
        html = self.get_html('statichtml/cnn1.txt')
        url = "http://www.cnn.com/2010/POLITICS/08/13/democrats.social.security/index.html"
        title = "Democrats to use Social Security against GOP this fall"
        content = "Washington (CNN) -- Democrats pledged "
        article = self.getArticle(url, html)
        self.runArticleAssertions(article=article, expectedTitle=title, expectedStart=content)
        self.printReport()

    def test_businessWeek1(self):
        html = self.get_html("statichtml/businessweek1.txt")
        url = "http://www.businessweek.com/magazine/content/10_34/b4192066630779.htm"
        title = "Olivia Munn: Queen of the Uncool"
        content = "Six years ago, Olivia Munn arrived in Hollywood with fading ambitions of making it as a sports reporter and set about deploying"
        article = self.getArticle(url, html)
        self.runArticleAssertions(article=article, expectedTitle=title, expectedStart=content)
        self.printReport()

    def test_businessWeek2(self):
        html = self.get_html("statichtml/businessweek2.txt")
        url = "http://www.businessweek.com/management/five-social-media-lessons-for-business-09202011.html"
        title = "Five Social Media Lessons for Business"
        content = "At Home Depot, we first realized we needed to have a real conversation with"
        article = self.getArticle(url, html)
        self.runArticleAssertions(article=article, expectedTitle=title, expectedStart=content)
        self.printReport()

    def test_businessWeek3(self):
        html = self.get_html("statichtml/businessweek3.txt")
        url = "http://www.businessweek.com/technology/here-comes-apples-real-tv-09132011.html"
        content = "Get ready, America, because by Christmas 2012 you will have an Apple TV in your living room"
        article = self.getArticle(url, html)
        self.runArticleAssertions(article=article, expectedStart=content)
        self.printReport()

    def test_cbslocal(self):
        html = self.get_html("statichtml/cbslocal1.txt")
        url = "http://newyork.cbslocal.com/2012/06/08/bc-morning-show-american-hero-kelly-malloy/"
        content = "Boomer & Craig were thrilled to welcome an American Hero into the Allstate Studio, as Kelly"
        article = self.getArticle(url, html)
        self.runArticleAssertions(article=article, expectedStart=content)
        self.printReport()

    def test_elmondo1(self):
        html = self.get_html("statichtml/elmondo1.txt")
        url = "http://www.elmundo.es/elmundo/2012/10/28/espana/1351388909.html"
        content = "Importante golpe a la banda terrorista ETA en Francia."
        article = self.getArticle(url, html, language='es')
        self.runArticleAssertions(article=article, expectedStart=content)
        self.printReport()

    def test_elpais(self):
        html = self.get_html("statichtml/elpais.txt")
        url = "http://www.sociedad.elpais.com/sociedad/2012/10/27/actualidad/1351332873_157836.html"
        content = "Los recortes pasan factura a los pacientes."
        article = self.getArticle(url, html)
        self.runArticleAssertions(article=article, expectedStart=content)
        self.printReport()

    def test_liberation(self):
        html = self.get_html("statichtml/liberation.txt")
        url = "http://www.liberation.fr/politiques/2012/10/27/ayrault-assume-et-revendique-sa-methode_856451"
        content = "A Toulouse, Jean-Marc Ayrault aura fait deux rappels sur"
        article = self.getArticle(url, html)
        self.runArticleAssertions(article=article, expectedStart=content)
        self.printReport()

    def test_lefigaro(self):
        html = self.get_html("statichtml/lefigaro1.txt")
        url = 'http://www.lefigaro.fr/conjoncture/2013/04/05/20002-20130405ARTFIG00473-montebourg-envisage-des-privatisations-partielles.php'
        content = u"Selon le ministre du Redressement productif interview\xe9 par le Wall Street Journal, le gouvernement"
        article = self.getArticle(url, html, language='fr')
        self.runArticleAssertions(article=article, expectedStart=content)
        self.printReport()

    ########################################
    # makes lxml crash
    # python: double free or corruption
    def test_techcrunch1(self):
        html = self.get_html("statichtml/techcrunch1.txt")
        url = "http://techcrunch.com/2011/08/13/2005-zuckerberg-didnt-want-to-take-over-the-world/"
        content = "The Huffington Post has come across this fascinating five-minute interview"
        title = u"2005 Zuckerberg Didn’t Want To Take Over The World"
        article = self.getArticle(url, html)
        self.runArticleAssertions(article=article, expectedTitle=title, expectedStart=content)
        self.printReport()

    def test_foxNews(self):
        html = self.get_html("statichtml/foxnews1.txt")
        url = "http://www.foxnews.com/politics/2010/08/14/russias-nuclear-help-iran-stirs-questions-improved-relations/"
        content = "Russia's announcement that it will help Iran get nuclear fuel is raising questions"
        article = self.getArticle(url, html)
        self.runArticleAssertions(article=article, expectedStart=content)
        self.printReport()

    def test_aolNews(self):
        html = self.get_html("statichtml/aol1.txt")
        url = "http://www.aolnews.com/nation/article/the-few-the-proud-the-marines-getting-a-makeover/19592478"
        content = "WASHINGTON (Aug. 13) -- Declaring \"the maritime soul of the Marine Corps\" is"
        article = self.getArticle(url, html)
        self.runArticleAssertions(article=article, expectedStart=content)
        self.printReport()

    def test_huffingtonPost2(self):
        html = self.get_html("statichtml/huffpo2.txt")
        url = "http://www.huffingtonpost.com/2011/10/06/alabama-workers-immigration-law_n_997793.html"
        content = "MONTGOMERY, Ala. -- Alabama's strict new immigration law may be backfiring."
        article = self.getArticle(url, html)
        self.runArticleAssertions(article=article, expectedStart=content)
        self.printReport()

    def test_testHuffingtonPost(self):
        html = self.get_html("statichtml/huffpo1.txt")
        url = "http://www.huffingtonpost.com/2010/08/13/federal-reserve-pursuing_n_681540.html"
        title = "Federal Reserve's Low Rate Policy Is A 'Dangerous Gamble,' Says Top Central Bank Official"
        content = "A top regional Federal Reserve official sharply criticized Friday"
        keywords = "federal, reserve's, low, rate, policy, is, a, 'dangerous, gamble,', says, top, central, bank, official, business"
        description = "A top regional Federal Reserve official sharply criticized Friday the Fed's ongoing policy of keeping interest rates near zero -- and at record lows -- as a \"dangerous gamble.\""
        article = self.getArticle(url, html)
        self.runArticleAssertions(article=article, expectedTitle=title, expectedStart=content, expectedDescription=description)
        self.printReport()

    def test_espn(self):
        html = self.get_html("statichtml/espn1.txt")
        url = "http://sports.espn.go.com/espn/commentary/news/story?id=5461430"
        content = "If you believe what college football coaches have said about sports"
        article = self.getArticle(url, html)
        self.runArticleAssertions(article=article, expectedStart=content)
        self.printReport()

    def test_engadget(self):
        html = self.get_html("statichtml/engadget1.txt")
        url = "http://www.engadget.com/2010/08/18/verizon-fios-set-top-boxes-getting-a-new-hd-guide-external-stor/"
        content = "Streaming and downloading TV content to mobiles is nice"
        article = self.getArticle(url, html)
        self.runArticleAssertions(article=article, expectedStart=content)
        self.printReport()

    def test_msn1(self):
        html = self.get_html("statichtml/msn1.txt")
        url = "http://lifestyle.msn.com/your-life/your-money-today/article.aspx?cp-documentid=31244150"
        expected = self.get_html("statichtml/msn1_result.txt")
        article = self.getArticle(url, html)
        self.runArticleAssertions(article=article, expectedStart=expected)
        self.printReport()

    # #########################################
    # # FAIL CHECK
    # # UNICODE
    # def test_guardian1(self):
    #     html = self.get_html("statichtml/guardian1.txt")
    #     url = "http://www.guardian.co.uk/film/2011/nov/18/kristen-wiig-bridesmaids"
    #     expected = self.get_html("statichtml/guardian1_result.txt")
    #     article = self.getArticle(url, html)
    #     self.runArticleAssertions(article=article, expectedStart=expected)
    #     self.printReport()

    def test_time(self):
        html = self.get_html("statichtml/time1.txt")
        url = "http://www.time.com/time/health/article/0,8599,2011497,00.html"
        title = "Invisible Oil from BP Spill May Threaten Gulf Aquatic Life"
        content = "This month, the federal government released"
        article = self.getArticle(url, html)
        self.runArticleAssertions(article=article, expectedTitle=title, expectedStart=content)
        self.printReport()

    def test_time2(self):
        html = self.get_html("statichtml/time2.txt")
        url = "http://newsfeed.time.com/2011/08/24/washington-monument-closes-to-repair-earthquake-induced-crack/"
        content = "Despite what the jeers of jaded Californians might suggest"
        article = self.getArticle(url, html)
        self.runArticleAssertions(article=article, expectedStart=content)
        self.printReport()

    def test_cnet(self):
        html = self.get_html("statichtml/cnet1.txt")
        url = "http://news.cnet.com/8301-30686_3-20014053-266.html?tag=topStories1"
        content = "NEW YORK--Verizon Communications is prepping a new"
        article = self.getArticle(url, html)
        self.runArticleAssertions(article=article, expectedStart=content)
        self.printReport()

    def test_yahoo(self):
        html = self.get_html("statichtml/yahoo1.txt")
        url = "http://news.yahoo.com/apple-says-steve-jobs-resigning-ceo-224628633.html"
        content = u"SAN FRANCISCO (AP) — Steve Jobs, the mind behind the iPhone"
        article = self.getArticle(url, html)
        self.runArticleAssertions(article=article, expectedStart=content)
        self.printReport()

    def test_politico(self):
        html = self.get_html("statichtml/politico1.txt")
        url = "http://www.politico.com/news/stories/1010/43352.html"
        content = "If the newest Census Bureau estimates stay close to form"
        article = self.getArticle(url, html)
        self.runArticleAssertions(article=article, expectedStart=content)
        self.printReport()

    def test_businessinsider1(self):
        html = self.get_html("statichtml/businessinsider1.txt")
        url = "http://articles.businessinsider.com/2011-09-21/markets/30183619_1_parliament-vote-greece-civil-servants"
        content = "As everyone in the world was transfixed on the Fed"
        article = self.getArticle(url, html)
        self.runArticleAssertions(article=article, expectedStart=content)
        self.printReport()

    def test_businessinsider2(self):
        html = self.get_html("statichtml/businessinsider2.txt")
        url = "http://www.businessinsider.com/goldman-on-the-fed-announcement-2011-9"
        content = "From Goldman on the FOMC operation twist announcement"
        article = self.getArticle(url, html)
        self.runArticleAssertions(article=article, expectedStart=content)
        self.printReport()

    #########################################
    # FAIL
    # TEXT APPEND
    def test_cnbc1(self):
        html = self.get_html("statichtml/cnbc1.txt")
        url = "http://www.cnbc.com/id/44613978"
        content = "Some traders found Wednesday's Fed statement to be a bit gloomier than expected."
        article = self.getArticle(url, html)
        self.runArticleAssertions(article=article, expectedStart=content)
        self.printReport()

    def test_marketplace(self):
        html = self.get_html("statichtml/marketplace.txt")
        url = "http://www.marketplace.org/shows/marketplace-tech-report/marketplace-tech-friday-april-19-2013"
        content = "Gun control advocates are looking for new options, including some tech strategies. On Wednesday"
        article = self.getArticle(url, html)
        self.runArticleAssertions(article=article, expectedStart=content)
        self.printReport()

    def test_issue24(self):
        html = self.get_html("statichtml/issue_24.txt")
        url = "http://danielspicar.github.com/goose-bug.html"
        expected = self.get_html("statichtml/issue_24_result.txt")
        article = self.getArticle(url, html)
        self.runArticleAssertions(article=article, expectedStart=expected)
        self.printReport()

    def test_issue25(self):
        html = self.get_html("statichtml/issue_25.txt")
        url = "http://www.accountancyage.com/aa/analysis/2111729/institutes-ifrs-bang"
        expected = "UK INSTITUTES have thrown their weight behind rapid adoption of international financial reporting standards in the US."
        article = self.getArticle(url, html)
        self.runArticleAssertions(article=article, expectedStart=expected)
        self.printReport()

    #########################################
    # FAIL
    def test_issue28(self):
        html = self.get_html("statichtml/issue_28.txt")
        url = "http://www.telegraph.co.uk/foodanddrink/foodanddrinknews/8808120/Worlds-hottest-chilli-contest-leaves-two-in-hospital.html"
        expected = "Emergency services were called to Kismot Restaurant's curry-eating challenge,"
        article = self.getArticle(url, html)
        self.runArticleAssertions(article=article, expectedStart=expected)
        self.printReport()

    def test_issue32(self):
        html = self.get_html("statichtml/issue_32.txt")
        url = "http://www.tulsaworld.com/site/articlepath.aspx?articleid=20111118_61_A16_Opposi344152&rss_lnk=7"
        expected = "Opposition to a proposal to remove certain personal data"
        article = self.getArticle(url, html)
        self.runArticleAssertions(article=article, expectedStart=expected)
        self.printReport()

    def test_issue4(self):
        html = self.get_html("statichtml/issue_4.txt")
        url = "http://www.slate.fr/story/64063/tapie-mougeotte-la-provence"
        expected = u"Exercice: apr\xe8s avoir attentivement lu cette br\xe8ve parue dans L'Express, vous expliquerez en quoi elle r\xe9sume une certaine id\xe9e de la France.\n\n\xabBernar"
        article = self.getArticle(url, html)
        self.runArticleAssertions(article=article, expectedStart=expected)
        self.printReport()


class TestExtractWithUrl(TestExtractionBase):
    def test_get_canonical_url(self):
        html = self.get_html("statichtml/marketplace.txt")
        url = "http://www.marketplace.org/shows/marketplace-tech-report/marketplace-tech-friday-april-19-2013"
        canonical_url = "http://www.marketplace.org/shows/marketplace-tech-report/marketplace-tech-friday-april-19-2013"
        content = "Gun control advocates are looking for new options, including some tech strategies. On Wednesday"
        article = self.getArticle(url, html)
        self.runArticleAssertions(article=article, expectedStart=content, expectedCanonicalLink=canonical_url)
        self.printReport()


class TestExtractChinese(TestExtractionBase):

    def getArticle(self, url, raw_html, language=None):
        g = Goose({'stopwords_class': StopWordsChinese})
        article = g.extract(url=url, raw_html=raw_html)
        return article

    def test_bbc_chinese(self):
        html = self.get_html("statichtml/bbc_hongkong_politics.html")
        url = "http://www.bbc.co.uk/zhongwen/simp/chinese_news/2012/12/121210_hongkong_politics.shtml"
        expected = u"""香港行政长官梁振英在各方压力下就其大宅的违章建筑（僭建）问题到立法会接受质询，并向香港民众道歉。

梁振英在星期二（12月10日）的答问大会开始之际在其演说中道歉，但强调他在违章建筑问题上没有隐瞒的意图和动机。

一些亲北京阵营议员欢迎梁振英道歉，且认为应能获得香港民众接受，但这些议员也质问梁振英有"""
        article = self.getArticle(url, html)
        self.runArticleAssertions(article=article, expectedStart=expected)
        self.printReport()


class TestExtractArabic(TestExtractionBase):

    def getArticle(self, url, raw_html, language=None):
        g = Goose({'stopwords_class': StopWordsArabic})
        article = g.extract(url=url, raw_html=raw_html)
        return article

    def test_cnn_arabic(self):
        html = self.get_html("statichtml/cnn_arabic.html")
        url = "http://arabic.cnn.com/2013/middle_east/8/3/syria.clashes/index.html"
        expected = u"""دمشق، سوريا (CNN) -- أكدت جهات سورية معارضة أن فصائل مسلحة معارضة لنظام الرئيس بشار الأسد وعلى صلة بـ"الجيش الحر" تمكنت من السيطرة على مستودعات للأسل"""
        article = self.getArticle(url, html)
        self.runArticleAssertions(article=article, expectedStart=expected)
        self.printReport()


class TestExtractionsRaw(TestExtractions):

    def setUp(self):
        self.articleReport = ["=======================::. ARTICLE REPORT .::======================\n"]

    def getArticle(self, url, raw_html, language=None):
        config = Configuration()
        if language:
            config.target_language = language
            config.use_meta_language = False
        config.enable_image_fetching = False
        g = Goose(config=config)
        article = g.extract(raw_html=raw_html)
        return article
