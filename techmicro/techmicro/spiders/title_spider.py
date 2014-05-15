from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.spider import Spider
from scrapy import log
from techmicro.items import techmicroItem
import ConfigParser

class technetSpider(Spider):
    name = "technet"
    
    def __init__(self, keyword = None, *args, **kwargs):
        super(technetSpider, self).__init__(*args, **kwargs)
        #self.search = techmicroItem(keyword = keyword)
        #self.keyword = keyword
        self.ConfigSettings()
        try:
            self.keyword = keyword.lower()
            self.file_keyword = "pages with %s" %self.keyword
            open(self.file_keyword, 'w').close()
        except AttributeError:
            self.log('No keyword entered to search for in webpages!')
        self.totalCount = 0
        self.number = 0

    #start_urls = ["https://technet.microsoft.com/en-us/library/security/dn631937.aspx"]

    def ConfigSettings(self):
        self.start_urls = []
        config = ConfigParser.ConfigParser()
        config.read("/home/behzad/scrapyproject/techmicro/spider_settings.ini")
        self.start_urls.append(config.get('website', 'start_urls'))
        self.keyword = config.get('search', 'keywords')
        self.title_xpath = config.get('xpaths', 'title')
        self.date_xpath = config.get('xpaths', 'date')
        nodes = [x for x in config.options('xpaths') if x.startswith('node_')]
        self.node_xpath = []
        for node in nodes:
            self.node_xpath.append(config.get('xpaths', node)) 
       

    def parse(self, response):
        self.sel = Selector(response)
        count = self.getCount(response)
        if count:
            self.number += 1
            f = open(self.file_keyword, 'a')
            f.write("%d)%s\n" %(self.number, self.getTitle()) + response.url + "\n" + "count = %d, %s" %(count, self.getDate()) + "\n\n")
            f.close() 
        for url in self.sel.xpath('//div[re:test(@class, "toclevel2")]//a/@href').extract():
            yield Request(url, callback = self.parse) 
    
    def getCount(self, response):
        count = 0
        if not response.url.count("technet.microsoft.com/en-us/library/security/ms"):
            return count
        for node in self.node_xpath:
            for p in self.sel.xpath(node).extract():
                lowerp = p.lower()
                count += lowerp.count(self.keyword)
        self.totalCount += count 
        return count   

    def getDate(self): 
        self.search['date'] = self.sel.xpath(self.date_xpath).extract()
        date = self.search['date']
        if date:
            return date[0]
        return ''

    def getTitle(self):
        self.search['title'] = self.sel.xpath(self.title_xpath).extract()
        title = self.search['title']
        if title:
            return title[0]
        return ''
